📖 LiteratureAgent

A resource-constrained, multi-agent orchestration system for autonomous long-form literature generation (≥200,000 words). Designed for headless Ubuntu 24.04 VPS environments with a strict ≤2GB RAM footprint, the system dynamically routes tasks between local Ollama models and cloud LLM APIs. It features a Telegram control interface, checkpointed DAG execution, and a FastAPI export pipeline.

⚠️ Note: This is an agentic orchestration layer, not a neural architecture. OpenMythos principles are conceptually adapted into workflow patterns, routing logic, and state management.

✨ Key Features

Multi-Agent DAG Pipeline:
Orchestrator → Planner → Thinker → Writer → Reviewer → Compiler with persistent state and interruptible execution.

≤2GB RAM Optimization: LRU memory pooling, disk-backed context serialization, streaming I/O, and automatic fallback when local inference exceeds thresholds.

MoE-Inspired Routing: Dynamic LLM provider selection balancing cost, speed, quality, and memory pressure with bias-adjusted load balancing.

ACT Halting & Convergence: Iterative refinement loops with quality-scoring early stopping to prevent redundant API calls and compute waste.

LTI-Stable State Management: Periodic consistency checks, atomic checkpointing, and rollback mechanisms to prevent narrative drift.

Telegram Control: Remote job management, parameter tuning, pause/resume, and progress monitoring via aiogram.

Web Export Pipeline: FastAPI server for real-time status and multi-format export (Markdown, PDF, ePub, DOCX via pandoc).

Production-Ready: Async I/O, structured logging (loguru), exponential backoff retries, systemd service integration, and zero-copy data passing.

🏗️ System Architecture
<img width="763" height="502" alt="image" src="https://github.com/user-attachments/assets/89741037-6d5b-4f90-aa8c-f2199a7240b3" />

🔬 OpenMythos Conceptual Mapping
<img width="1067" height="560" alt="image" src="https://github.com/user-attachments/assets/befebb81-d238-4c76-9796-dcd209f9db9c" />

⚙️ Prerequisites

OS: Ubuntu 24.04 (recommended)
Python: 3.10+
RAM: ≤2GB (strictly managed)
Dependencies: pandoc, texlive-xetex (for PDF export), ollama (optional, for local inference)
Accounts: Telegram Bot Token, OpenAI/Together/Cloud API keys

🚀 Quick Start

1. Clone & Setup

git clone https://github.com/chelotithehost-sketch/Literature-Agent-System.git
cd LiteratureAgent
chmod +x setup.sh
./setup.sh

2. Configure Environment

cp config/default.yaml config/local.yaml
# Edit local.yaml to adjust models, routing weights, or thresholds

Set environment variables:

export OPENAI_API_KEY="your_key_here"
export TOGETHER_API_KEY="your_key_here"
export TELEGRAM_BOT_TOKEN="your_bot_token"

3. Run Locally

source venv/bin/activate
python run.py

💬 Usage
Telegram Commands
<img width="1088" height="386" alt="image" src="https://github.com/user-attachments/assets/64eac3ef-d41b-4359-aae6-833be134391b" />

Web API (FastAPI)
Base URL: http://127.0.0.1:8000

<img width="1081" height="287" alt="image" src="https://github.com/user-attachments/assets/f670a7b4-88e3-4e90-96f1-c93a3e992ddf" />

📦 Production Deployment (Systemd)
Enable persistent, auto-restarting service:

sudo systemctl daemon-reload
sudo systemctl enable literature_agent
sudo systemctl start literature_agent
sudo journalctl -u literature_agent -f  # View logs

Service handles:
Virtual environment isolation
Memory pressure monitoring
Automatic restart on failure (Restart=on-failure)
Clean shutdown with checkpoint preservation

📁 Project Structure

<img width="726" height="568" alt="image" src="https://github.com/user-attachments/assets/506e4262-1f88-48b3-a861-57a1d497f4e9" />

⚠️ Resource Management & Constraints

This system is engineered for ≤2GB RAM environments. Key strategies:

LRU Memory Pool: Evicts stale context objects when threshold (1.5GB) is crossed.

Disk-Backed State: All chapter drafts, metadata, and routing states serialize to data/checkpoints/ after each agent cycle.

Streaming & Lazy Loading: Token generation and API responses stream directly to disk; no full-manuscript RAM caching.

Quantization Fallback: If Ollama local inference triggers memory pressure, the Router automatically falls back to cloud providers.

Async I/O: Non-blocking network calls prevent thread starvation and reduce context-switch overhead.

📜 License & Disclaimer

MIT License © 2026
This repository is an independent, community-driven agentic implementation. It is not affiliated with, endorsed by, or connected to Anthropic, OpenMythos authors, or any proprietary LLM providers. The OpenMythos architectural concepts are used as theoretical inspiration for agentic workflow design, not as neural weight implementations.
Use responsibly. Monitor API costs. Respect provider rate limits.

📚 References & Inspiration
OpenMythos: Recurrent-Depth Transformers
Universal Transformers & ACT Halting
Parcae: Scaling Laws for Stable Looped Models
DeepSeekMoE: Fine-Grained Expert Routing

Built for researchers, writers, and engineers pushing the boundaries of constrained autonomous generation.
