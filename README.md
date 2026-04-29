# Content Automation Agent

An enterprise-grade, deterministic content pipeline designed to research, draft, publish, and distribute articles across multiple platforms. Powered by LangGraph for state-machine orchestration, local LLMs for curation, and external APIs for content synthesis.

For a deep dive into the system design, diagrams, and technical advantages, see the [System Architecture](architecture.md).

## ✨ Features

- **Deterministic Orchestration**: Reliable LangGraph state machine loop.
- **Decoupled Synthesis**: Local orchestration with cloud-scale content generation.
- **Omnichannel Support**: Automatic distribution to WordPress, Telegram, and X.
- **Audit System**: Built-in duplicate prevention and execution logging.
- **Enterprise Ready**: Full Docker support and professional CI/CD pipeline.

---

## 🚀 Results Showcase

When the agent is active, it produces high-fidelity, SEO-optimized content autonomously.


### 🖥️ Terminal Output (Orchestration)
```text
[14:30:05] Starting new content cycle...
🔍 [Audit] Checking recent history... No duplicates found.
📡 [Research] Fetching trending tech news...
🧠 [Orchestrator] Evaluating headlines...
✅ [Selection] Optimal topic: "The Rise of Autonomous AI Agents"
✍️ [Journalist] Composing SEO-optimized HTML article...
🚀 [Publish] Article injected into WordPress CMS.
📢 [Broadcast] Sent update to Telegram and X (Twitter).
[14:31:12] Cycle complete.
```

---

## 🛠️ Quick Start

### 1. Configure Environment
Clone the repo and create your `.env` file from the template:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 2. Run via Docker (Recommended)
```bash
make docker-build
make docker-run
```

### 3. Native Setup
```bash
make setup
make run
```

---

## 📖 Documentation & Architecture

For a deep dive into the system design, C4 diagrams, and technical advantages, please refer to the **[System Architecture Guide](architecture.md)**.

---

## 🤝 Contributing

Contributions are welcome! Please see our **[Contributing Guidelines](CONTRIBUTING.md)** for details on how to get started.

---

## 👤 Developer

**Tesfay G Chekole**  
*Machine Learning Engineer, Co-Founder @ [HahuScholar](https://hahuscholar.com)*  
- LinkedIn: [hopetesfa](https://www.linkedin.com/in/hopetesfa/)
- X (Twitter): [@hopegeb](https://twitter.com/hopegeb)
