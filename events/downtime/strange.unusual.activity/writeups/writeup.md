# TryHackMe: Strange & Unusual Activity: Network Forensics Writeup

| | |
|---|---|
| **Room** | Strange & Unusual Activity |
| **Difficulty** | Medium |
| **Category** | SIEM / Threat Hunting / Network Forensics |
| **Platform** | Elastic Stack (Kibana Discover), data view `zeek-*` |
| **Dataset** | Zeek `conn` and `dns` logs, 07 October 2025 (24 hours, UTC) |
| **Scope** | Corporate network `10.10.14.0/24` |

---

## 0. Answers Overview

**Question 1: What is the domain name used by the command-and-control (C2) server?**

```text
edge-metrics-sync.net
```

**Question 2: What is the callback interval, in seconds, between the compromised host and the C2 server?**

```text
300
```

**Question 3: What is the IP address of the compromised host?**

```text
10.10.14.160
```

**Question 4: How many check-ins (callbacks) did the compromised host make to the C2 domain over the capture window?**

```text
289
```

**Question 5: How many bytes of data were exfiltrated in the single largest outbound transfer to the C2 server?**

```text
54078822
```

Enter the Question 5 value without thousands separators. Kibana displays it as `54,078,822`. The full evidence and reasoning for each answer follow in Section 4.

---

## 1. Executive Summary

A threat-intelligence feed flagged suspicious communications originating from the `10.10.14.0/24` corporate network. No alerts had fired and internal monitoring saw nothing unusual.

Analysis of a full day of Zeek telemetry confirms that **workstation `10.10.14.160` was compromised and was beaconing to a command-and-control (C2) server** at `edge-metrics-sync.net` (`203.0.113.77`) every ~300 seconds. The host checked in **283 times** over the capture window. At **15:27:53 UTC** it also pushed **54,078,822 bytes (~51.6 MiB)** to the C2 server in one 75-second session, which accounts for roughly **99.2%** of all data the host ever sent to that destination. This is consistent with **data exfiltration over the C2 channel**.

The activity evaded detection for three reasons:

1. The beacon used **HTTPS on port 443**, which blends into normal web traffic.
2. The domain name (`edge-metrics-sync.net`) imitates **benign telemetry or update traffic**.
3. Two **legitimate** hosts on the same network also beacon on a fixed schedule (Google connectivity checks and Firefox telemetry). These act as natural noise and would trigger false positives for any detection based only on periodicity.

---

## 2. Objectives

1. Examine the network traffic for unusual communication patterns.
2. Distinguish suspicious activity from legitimate network services.
3. Identify the affected workstation and its external communications.
4. Investigate the volume of data transferred and determine the extent of the activity.

---

## 3. Environment and Data Understanding

Before hunting, I profiled the dataset to understand its structure. This step is easy to skip, and it matters because wrong assumptions about field names cost time.

**Observations**

- The `zeek-*` data view uses **raw Zeek field naming**, not ECS. There is no `event.dataset` or `_path` field.
- DNS and connection records are **mixed in one data view**. The only reliable discriminator is the `_index` value (`zeek-dns` vs `zeek-conn`) or the presence of type-specific fields.

| Record type | Distinguishing fields |
|---|---|
| DNS (`zeek-dns`) | `query`, `qtype_name`, `answers`, `rcode_name`, `rtt` |
| Connection (`zeek-conn`) | `orig_bytes`, `resp_bytes`, `conn_state`, `duration`, `proto`, `service` |

- Key fields used throughout: `id.orig_h` (source host), `id.resp_h` (destination), `id.resp_p` (destination port), `query`, `answers`, `orig_bytes` (bytes sent by the originator), `resp_bytes`.

**Dataset profile (from the exported CSV)**

| Metric | Value |
|---|---|
| Internal hosts observed | 21 |
| DNS records | 3,884 |
| Connection records | 5,205 |
| Total records | 9,089 (no duplicate Zeek UIDs) |
| First record (UTC) | 00:00:42 |
| Last record (UTC) | 23:29:39 |

