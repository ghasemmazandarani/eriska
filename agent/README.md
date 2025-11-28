# Eriska Security Agent V2

The second, improved version of the Eriska Security Agent with advanced capabilities, featuring a **LangGraph-based Multi-Agent AI System**.

## 🧠 AI Capabilities (New)

Agent V2 introduces a sophisticated AI engine powered by **Gemini 2.5 Pro** and **LangGraph**. It orchestrates five specialized agents to perform deep security analysis:

### Multi-Agent Workflow

1.  **📡 ScanMonitor**: Continuously monitors the network for new devices and changes.
2.  **🔍 DeviceIdentifier**: Uses RAG (Retrieval-Augmented Generation) to fingerprint devices with high accuracy.
3.  **🛡️ CVEHunter**: Correlates findings with a massive CVE database to find vulnerabilities.
4.  **⚡ AttackPath**: Analyzes potential attack vectors and lateral movement paths (Runs in parallel with CVEHunter).
5.  **⚖️ DebateSynthesis**: Verifies findings through a multi-agent debate process to reduce false positives and generates a human-readable report.

## 🚀 Installation & Usage

### Prerequisites

- Python 3.8+
- Google Gemini API Key

### Installation

```bash
pip install -r requirements.txt
```

### Running in AI Mode

To start the AI-powered security analysis:

```bash
python main.py --mode ai --api-key YOUR_GEMINI_API_KEY
```

### Continuous Monitoring

To run in continuous mode (scanning every 5 minutes):

```bash
python main.py --mode ai --continuous --interval 300
```

### Standard Modes

You can still use the standard scanning modes:

```bash
# Network Scan
python main.py --mode active

# Router Scan
python main.py --mode router --router-ip 192.168.1.1 ...
```
