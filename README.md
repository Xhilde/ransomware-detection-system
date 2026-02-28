# Behavior-Based Ransomware Detection System

A real-time ransomware detection engine built in Python that identifies malicious file system behavior and correlates it with process-level indicators — without relying on signatures.

![Detection Demo](Screenshot%202026-02-28%20210820.png)

---

## Overview

Traditional antivirus relies on known signatures. Modern ransomware variants mutate frequently, obfuscate payloads, and evade static scanning. This system takes a different approach — detecting ransomware by **what it does**, not what it looks like.

The monitor watches a target directory and flags:

- Mass file creation or modification within a rolling time window
- Rapid file extension changes consistent with encryption (e.g. `file.txt` → `file.encrypted`)
- High CPU usage processes spawned around the time of file activity
- Recently started processes correlated with suspicious events

When thresholds are exceeded, the engine calculates a **suspicion score**, raises an alert, and logs correlated process data.

---

## Detection Logic

### Burst File Activity
File events are tracked within a 60-second rolling window. If the event count crosses the configured threshold, a ransomware-like activity alert is triggered.

### Extension Anomaly Detection
The system monitors file rename operations. A spike in extension changes (e.g. bulk `.encrypted` renames) triggers a high-severity warning independent of the burst threshold.

### Process Correlation
Using `psutil`, the engine inspects running processes at alert time — surfacing high CPU consumers and recently spawned processes likely responsible for the file activity.

### Suspicion Score
Rather than binary detection, the system outputs a weighted risk score based on:
- Number of high-CPU processes
- Number of recently started processes
- File burst intensity
- Extension anomaly rate

---

## Architecture

```
Monitored Directory
        ↓
Watchdog File Observer
        ↓
File Event Handler
        ↓
Behavior Analysis Engine
        ↓
Process Correlation (psutil)
        ↓
Suspicion Score + Alert + Logging
```

---

## Project Structure

```
ransomware-detection-system/
├── monitor/
│   └── file_monitor.py        # Core file system monitoring logic
├── ai_engine/                 # Behavior analysis and scoring engine
├── main.py                    # Entry point
├── .gitignore
└── requirements.txt
```

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Xhilde/ransomware-detection-system.git
cd ransomware-detection-system
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate (Windows):
```powershell
.\.venv\Scripts\activate
```

Activate (macOS/Linux):
```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Monitor

```bash
cd monitor
python file_monitor.py
```

To save output to a log file:
```bash
python file_monitor.py > ../logs/session.log
```

---

## Simulating a Ransomware Attack (PowerShell)

Use the following commands to simulate ransomware behavior against a test directory:

```powershell
# Step 1 — Create target files
1..15 | ForEach-Object { New-Item "sim$_.txt" }

# Step 2 — Modify file contents (simulate data encryption)
Get-ChildItem sim*.txt | ForEach-Object { Add-Content $_ "encrypted_payload" }

# Step 3 — Rename files (simulate extension hijacking)
Get-ChildItem sim*.txt | ForEach-Object {
    Rename-Item $_ ($_.BaseName + ".encrypted")
}

# Step 4 — Delete files
Remove-Item sim*.encrypted
```

> ⚠️ Run this only in an isolated test directory. Never simulate on production file systems.

---

## Detection Screenshots

| Burst Detection | Extension Anomaly |
|---|---|
| ![](Screenshot%202026-02-28%20210820.png) | ![](Screenshot%202026-02-28%20210903.png) |

| Process Correlation | Suspicion Score |
|---|---|
| ![](Screenshot%202026-02-28%20210951.png) | ![](Screenshot%202026-02-28%20211047.png) |

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3 | Core language |
| `watchdog` | Real-time file system monitoring |
| `psutil` | Process inspection and correlation |
| `logging` | Structured alert and event logging |
| PowerShell | Attack simulation |

---

## Roadmap

- [ ] Entropy-based encryption detection
- [ ] Automatic malicious process termination
- [ ] Real-time web dashboard
- [ ] Email/SMS alerting integration
- [ ] Machine learning anomaly scoring
- [ ] Cross-platform support (Linux/macOS)

---

## Disclaimer

This project is intended for **educational and research purposes only**. Do not deploy against systems you do not own or have explicit permission to test.

---