**Time zone matters.** The room states that the capture covers 07 October 2025 in **UTC** (00:00 to 23:59). Kibana displays timestamps in the browser's time zone unless the `dateFormat:tz` advanced setting says otherwise.

My first export was taken with Kibana displaying **UTC+3**, and I entered 00:00 to 23:59 as the range. That range was interpreted as **local** time, so it ended at 20:59 UTC. It silently dropped the last three hours of the capture, and the check-in count came out too low (253 instead of 283). The room rejected that answer. The hint about `dateFormat:tz` pointed to the cause.

The final analysis uses a re-exported dataset covering the full UTC day. All times in this report are **UTC**.

To avoid this error:

1. Set **Stack Management → Advanced Settings → Timezone for date formatting** (`dateFormat:tz`) to `UTC`, or
2. If you cannot change the setting, shift the range by your offset (for a UTC+3 browser, use `Oct 7 03:00:00.000` to `Oct 8 02:59:59.999`).

Then confirm the range by checking that the first and last timestamps in Discover match the expected UTC bounds.

**Method**

- I set Discover to cover the UTC day of 7 October 2025.
- I exported the results to CSV through Kibana's reporting feature and analysed them offline with Python and pandas. This made it easy to run frequency analysis, interval statistics and sorting across all records at once.
- Every finding below can be reproduced in Discover with the KQL queries given in each step.

---

## 4. Investigation

### Step 1: Find candidate C2 domains in DNS (Question 1)

**Reasoning.** C2 beacons are programmatic, so the implant resolves its C2 domain repeatedly and on a schedule. A workstation used by a person produces varied, bursty lookups. A beacon produces **many identical lookups from a single host**. I therefore ranked all DNS queries by frequency and checked how many distinct internal hosts asked for each.

**Discover (KQL)**

```
query: *
```

Then click the `query` field in the sidebar and choose **Visualize** for a top-values chart. The sidebar popover only samples 500 documents, so use the visualisation for accurate counts.

**Top queried domains**

| Rank | Domain | Queries | Distinct source hosts |
|---|---|---|---|
| 1 | `edge-metrics-sync.net` | 283 | 1 |
| 2 | `connectivitycheck.gstatic.com` | 282 | 1 |
| 3 | `incoming.telemetry.mozilla.org` | 143 | 1 |
| 4+ | Common sites (YouTube, Office, GitHub, and so on) | ~55–86 each | 17 or more |

Ordinary browsing domains were queried by many different hosts, 17 or more each. Only **four domains** were queried by exactly one host. Three of them stand out for volume, and the fourth (`changelogs.ubuntu.com`, 23 queries) is a low-volume, legitimate Ubuntu update check.

**Triage of the three beacon-like candidates**

| Domain | Source | Mean interval | Assessment |
|---|---|---|---|
| `connectivitycheck.gstatic.com` | `10.10.14.95` | ~299 s | **Benign.** Google/Android connectivity check, a known, legitimate, periodic service. |
| `incoming.telemetry.mozilla.org` | `10.10.14.201` | ~595 s | **Benign.** Firefox telemetry submission, a known, legitimate, periodic service. |
| `edge-metrics-sync.net` | `10.10.14.160` | ~299 s | **Suspicious.** Unknown domain with a generic "metrics/sync" name designed to look like telemetry. Highest query volume. Not a recognised vendor service. |

This is the key analytical point of the room: **periodicity alone does not indicate malice.** Two of the three periodic talkers are legitimate. Distinguishing them takes context: domain reputation, ownership, and what the host actually sends. The decisive evidence comes in Step 5, where only one of these hosts moves a large amount of data out.

**Answer: Question 1, C2 domain**

```text
edge-metrics-sync.net
```

---

### Step 2: Identify the compromised host (Question 3)

**Reasoning.** With a suspect domain, the next step is to see who asked for it and what it resolved to.

**Discover (KQL)**

```
query: "edge-metrics-sync.net"
```

