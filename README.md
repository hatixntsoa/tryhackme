# ☁️ TryHackMe Room Training Portfolio

A structured, chronological record of every [TryHackMe](https://tryhackme.com) room I have completed: enumeration output, exploit code, decoded artefacts, captured evidence and, progressively, full technical writeups.

The repository covers offensive security, defensive security, digital forensics, malware analysis, security operations and cloud security. Its commit history mirrors the real completion dates of each room.

I know I should've written writeups in a live Jekyll site instead but as I am too excited for each room that I did so far, I didn't have the time neither the will to do so. 

Because you know I have been learning hacking very intensively for as long as I have started, some *completed* rooms are not even covered here *yet* but it's a work in progress anyways. I have exposed my TryHackMe profile dynamic badge in here though : [tryhackme.hatixntsoa.me](https://tryhackme.hatixntsoa.me)

Oh and by the way you can also visit my THM profile here: [tryhackme.com/hatixntsoa](https://tryhackme.com/p/hatixntsoa)

---

## ⚠️ Disclaimer: Credentials, Keys and Flags

Many folders contain material that looks sensitive: SSH private keys, RDP and SSH credentials, password hashes, tokens, cracked passwords and flags.

**None of this is real, and none of it is reusable.**

- **Ephemeral lab machines.** Every TryHackMe room deploys a temporary virtual machine for the session. Credentials, keys, IP addresses, hostnames and tokens are generated or assigned for that session only. They stop working when the machine is terminated, usually within hours.
- **Training environments.** All targets are intentionally vulnerable machines in an isolated, authorised, legal training platform. No real organisation, system or person is affected.
- **Flags are spoilers.** Flag files are kept as a personal progress record. If you plan to do these rooms yourself, avoid the `flags/` folders and the `writeups/` folders.

I am keeping this material on purpose, because it documents the work as it actually happened. If you think you have found a leaked secret here, you have found an expired lab credential.

---

## ⚖️ Legal and Ethical Notice

Everything in this repository was performed against systems I was explicitly authorised to test, inside TryHackMe's controlled lab environment. The exploit code, scripts and techniques are for **education and authorised security testing only**.

Do not use anything in this repository against systems you do not own or do not have written permission to test. Unauthorised access to computer systems is illegal in most jurisdictions. The author accepts no liability for misuse.

---

## 📁 Repository Structure

Rooms are grouped by discipline:

| Category | Focus |
|---|---|
| `red.team/` | CTF-style machines, web exploitation, privilege escalation, Active Directory, cryptography challenges, OPSEC |
| `penetration.testing/` | Boxes and rooms following a full pentest workflow, plus reporting |
| `blue.team/` | Detection engineering, SOC operations, SIEM, network detection, threat hunting |
| `incident.response/` | Digital forensics, memory and disk analysis, Windows, Linux and macOS investigations, mobile acquisition |
| `malware.analysis/` | Static and dynamic analysis, reverse engineering, macro and shellcode analysis |
| `security.operations/` | DevSecOps, vulnerability management, threat intelligence, scripting and tooling |
| `cloud/` | Cloud and infrastructure-as-code security |
| `events/` | Advent of Cyber, side quests, CTF events and other time-limited challenges |

### Anatomy of a Room Folder

Each room follows the same layout, using only the folders it needs:

```text
room.name/
├── access/         # SSH, FTP, RDP, netcat and reverse shell commands
├── credentials/    # Credentials, keys and room links (ephemeral, see disclaimer)
├── decryption/     # Decoding, cracking, steganography and reverse engineering work
├── enumeration/    # nmap, gobuster, feroxbuster, wpscan, enum4linux and similar output
├── exploit/        # Exploit scripts, payloads and privilege escalation material
├── flags/          # Captured flags (spoilers)
├── screenshots/    # Evidence captured during the room
└── writeups/       # Technical writeup (rolled out progressively)
```

---

## 🔬 Methodology

Each room is approached with a consistent workflow:

1. **Reconnaissance and enumeration:** service discovery, directory and subdomain brute-forcing, technology fingerprinting.
2. **Vulnerability identification:** version analysis, CVE research, misconfiguration review, source code review.
3. **Exploitation:** initial access through web, network or credential-based attack paths.
4. **Privilege escalation:** SUID and sudo abuse, cron jobs, kernel exploits, token abuse, Active Directory attacks.
5. **Post-exploitation:** credential harvesting, lateral movement, persistence.
6. **Documentation:** commands, evidence and findings saved alongside each room.

For defensive rooms, the same discipline applies to **detection, triage, investigation and reporting**.

---

## 🧰 Tooling

| Area | Tools |
|---|---|
| Recon and scanning | nmap, rustscan, gobuster, feroxbuster, ffuf, nikto, amass, Sublist3r |
| Web | Burp Suite, sqlmap, wpscan, BeEF, curl |
| Passwords and crypto | John the Ripper, Hashcat, Hydra, CyberChef, stegseek, steghide |
| Active Directory | Impacket, BloodHound, Kerbrute, Evil-WinRM, CrackMapExec, Mimikatz |
| Exploitation | Metasploit, msfvenom, pwntools, custom Python scripts |
| Forensics and DFIR | Volatility, Autopsy, Registry Explorer, exiftool, KAPE-style triage |
| Malware analysis | Ghidra, oledump, olevba, ViperMonkey, FLOSS, YARA, strings |
| Blue team | Splunk, Elastic/Kibana, Wazuh-style SIEM workflows, Wireshark, Sigma and YARA rules |
| Vulnerability management | OpenVAS, Snyk |

---

## 🗺️ Skills Coverage

The rooms map to the main phases of the MITRE ATT&CK framework and the main defensive disciplines:

- **Offence:** initial access, execution, persistence, privilege escalation, credential access, lateral movement, defence evasion
- **Defence:** log analysis, alert triage, threat hunting, detection engineering, threat intelligence, incident response
- **Forensics:** memory, disk, registry, mobile, network and cloud artefacts
- **Engineering:** secure SDLC, DevSecOps, infrastructure-as-code security, scripting and automation

---

## 📝 Writeups

Writeups are being added room by room, built from the screenshots and command history already stored in each folder. Completed writeups live in the room's `writeups/` directory. Rooms without a `writeups/` folder have raw evidence only.

---

## 🕒 Commit History

Each commit corresponds to one completed room and is dated to the day the room was done, so the history works as a timeline of my learning. The convention is:

```text
feat: <Room Name> completed
docs: <Room Name> writeup added
```

---

## 📄 License

Released under the terms in [LICENSE.md](LICENSE.md).

---

*Remember, always hack **legally** and **ethically**.*
