# System Architecture

The Content Automation Agent is designed using a **decoupled, modular architecture**, ensuring maximum stability, testability, and upgradeability.

## 1. System Context Diagram (Level 1)

This high-level diagram shows the Content Automation Agent as a central system and its relationships with external users and third-party ecosystems.

```mermaid
graph LR
    %% Styles
    classDef system fill:#4f46e5,stroke:#312e81,color:#fff,stroke-width:2px;
    classDef user fill:#f59e0b,stroke:#b45309,color:#fff,stroke-width:2px;
    classDef external fill:#64748b,stroke:#334155,color:#fff,stroke-width:2px;

    User(("<b>User / Admin</b>")):::user
    Agent["<b>Content Automation Agent</b><br/>(Deterministic Orchestrator)"]:::system
    
    subgraph "External Ecosystem"
        News["<b>News Sources</b><br/>RSS / HackerNews"]:::external
        AI["<b>AI Services</b><br/>Grok 4.1 / Gemini 2.5 Flash"]:::external
        Publishing["<b>Publication Platforms</b><br/>WordPress / Telegram / X"]:::external
    end

    User -->|Triggers & Configures| Agent
    Agent -->|1. Fetches News| News
    Agent -->|2. Synthesizes Content| AI
    Agent -->|3. Distributes Articles| Publishing
    Publishing -->|Delivers Content| User
```

## 2. Container Diagram (Level 2)

This diagram illustrates the logical containers within the system and how data flows through the deterministic pipeline.

```mermaid
graph TD
    subgraph "Content Automation System (Docker Container)"
        ORCH["<b>Orchestrator</b><br/>(LangGraph Engine)"]
        DB[("<b>Audit Store</b><br/>SQLite DB")]
        
        subgraph "Functional Modules"
            RESEARCH["<b>Research Module</b><br/>(RSS / HackerNews)"]
            WRITER["<b>Content Creator</b><br/>(AI Journalist)"]
            DIST["<b>Distributor</b><br/>(WP / Social APIs)"]
        end
    end

    %% Flow
    ORCH <-->|Audit Check| DB
    ORCH -->|1. Trigger Research| RESEARCH
    RESEARCH -->|Raw Headlines| ORCH
    ORCH -->|2. Delegate Drafting| WRITER
    WRITER -->|Draft JSON| ORCH
    ORCH -->|3. Publish & Broadcast| DIST
    DIST -->|Success URL| DB
```

### Data Inputs & Outputs
| Entity | Type | Description |
| :--- | :--- | :--- |
| **Inputs** | Raw Headlines | Fetched from global RSS feeds (Trending vs Global). |
| **Input** | Configuration | API Keys and Preferences loaded via `.env`. |
| **Output** | HTML Post | A fully formatted SEO article published to WordPress Website. |
| **Output** | Broadcast | Real-time notifications sent to Telegram and X (Twitter) APIs. |
| **Output** | Audit Log | A record of the transaction stored in `agent_audit.db`. |

---

## 3. Technical Core Advantages

### 🛡️ Multi-Layered Duplication Prevention
The system implements a hardened memory system to ensure no topic is ever repeated, even across container restarts:
- **Layer 1 (AI Context)**: The orchestrator injects the last 30 published topics directly into the LLM's prompt with strict negative constraints.
- **Layer 2 (Python Safety Check)**: A secondary code-level check performs string similarity analysis on every chosen topic. If a match is detected, the cycle is terminated before any resources are consumed.
- **Persistent Volumes**: In Docker environments, the SQLite database is mapped via host volumes, ensuring the agent "remembers" its history even after being stopped or rebuilt.

### 🔄 High-Availability & Resilience
- **Persistent Sessions**: The WordPress service utilizes `requests.Session` with custom `User-Agent` headers to mitigate SSL EOF errors and WAF blocking.
- **Automated Retries**: Critical paths (CMS uploads, Media fetching) implement exponential backoff via the `tenacity` library, allowing the agent to silently recover from transient DNS or network resolution failures.
- **Multi-LLM Strategy**: Primary synthesis via Grok 4.1 Fast with a seamless fallback to Gemini 2.5 Flash ensures the content pipeline never stalls.

---

## 4. Directory Structure

- **`core/`**: Orchestration logic and initialization. Contains LangGraph workflows and environment configuration.
- **`tools/`**: The abstraction layer. LangChain `@tool` functions connecting the engine to system actions.
- **`services/`**: The integration layer. Pure Python classes for API interaction (WP, Grok, Pexels, SQLite).
- **`tests/`**: Pytest suite using mocked HTTP responses to guarantee system integrity.

---

## 5. Workflow Modes

- **Manual Mode**: Direct terminal interaction for specific research or audit queries.
- **Automated Content Loop**: A continuous background process executing the full pipeline hourly.

---

## 6. Technical Verification Snapshot

The system's accuracy is verified against live global events. Snapshot as of **April 29, 2026**:

![News Verification Table](images/verification.png)