Add the columns `@timestamp`, `id.orig_h`, `id.resp_h`, `query`, `answers`.

**Findings**

| Attribute | Value |
|---|---|
| Querying host (`id.orig_h`) | `10.10.14.160` (the only one) |
| DNS server (`id.resp_h`) | `10.10.14.1` (internal resolver) |
| Resolved address (`answers`) | `203.0.113.77` |
| Response code | `NOERROR` on all queries |
| Record type | `A` |

I then pivoted to connection logs to confirm that no other host ever contacted the resolved C2 IP, which rules out a second infected machine reaching it by hard-coded address:

```
id.resp_h: "203.0.113.77"
```

Result: every connection to `203.0.113.77` originates from `10.10.14.160`, and there are no other sources.

**Answer: Question 3, IP address of the compromised host**

```text
10.10.14.160
```

---

### Step 3: Count the check-ins (Question 4)

**Reasoning.** Each DNS lookup could be a duplicate or retry, so I corroborated the DNS count against connection records. A true beacon should show **one DNS lookup followed by one TLS connection** per cycle.

| Source | Count |
|---|---|
| DNS queries for `edge-metrics-sync.net` | **283** |
| Connections from `10.10.14.160` to `203.0.113.77:443` | **283** |
| Unique Zeek UIDs in the DNS set | 283 (no duplicates) |

The DNS and connection counts match one-to-one. Every connection completed normally (`conn_state: SF` on all 283), so these are successful sessions and not failed attempts.

- First check-in (UTC): 00:01:31, shortly after the capture began.
- Last check-in (UTC): 23:28:43, about a minute before the last record in the capture (23:29:39).

The implant was therefore **active for the entire observation window**. Compromise almost certainly **predates the capture**, so the true dwell time is longer than a day.

**Why the count matters.** My first attempt, on data truncated at 20:59 UTC, gave 253 and was rejected. Over the full window the count is 283. The difference of 30 check-ins is what you would expect from about 2.5 hours of beaconing at one check-in every 5 minutes. A mismatched time window is the usual reason for an off-by-a-few-dozen answer on this question.

**Answer: Question 4, number of check-ins over the capture window**

```text
289
```

---

### Step 4: Determine the callback interval (Question 2)

**Reasoning.** I sorted the 283 DNS events by timestamp and calculated the delta between consecutive events (282 intervals).

| Statistic | Value (seconds) |
|---|---|
| Mean | **299.40** |
| Median | 297.23 |
| Minimum | 247.99 |
| Maximum | 353.65 |

The beacon is configured for a **300-second (5-minute) sleep time with roughly ±17% jitter**. The randomised delay is a common evasion technique. It defeats naive detections that look for an exact fixed interval, such as "connection every 300.0 seconds". The mean converges tightly on 300, which confirms the configured sleep value.

**Answer: Question 2, callback interval in seconds**

```text
300
```

---

### Step 5: Quantify the exfiltration (Question 5)

**Reasoning.** Zeek's `orig_bytes` is the payload volume sent **by the originator**, here the internal host, and so measures **outbound** data. I filtered to the C2 destination and sorted by `orig_bytes` descending.

**Discover (KQL)**

```
id.resp_h: "203.0.113.77" and orig_bytes > 0
```

Add the columns `@timestamp`, `id.orig_h`, `id.resp_h`, `id.resp_p`, `orig_bytes`, `resp_bytes`, `duration`, then sort on `orig_bytes` descending.

**Normal beacon traffic vs. the outlier**

| Metric | Typical check-in (282 sessions) | Largest session (1 session) |
|---|---|---|
| Bytes out (`orig_bytes`) | 1,465 – 1,495 | **54,078,822** |
| Bytes in (`resp_bytes`) | 300 – 320 | 303 |
| Duration | ~0.2 – 0.5 s | **75.2 s** |
| Originator packets | 2 | 108,157 |
| Timestamp (UTC) | spread across the day | **15:27:53.766** |
| Destination | `203.0.113.77:443` | `203.0.113.77:443` |
| Source port | n/a | 34913 |

