# TryHackMe: Day-O: Memory Forensics & Malware Analysis Writeup

**Difficulty:** Medium | **Category:** Memory Forensics, Malware Analysis
**Evidence:** `memory.mem` (4.1 GB Windows 10 build 19041 x64 capture) plus offline ISF symbols
**Tooling:** Volatility 3 (2.28.2), objdump, Speakeasy, Python (base64, struct, PyCryptodome)

---

## 1. Executive Summary

A user (`s.reyes`) ran a "document review" package from her Downloads folder. The package's executable, `ReviewClient.exe`, loaded a shellcode payload that had been **appended to the end of a PNG file** (`review-cover.png`) and placed it in a private RWX memory region. The shellcode rebuilt a PowerShell command on the stack, resolved `WinExec` by walking the PEB and kernel32's export table, and launched a Base64-encoded PowerShell stage. That stage used **AES-256-CBC** to decrypt a second file, `review-cache.dat`, into a ZIP archive containing `release/approval.txt` and `release/contacts.csv`.

Every artifact was recovered from memory alone, with no disk image.

### Answers

**Q1: Which executable contains the suspicious payload?**

```
ReviewClient.exe
```

**Q2: What is the starting virtual address of its private executable memory region?**

```
0x8e0000
```

**Q3: Which file associated with the process also contains the same payload?**

```
review-cover.png
```

**Q4: Which MITRE ATT&CK sub-technique best describes how the payload is stored in the recovered PNG file?**

```
T1027.009
```

(Obfuscated Files or Information: Embedded Payloads)

**Q5: Which Windows API does the payload call to launch its next stage?**

```
WinExec
```

**Q6: What encryption key does the decoded stage use to decrypt the document cache?**

```
7d714a7267e88abc1afd223830cb74d7c840f677ff165fbec9c134595f06faa8
```

**Q7: What is the flag?**

```
THM{2b3cc75adab999202e1879af542b2c11}
```

---

## 2. Methodology

1. Validate the image and symbols.
2. Enumerate processes and look for anomalies in parentage, path and architecture.
3. Hunt for injected or unbacked executable memory.
4. Correlate the process's open files with the memory finding.
5. Carve and characterise the payload.
6. Emulate the shellcode to get its behaviour safely.
7. Decode the next stage and recover the cryptographic material.
8. Decrypt the staged data.

---

## 3. Analysis

### 3.1 Environment validation

```bash
cd ~/Desktop/artifacts
source tools/venv/bin/activate
vol -s symbols -f memory.mem windows.info
```

Volatility resolved the kernel via the supplied `ntkrnlmp.pdb` ISF (`-s symbols` points it at the offline symbol directory). The image is a 64-bit Windows 10 (build 19041) capture with two CPUs.

### 3.2 Process triage (Q1)

```bash
vol -s symbols -f memory.mem windows.pstree > /tmp/pstree.txt
vol -s symbols -f memory.mem windows.cmdline > /tmp/cmdline.txt
```

Almost everything was normal Windows: `smss`, `csrss`, `wininit`, `services`, `lsass`, a large `svchost` tree and `explorer.exe` with its usual children. One entry stood out:

```
6260  6164  ReviewClient.e  Wow64=True  03:54:18
      C:\Users\s.reyes\Downloads\DocumentReview\ReviewClient.exe
6280  6164  notepad.exe                 03:54:18
```

Indicators:

- **Orphaned parent.** PPID 6164 is not in the process list, so the parent exited after launching the child. `notepad.exe` shares the same missing parent and start time, which suggests a launcher or a distraction process.
- **Execution from a user Downloads path**, with no signed or installed location.
- **Wow64 = True.** A 32-bit process on 64-bit Windows. This matters later, because the payload is x86 shellcode that uses the 32-bit PEB layout (`fs:[0x30]`).
- The process name matches the incident brief's "document review" story.

**Q1:** (Volatility truncates the name to `ReviewClient.e`)

```
ReviewClient.exe
```

