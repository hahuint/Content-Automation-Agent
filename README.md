# Content Automation Agent

An enterprise-grade, deterministic content pipeline designed to research, draft, publish, and distribute articles across multiple platforms. Powered by LangGraph for state-machine orchestration, local LLMs for curation, and external APIs for content synthesis.

For a deep dive into the system design, diagrams, and technical advantages, see the [System Architecture](architecture.md).

## Key Features

- **StateGraph Orchestration**: Utilizes LangGraph to manage the automated content loop (Audit -> Research -> Draft -> Publish -> Log). This deterministic state machine ensures 100% execution reliability without relying on the LLM to route actions.
- **Decoupled Architecture**: The pipeline delegates text generation to a secondary model via the `delegate_to_journalist` abstraction. This allows a local, low-resource model to handle workflow orchestration while offloading heavy SEO content generation to external APIs (e.g., Grok, OpenAI).
- **Algorithmic Curation**: Aggregates live news via RSS, cross-references against local audit logs to prevent duplication, and evaluates headlines to select the optimal topic before drafting begins.
- **Plug-and-Play Publishing**: Synthesizes structured HTML articles and fetches relevant media. Interfaces securely with the WordPress REST API if configured, otherwise remains platform-agnostic.
- **Omnichannel Social Broadcast**: Distributes publications across social platforms via official APIs (e.g., Telegram, X/Twitter). Easily configurable or skippable via environment variables.
- **Audit Logging**: Maintains a local SQLite database (`agent_audit.db`) for comprehensive workflow tracking and state preservation.

---

## Setup & Configuration

1. **Environment Variables**: Clone the repository, duplicate the `.env.example` file to `.env`, and populate the necessary credentials:
   ```env
   # Core Config
   WP_URL=https://yourwebsite.com/wp-json/wp/v2
   WP_USERNAME=your_wp_username
   WP_APP_PASSWORD=your_app_password
   PEXELS_API_KEY=your_pexels_key
   GROK_API_KEY=your_grok_key
   MODEL_NAME=llama3.2:3b

   # Social Config (Optional)
   TELEGRAM_BOT_TOKEN=...
   TELEGRAM_CHAT_ID=...
   X_API_KEY=...
   X_API_SECRET=...
   X_ACCESS_TOKEN=...
   X_ACCESS_SECRET=...
   ```
   *(Note: To generate a WordPress App Password, navigate to WP Admin -> Users -> Profile -> Application Passwords).*

2. **Local Orchestrator Model**: Ensure [Ollama](https://ollama.com/) is running on the host system with the orchestration model pulled (`ollama run llama3.2:3b`).

---

## Deployment via Docker (Recommended)
Docker provides an isolated environment containing all dependencies, ensuring zero interruptions to your local workflow.

```bash
# Build the container image
docker-compose build

# Run the container process
docker-compose run --rm agent
```

## Local Environment (Mac/Linux/Windows)
If running natively on the host machine:

```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
python main.py
```

---

## Operation Modes

Upon startup, the system requests an operation mode:

*   **Mode 1: Manual Mode**: Interface directly with the orchestration model. Example instructions: *"Fetch the latest tech news"* or *"Check your audit logs, what did you do today?"*
*   **Mode 2: Automated Content Loop**: The system enters continuous execution. It runs the LangGraph pipeline every hour to evaluate news, publish an article, distribute the link, and record the activity log.

---

## Architecture Map

- **`core/`**: Contains pipeline orchestration logic (`autopilot_graph.py`), language model instantiation (`agent_setup.py`), and configuration variables.
- **`tools/`**: The abstracted functions connecting the orchestrator's decisions to physical system actions.
- **`services/`**: Pure Python wrappers for external endpoints (WordPress, Pexels, HackerNews, RSS) kept strictly separated from LLM logic.
- **`tests/`**: Pytest suite using mocked responses for offline validation.

---

## Developer

**Tesfay G Chekole**  
*Machine Learning Engineer, Co-Founder @ [HahuScholar](https://hahuscholar.com)*  
- LinkedIn: [https://www.linkedin.com/in/hopetesfa/](https://www.linkedin.com/in/hopetesfa/)
- X (Twitter): [@hopegeb](https://twitter.com/hopegeb)