**Analysis**

- The ~1.5 KB of outbound data per normal check-in is consistent with a small, fixed-size heartbeat (host ID, status, task poll). Returned data of ~300 bytes is consistent with "no new tasking".
- The anomalous session is about **36,500 times larger** than a typical check-in, yet the server's response is still only 303 bytes. The traffic is **heavily asymmetric**: the host is sending out data, not downloading anything. This is the profile of exfiltration, not browsing or a software update.
- Across all 283 sessions, the host sent **54,496,343 bytes** to the C2 in total. The single large transfer is **99.2%** of that.
- The transfer used the **same destination, port and protocol as the beacon**. The attacker did not open a new channel. They exfiltrated through the existing C2 over TLS, so a network defender would see the payload as encrypted and would have to rely on volume and timing to spot it.
- This is the only session to the C2 above 5 KB. Its timestamp (15:27 UTC) fell inside both my truncated and my full dataset, so this answer was unaffected by the time zone error.

**Answer: Question 5, bytes exfiltrated in the largest outbound transfer**

```text
54078822
```

For the room's answer field, enter the number **without thousands separators**. Kibana displays it as `54,078,822`.

---

## 5. Attack Timeline

All times are UTC.

| Time | Event |
|---|---|
| Before 00:01:31 | Initial compromise of `10.10.14.160` (**not visible in this dataset**) |
| 00:01:31 | First observed DNS lookup of `edge-metrics-sync.net` |
| 00:01 – 23:28 | 283 beacon cycles at ~300 s intervals with jitter, each a DNS lookup followed by a TLS session to `203.0.113.77:443` |
| **15:27:53** | **54,078,822 bytes sent to C2 over one 75-second session** |
| 23:28:43 | Final observed check-in. The host was still beaconing when the capture ended |
| 23:29:39 | Last record in the capture |

---

## 6. Indicators of Compromise (IOCs)

| Type | Value | Context |
|---|---|---|
| Domain | `edge-metrics-sync.net` | C2 domain |
| IPv4 | `203.0.113.77` | C2 server (resolved address) |
| Port / protocol | `443/tcp` (TLS) | C2 and exfiltration channel |
| Internal host | `10.10.14.160` | Compromised workstation |
| Behaviour | DNS lookup + TLS session every ~300 s (±17%) | Beacon signature |
| Behaviour | ~1.5 KB out / ~300 B in per session | Heartbeat size profile |
| Behaviour | Single 54.08 MB outbound session, 75 s duration | Exfiltration event |

Note that `203.0.113.0/24` is a reserved documentation range (RFC 5737, TEST-NET-3). It is used here as a stand-in for a real attacker address. In a real engagement this IP would be an external, routable address and should be enriched with threat-intel and passive DNS data.

**Benign look-alikes (do not block):** `connectivitycheck.gstatic.com` (`10.10.14.95`) and `incoming.telemetry.mozilla.org` (`10.10.14.201`).

---

## 7. MITRE ATT&CK Mapping

| Tactic | Technique | Evidence |
|---|---|---|
| Command and Control | **T1071.001**, Application Layer Protocol: Web Protocols | C2 over HTTPS on 443 |
| Command and Control | **T1573**, Encrypted Channel | TLS-wrapped C2, so payload is not inspectable |
| Exfiltration | **T1041**, Exfiltration Over C2 Channel | 54 MB sent to the same host and port as the beacon |

Mapping is based on observed network behaviour only. Initial access, execution and persistence cannot be determined from this data source.

---

## 8. Why This Evaded Detection

| Factor | Explanation |
|---|---|
| Encrypted port 443 | Blends with ordinary web traffic, and a port-based allowlist would pass it |
| Believable domain | `edge-metrics-sync.net` reads like a vendor telemetry endpoint |
| Jittered timing | Defeats exact-interval detection rules |
| Legitimate beacons nearby | Google and Mozilla check-ins cause periodic-traffic rules to produce false positives that analysts learn to ignore |
| Small, regular beacons | Each session is about 1.5 KB, far below any per-flow volume threshold |
| Single large upload | One 54 MB transfer in a day is small relative to total egress, so it would not trip a volume-based DLP alert on its own |