### 3.3 Injected memory (Q2)

```bash
vol -s symbols -f memory.mem windows.malfind --pid 6260
```

```
PID   Process         Start VPN  End VPN   Tag   Protection             PrivateMemory
6260  ReviewClient.e  0x8e0000   0x8e0fff  VadS  PAGE_EXECUTE_READWRITE 1
```

`malfind` reports private VAD regions that are executable, writable and not file-backed. A single 4 KB region was returned. The start of the dump was:

```
55 89 e5 83 ec 18 31 f6 56 6a 63 66 68 78 65 68 57 69 6e 45 ...
```

This is a standard x86 prologue (`push ebp; mov ebp, esp`) followed by pushes of `0x63`, `0x6578` and `0x456e6957`. In little-endian ASCII these spell `WinExec`, a stack-built string used to avoid a literal in the binary. The `mov ebx, fs:[esi+0x30]` instruction begins a PEB walk, a classic position-independent technique for locating kernel32 without imports.

**Q2:**

```
0x8e0000
```

### 3.4 Correlating files with the process (Q3)

```bash
vol -s symbols -f memory.mem windows.handles --pid 6260 | grep -i "File" | grep -iv "\\\\Windows\\\\"
```

Two sibling files in `DocumentReview\` were held open with read access (`0x120089`):

```
review-cache.dat
review-cover.png
```

Both were extracted using their `FileObject` addresses:

```bash
vol -s symbols -f memory.mem -o /tmp/out windows.dumpfiles --virtaddr 0xbd8fdbcb5a10   # PNG
vol -s symbols -f memory.mem -o /tmp/out windows.dumpfiles --virtaddr 0xbd8fdbcb3c60   # cache
```

Practical note: `dumpfiles` emits `DataSectionObject` (`.dat`, the file contents as cached) and `SharedCacheMap` (`.vacb`, 256 KB cache views padded with unrelated data) variants. The `DataSectionObject` copy is the right one for analysis. The globbing `cp file.*...*` failed because several files matched, so each source was named explicitly.

`file` identified the PNG as valid (`PNG image data, 1000 x 620, 8-bit/color RGB`) and the cache as opaque `data`.

### 3.5 PNG structure and carving the payload (Q3 confirmed, Q4)

A short parser walked the PNG chunks:

```
0x8    IHDR   13
0x21   IDAT   28772
0x7091 IEND   0
trailing bytes after IEND: 3939
5589e583ec1831f6...
```

The image is structurally normal: a single `IDAT` chunk and a terminating `IEND`. Image viewers stop at `IEND`, so the file renders correctly. **3,939 bytes follow `IEND`**, and they begin with exactly the bytes seen in the `malfind` region. This confirms **Q3: `review-cover.png`**.

```python
d = open('/tmp/cover.png','rb').read()
i = d.rfind(b'IEND')
open('/tmp/payload.bin','wb').write(d[i+8:])   # skip 'IEND' + 4-byte CRC
```

**MITRE mapping (Q4).** The payload is not hidden in the pixel data. It is appended as a contiguous blob in a file the host process reads. That distinguishes two candidate sub-techniques:

- **T1027.003 Steganography** conceals data inside the content of the carrier (for example, LSB encoding in pixels). It does not fit, because the image data is untouched and the payload sits in plaintext after `IEND`.
- **T1027.009 Embedded Payloads** covers payloads included inside another file. This fits the evidence.

**Q4:**

```
T1027.009
```

### 3.6 Shellcode analysis (Q5)

Static disassembly:

```bash
objdump -D -b binary -m i386 -M intel /tmp/payload.bin > /tmp/payload.asm
grep -n "call" /tmp/payload.asm
```

Findings:

- **Offsets `0x00` to `0x86`:** PEB walk (`fs:[0x30]` → `PEB_LDR_DATA` → `InMemoryOrderModuleList`) to reach kernel32's base. It then parses the PE export directory (name, ordinal and address tables) and compares the pushed `WinExec` string using `repz cmpsb` to resolve the function pointer.
- **Offsets `0x8d` onwards:** a long run of `push imm32` instructions that assemble a string on the stack. The pushed values (for example `0x25256266`) are not readable ASCII, so the string is **encoded**. `strings` shows only noise (`hfb%%hvfpvhf...`) apart from the `WinE` fragment.
- **Offset `0x53b`:** a single `call eax`, which is the resolved `WinExec`. It is the only `call` in the blob.

Rather than hand-decoding the stack string, the shellcode was emulated with Speakeasy:

```bash
speakeasy -t /tmp/payload.bin -r -a x86 -o /tmp/report.json
```

Output:

```
* exec: shellcode
kernel32.WinExec("powershell.exe -NoProfile -EncodedCommand JABrAD0AWwBD...", 0x5) -> 0x20
```

`WinExec` is called with `SW_SHOW` (`0x5`) and a PowerShell command line. A return value above 31 indicates success.

**Q5:**

```
WinExec
```

### 3.7 Decoding the second stage (Q6)

`-EncodedCommand` expects Base64 of **UTF-16LE** text:

```python
import base64, re
txt = open('/tmp/report.json').read()
b = re.search(r'-EncodedCommand ([A-Za-z0-9+/=]+)', txt).group(1)
print(base64.b64decode(b).decode('utf-16le'))
```

Decoded stage 2:

```powershell
$k=[Convert]::FromBase64String('fXFKcmfoirwa/SI4MMt018hA9nf/Fl++ycE0WV8G+qg=')
$b=[IO.File]::ReadAllBytes('review-cache.dat')
$a=[Security.Cryptography.Aes]::Create()
$a.Key=$k
$a.IV=$b[0..15]
$a.Mode='CBC'
$a.Padding='PKCS7'
$d=$a.CreateDecryptor().TransformFinalBlock($b,16,$b.Length-16)
[IO.File]::WriteAllBytes('review-cache.zip',$d)
```

Cryptographic parameters:

| Parameter | Value |
|-----------|-------|
| Algorithm | AES-256 (32-byte key) |
| Mode / padding | CBC / PKCS7 |
| IV | First 16 bytes of `review-cache.dat` |
| Ciphertext | Bytes 16 to end of file |
| Output | `review-cache.zip` |

The Base64 key decodes to 32 bytes. The room requires the key as 64 hex characters (the Base64 text was rejected):

```bash
python3 -c "import base64;print(base64.b64decode('fXFKcmfoirwa/SI4MMt018hA9nf/Fl++ycE0WV8G+qg=').hex())"
```

**Q6:**

```
7d714a7267e88abc1afd223830cb74d7c840f677ff165fbec9c134595f06faa8
```

### 3.8 Recovering the data (Q7)

The dumped `review-cache.dat` was 4096 bytes. Decrypting with the recovered key and IV produced output beginning with `PK\x03\x04`, which validates the key, IV and mode. The padded 256 KB `.vacb` copies decrypted identically once trailing zeros were trimmed, because the ciphertext length must be a multiple of 16.

```python
from Crypto.Cipher import AES
import base64
key = base64.b64decode('fXFKcmfoirwa/SI4MMt018hA9nf/Fl++ycE0WV8G+qg=')
b = open('/tmp/cache.dat','rb').read()
n = len(b.rstrip(b'\x00'))
ct = b[16:n]; ct = ct[:len(ct)//16*16]
open('/tmp/review-cache.zip','wb').write(AES.new(key, AES.MODE_CBC, b[:16]).decrypt(ct))
```

```bash
unzip -o /tmp/review-cache.zip -d /tmp/cache_out
#  release/approval.txt
#  release/contacts.csv
```

The flag was recovered from the extracted contents:

**Q7:**

```
THM{2b3cc75adab999202e1879af542b2c11}
```

---

## 4. Attack Chain

```
Phishing / social engineering (review package in Downloads)
  → ReviewClient.exe executes (32-bit, Wow64)
  → Reads review-cover.png and extracts the blob after IEND
  → Allocates RWX private memory at 0x8e0000 and runs shellcode
  → PEB walk, resolves kernel32!WinExec
  → powershell.exe -NoProfile -EncodedCommand <UTF-16LE Base64>
  → AES-256-CBC decrypt of review-cache.dat
  → review-cache.zip (release/approval.txt, release/contacts.csv)
```

## 5. MITRE ATT&CK Mapping

| Tactic | Technique | Evidence |
|--------|-----------|----------|
| Execution | T1204.002 User Execution: Malicious File | `ReviewClient.exe` run from Downloads |
| Execution | T1059.001 PowerShell | `-EncodedCommand` stage |
| Execution | T1106 Native API | `WinExec` via manual export resolution |
| Defense Evasion | T1027.009 Embedded Payloads | Shellcode appended after PNG `IEND` |
| Defense Evasion | T1027 Obfuscated Files or Information | Encoded stack string, Base64 UTF-16LE command |
| Defense Evasion / Privilege Escalation | T1055 Process Injection (in-process RWX memory) | `malfind` region at `0x8e0000` |
| Defense Evasion | T1140 Deobfuscate/Decode Files or Information | AES decryption of `review-cache.dat` |

The T1204.002 entry is inferred from the process path and the brief. The memory image alone does not show how the package arrived.

## 6. Indicators of Compromise

| Type | Value |
|------|-------|
| Process | `ReviewClient.exe`, PID 6260, parent PID 6164 (exited) |
| Path | `C:\Users\s.reyes\Downloads\DocumentReview\` |
| Files | `ReviewClient.exe`, `review-cover.png`, `review-cache.dat`, `review-cache.zip` |
| Memory | RWX private VAD `0x8e0000`–`0x8e0fff`, starting `55 89 e5 83 ec 18 31 f6` |
| Command line | `powershell.exe -NoProfile -EncodedCommand JABrAD0AWwBD...` |
| AES-256 key (hex) | `7d714a7267e88abc1afd223830cb74d7c840f677ff165fbec9c134595f06faa8` |
| Detection hint | PNG with data after `IEND`; PowerShell spawned by a non-shell parent |

## 7. Recommendations

**Detection**
- Alert on PowerShell launched with `-EncodedCommand` by a process other than an interactive shell or known management tooling.
- Flag `VirtualAlloc`/`VirtualProtect` calls producing RWX private regions in user applications.
- Scan image files for trailing data after their end markers (`IEND`, JPEG `FFD9`).
- Add a YARA rule for the PEB-walk prologue plus `WinExec` stack-string pattern.

**Prevention**
- Block execution from user-writable paths such as Downloads using AppLocker or WDAC.
- Enable PowerShell Script Block Logging, Module Logging and Constrained Language Mode.
- Apply ASR rules covering obfuscated scripts and executable content from email and downloads.

**Response**
- Isolate the host, preserve memory, and reset `s.reyes`'s credentials.
- Treat the contents of `review-cache.zip` as the data of interest and assess exposure of `contacts.csv`.
- Hunt for the filenames and the key across the estate.

## 8. Lessons Learned

- **Process names prove little.** The key finding came from comparing what was running (`ReviewClient.exe`) with what its memory contained (an unbacked RWX region).
- **Cross-reference artifacts.** The shared 8-byte prologue in both the VAD and the PNG tail tied the memory finding to the on-disk carrier.
- **Emulate before you reverse.** The shellcode's encoded stack string was resolved by Speakeasy in seconds, with no manual decoding.
- **Know your formats.** PowerShell `-EncodedCommand` is UTF-16LE Base64, and the room's answer format wanted the raw key as hex.
- **Pick the right dump.** `DataSectionObject` gives file content, while `SharedCacheMap` is padded, so use trailing-zero trimming if you rely on it.

**Final flag:**

```
THM{2b3cc75adab999202e1879af542b2c11}
```