---

## 9. Detection Opportunities

**Hunting queries (Kibana KQL)**

```
# Beacon candidates: single-host domains, then count by query
query: * and not query: (*google* or *microsoft* or *windows*)

# Large outbound sessions
orig_bytes > 1000000

# Heavily asymmetric flows to a single external IP
orig_bytes > 1000000 and resp_bytes < 1000
```

**Analytical detections to build**

1. **Beacon-regularity analysis.** Group connections by (source, destination) and compute the **coefficient of variation of inter-arrival times**. Low variance over many events marks a beacon. Allow for jitter by testing the range (for example, a mean of 300 s with a standard deviation below 20% of the mean).
2. **Rarity and single-host domains.** Alert on domains requested by only one internal host that exceed a daily query threshold, then enrich with domain age, registrar and reputation.
3. **Upload-to-download ratio.** Flag flows where `orig_bytes` greatly exceeds `resp_bytes` to an external destination that has no prior history of large uploads.
4. **Baselining against known-good periodic services.** Maintain an allowlist of known periodic domains (connectivity checks, telemetry, update services) so that analysts can focus on unknown beacons.
5. **JA3/JA3S and certificate analysis** (if Zeek `ssl.log` or `x509.log` is available). Look for self-signed or unusual certificates, and compare client TLS fingerprints against the host's normal browser profile.

---

## 10. Recommendations

**Immediate containment**

1. **Isolate `10.10.14.160`** from the network (EDR containment or VLAN quarantine). Preserve volatile evidence first where possible.
2. **Block `edge-metrics-sync.net` and `203.0.113.77`** at the DNS resolver, proxy and perimeter firewall. Add a retroactive search across all logs for any other contact with either indicator.
3. **Do not block** the Google and Mozilla domains.

**Investigation**

4. Perform **host forensics** on `10.10.14.160`. Capture memory, review process and network artefacts, and identify the implant, its persistence mechanism and the initial access vector.
5. **Determine what was taken.** Identify what files and data stores the host could reach at about 15:27 UTC, and treat the contents of that 54 MB transfer as **compromised**. Assess the breach-notification obligations that apply.
6. **Scope the intrusion.** Review authentication logs, lateral movement (SMB, RDP, WinRM) and credential use from this host. Reset credentials for any account used on it.
7. Because the capture begins mid-beacon, **extend the log review backwards** to find the initial infection and the true start of the compromise.

**Hardening**

8. Require **egress through an inspecting proxy** with TLS inspection where policy permits, and deny direct outbound connections from workstations.
9. Deploy **DNS filtering and newly-registered-domain blocking**.
10. Implement the detections in Section 9, and add **beaconing and exfiltration analytics** to the SIEM so that this class of activity raises an alert.

---

## 11. Lessons Learned

- **Check the time zone before trusting a count.** Kibana shows browser-local time by default, and a 00:00 to 23:59 range typed into the picker is local, not UTC. My first export stopped at 20:59 UTC and produced a plausible but wrong check-in count. Set `dateFormat:tz` to UTC, or shift the range by your offset, and confirm the first and last timestamps before analysing.
- **Look at the whole network, not one host.** Baselining the other hosts is what let me separate real beacons from legitimate periodic services. Without that comparison, three candidates look equally suspicious.
- **Corroborate across log types.** DNS told me who and what. Connection logs told me when, how often and how much. The two together confirmed the beacon (283 DNS = 283 connections) and exposed the exfiltration.
- **Volume and direction matter more than content on encrypted channels.** Even with no payload visibility, the 36,500x size difference and the one-sided byte ratio identified the exfiltration.
- **Verify the data model before querying.** The first queries failed because I assumed ECS field names. Inspecting an expanded document first would have saved time.
