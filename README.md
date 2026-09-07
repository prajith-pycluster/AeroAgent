# ✈️ AI Travel Planning System

> **A production-oriented multi-agent AI travel planning system built with LangGraph, LangChain, Groq, MCP, PostgreSQL, Streamlit, and Docker.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange)](https://www.langchain.com/langgraph)
[![LangChain](https://img.shields.io/badge/LangChain-Framework-green)](https://www.langchain.com/)
[![Groq](https://img.shields.io/badge/LLM-Groq-purple)](https://groq.com/)
[![MCP](https://img.shields.io/badge/MCP-Tools-black)](https://modelcontextprotocol.io/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)](https://www.docker.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Render](https://img.shields.io/badge/Deployment-Render-46E3B7)](https://render.com/)

---

## 🌐 Live Demo

🚀 **Live Application:**
https://ai-travel-planning-system.onrender.com

📦 **GitHub Repository:**
https://github.com/ashfaque-ahmed78/AI-Travel-Planning-System

---

# 📌 Overview

The **AI Travel Planning System** is an intelligent multi-agent travel assistant capable of planning trips by coordinating multiple specialized AI agents.

Instead of asking a single LLM to perform every task, the system uses a **Supervisor Agent** that dynamically selects and coordinates specialist agents.

The system can handle:

* ✈️ Flight search
* 🏨 Hotel recommendations
* 🌤️ Weather information
* 💰 Travel budget analysis
* 🗺️ Daily itinerary generation
* 👤 Human approval
* 🧠 LLM-based reasoning
* 🔌 MCP tool integration
* 💾 Persistent PostgreSQL checkpoints
* 🐳 Dockerized deployment
* ☁️ Cloud deployment

---

# 🎯 Project Goal

The goal of this project is to demonstrate how a **production-oriented Agentic AI system** can be designed using:

> **LLMs + Multi-Agent Architecture + Tool Calling + MCP + Stateful Workflows + Human-in-the-Loop + Persistent Storage + Docker + Cloud Deployment**

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │      User Input      │
                         │   Travel Request     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Streamlit Frontend │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   LangGraph Workflow │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Supervisor Agent   │
                         │   Task Decomposition │
                         └──────────┬───────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
                 ▼                  ▼                  ▼
        ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
        │ Flight Agent   │ │  Hotel Agent   │ │ Weather Agent  │
        └───────┬────────┘ └───────┬────────┘ └───────┬────────┘
                │                  │                  │
                ▼                  ▼                  ▼
        ┌────────────────────────────────────────────────────┐
        │                    MCP / APIs                      │
        │ Flights │ Hotels │ Weather │ Other External Tools │
        └────────────────────────────────────────────────────┘
                │                  │                  │
                └──────────────────┼──────────────────┘
                                   ▼
                         ┌──────────────────────┐
                         │    Budget Agent      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Itinerary Agent    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Human Approval Loop  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Final Response Agent │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   User / UI Output   │
                         └──────────────────────┘

                  ┌────────────────────────────┐
                  │       PostgreSQL           │
                  │ LangGraph Checkpointing    │
                  └────────────────────────────┘
```

---

# 🤖 Multi-Agent Architecture

The system is composed of specialized agents rather than one monolithic agent.

| Agent                   | Responsibility                                  | Tool / Capability    |
| ----------------------- | ----------------------------------------------- | -------------------- |
| 🧠 Supervisor Agent     | Understands request and selects required agents | LLM reasoning        |
| ✈️ Flight Agent         | Finds and analyzes flight information           | Flight/MCP tools     |
| 🏨 Hotel Agent          | Searches and evaluates accommodation            | Hotel/MCP tools      |
| 🌤️ Weather Agent       | Retrieves weather information                   | Weather MCP/API      |
| 💰 Budget Agent         | Calculates and analyzes trip cost               | LLM + collected data |
| 🗺️ Itinerary Agent     | Creates day-by-day travel plan                  | LLM reasoning        |
| 👤 Human Approval Agent | Allows human review before finalization         | Human-in-the-loop    |
| 📝 Final Response Agent | Produces final user-facing answer               | LLM                  |

---

# 🔄 Agent Execution Workflow

The system does **not** blindly execute every agent.

The Supervisor determines which specialists are necessary.

Example:

```text
User:
"Plan a 3-day Dubai trip from Karachi for 2 people."

                    │
                    ▼
              Supervisor
                    │
       ┌────────────┼─────────────┐
       ▼            ▼             ▼
    Flight        Hotel         Weather
       │            │             │
       └────────────┼─────────────┘
                    ▼
                 Budget
                    │
                    ▼
                Itinerary
                    │
                    ▼
             Human Approval
                    │
                    ▼
             Final Response
```

For a weather-only request:

```text
User
 │
 ▼
Supervisor
 │
 ▼
Weather Agent
 │
 ▼
Itinerary / Final Flow
 │
 ▼
Final Response
```

This conditional routing reduces unnecessary agent execution.

---

# 🧩 Core Technologies

| Technology       | Purpose                                 |
| ---------------- | --------------------------------------- |
| 🐍 Python        | Core programming language               |
| 🦜 LangChain     | LLM and tool integration                |
| 🕸️ LangGraph    | Stateful multi-agent orchestration      |
| ⚡ Groq           | High-speed LLM inference                |
| 🔌 MCP           | Model Context Protocol tool integration |
| 🐘 PostgreSQL    | Persistent state/checkpoint storage     |
| 🎨 Streamlit     | Interactive web interface               |
| 🐳 Docker        | Containerization                        |
| ☁️ Render        | Cloud deployment                        |
| 🔐 python-dotenv | Environment configuration               |
| 🧠 Pydantic      | Data/state validation                   |
| 🔗 psycopg       | PostgreSQL connectivity                 |

---

# ✨ Key Features

| Feature                       | Status |
| ----------------------------- | :----: |
| Multi-Agent Architecture      |    ✅   |
| Supervisor Agent              |    ✅   |
| Conditional Agent Routing     |    ✅   |
| Flight Agent                  |    ✅   |
| Hotel Agent                   |    ✅   |
| Weather Agent                 |    ✅   |
| Budget Agent                  |    ✅   |
| Itinerary Agent               |    ✅   |
| Human-in-the-Loop             |    ✅   |
| MCP Integration               |    ✅   |
| PostgreSQL Checkpointing      |    ✅   |
| Persistent Conversation State |    ✅   |
| Streamlit UI                  |    ✅   |
| Docker Support                |    ✅   |
| Environment Variables         |    ✅   |
| Cloud Deployment              |    ✅   |
| Production Testing            |    ✅   |

---

# 🔌 MCP Integration

The project uses **Model Context Protocol (MCP)** to connect AI agents with external tools and data sources.

Instead of hardcoding external functionality directly into the LLM, MCP provides a standardized interface between the AI system and tools.

```text
                 AI Agent
                    │
                    ▼
               MCP Client
                    │
                    ▼
              MCP Server
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Flights    Weather   Other APIs
```

### Benefits

* Standardized tool integration
* Better separation of concerns
* Reusable tools
* Easier agent development
* External API abstraction
* Scalable agent architecture

---

# 💾 PostgreSQL Persistence

The application uses PostgreSQL with LangGraph checkpointing.

```text
User Request
     │
     ▼
LangGraph
     │
     ▼
Agent Execution
     │
     ▼
PostgreSQL
     │
     ├── Thread State
     ├── Checkpoints
     └── Workflow Progress
```

This allows the application to maintain state across workflow execution.

---

# 👤 Human-in-the-Loop

The system includes a human approval stage before generating the final response.

```text
Agents
  │
  ▼
Generated Travel Plan
  │
  ▼
Human Approval
  │
  ├── Approve ──► Final Response
  │
  └── Modify / Review
```

This design is useful for applications where AI-generated decisions should be reviewed before final execution.

---

# 🧠 LangGraph Workflow

The graph is organized around a stateful `TravelState`.

Simplified workflow:

```text
START
  │
  ▼
Supervisor
  │
  ▼
Selected Specialist Agents
  │
  ├── Flight
  ├── Hotel
  ├── Weather
  ├── Budget
  └── Itinerary
  │
  ▼
Human Approval
  │
  ▼
Final Response
  │
  ▼
END
```

Conditional routing is implemented using LangGraph conditional edges.

---

# 📁 Project Structure

```text
AI-Travel-Planning-System/
│
├── agents/
│   ├── __init__.py
│   ├── supervisor.py
│   ├── flight_agent.py
│   ├── hotel_agent.py
│   ├── weather_agent.py
│   ├── budget_agent.py
│   ├── itinerary_agent.py
│   └── final_response.py
│
├── mcp/
│   ├── flight tools
│   ├── weather tools
│   └── other MCP integrations
│
├── graph.py
├── state.py
├── config.py
├── frontend.py
│
├── Dockerfile
├── requirements.txt
├── .gitignore
├── .env.example
├── README.md
│
└── ...
```

> File names may vary slightly depending on the current project version.

---

# ⚙️ How the System Works

## 1️⃣ User submits a request

Example:

```text
Plan a 3-day trip from Karachi to Dubai for 2 people
with a budget of $1000.
Include flights, hotels, weather and itinerary.
```

---

## 2️⃣ Supervisor analyzes the request

The Supervisor identifies required capabilities:

```text
Flight      → Required
Hotel       → Required
Weather     → Required
Budget      → Required
Itinerary   → Required
```

---

## 3️⃣ Specialist agents execute

Each agent performs its specific task.

```text
Flight Agent
      ↓
Hotel Agent
      ↓
Weather Agent
      ↓
Budget Agent
      ↓
Itinerary Agent
```

---

## 4️⃣ Data is combined

The collected information becomes part of the shared LangGraph state.

---

## 5️⃣ Human approval

The generated plan is reviewed before finalization.

---

## 6️⃣ Final response

The Final Response Agent creates a clean user-facing travel plan.

---

# 🧪 Production Testing

The application has been tested on the deployed cloud environment.

### Test Matrix

| Test | Scenario                   | Expected Result                         |   Status   |
| ---- | -------------------------- | --------------------------------------- | :--------: |
| 01   | Complete travel request    | All required agents execute             |   ✅ PASS   |
| 02   | Weather-only request       | Only relevant specialist agents execute | 🔄 Testing |
| 03   | No flight result           | Agent handles empty result gracefully   |      ⏳     |
| 04   | Budget constraint          | Budget logic responds correctly         |      ⏳     |
| 05   | PostgreSQL persistence     | State survives workflow execution       |      ⏳     |
| 06   | Human approval             | Approval stage works                    |      ⏳     |
| 07   | Invalid input              | Application handles bad input           |      ⏳     |
| 08   | API failure                | Graceful error handling                 |      ⏳     |
| 09   | Final response consistency | Output is coherent and complete         |      ⏳     |
| 10   | Production smoke test      | Complete system works end-to-end        |      ⏳     |

---

# 📊 Example Production Execution

A successful production request produced the following execution pipeline:

```text
Supervisor      ✅ DONE
      ↓
Flight Agent    ✅ DONE
      ↓
Hotel Agent     ✅ DONE
      ↓
Weather Agent   ✅ DONE
      ↓
Budget Agent    ✅ DONE
      ↓
Itinerary       ✅ DONE
      ↓
Human Approval  ✅
      ↓
Final Response  ✅
```

The system successfully connected:

```text
Streamlit
   ↓
LangGraph
   ↓
Groq
   ↓
MCP Tools
   ↓
External APIs
   ↓
PostgreSQL
   ↓
Final Response
```

---

# 🐳 Docker

The application is containerized using Docker.

### Build

```bash
docker build -t ai-travel-planning-system .
```

### Run

```bash
docker run -p 8501:8501 ai-travel-planning-system
```

Application:

```text
http://localhost:8501
```

---

# 🛠️ Local Development

## 1. Clone the repository

```bash
git clone https://github.com/ashfaque-ahmed78/AI-Travel-Planning-System.git
```

```bash
cd AI-Travel-Planning-System
```

---

## 2. Create virtual environment

### Windows

```bash
python -m venv .venv
```

Activate:

```bash
.venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure environment variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
AVIATION_STACK_API_KEY=your_aviation_stack_api_key

DATABASE_URL=your_postgresql_connection_string
```

> Never commit `.env` or API keys to GitHub.

---

# ▶️ Run the Application

Start the Streamlit application:

```bash
streamlit run frontend.py
```

Then open:

```text
http://localhost:8501
```

---

# 🔐 Environment Variables

| Variable                 | Required | Purpose               |
| ------------------------ | :------: | --------------------- |
| `GROQ_API_KEY`           |     ✅    | LLM inference         |
| `TAVILY_API_KEY`         |     ✅    | Search functionality  |
| `OPENWEATHER_API_KEY`    |     ✅    | Weather data          |
| `AVIATION_STACK_API_KEY` |     ✅    | Flight information    |
| `DATABASE_URL`           |     ✅    | PostgreSQL connection |

---

# ☁️ Deployment

The application is deployed using:

```text
GitHub
   │
   ▼
Docker
   │
   ▼
Render
   │
   ├── Web Service
   │
   └── PostgreSQL
```

### Production Stack

| Layer               | Technology        |
| ------------------- | ----------------- |
| Source Control      | GitHub            |
| Container           | Docker            |
| Application Hosting | Render            |
| Database            | Render PostgreSQL |
| UI                  | Streamlit         |
| AI Workflow         | LangGraph         |
| LLM                 | Groq              |
| Tool Layer          | MCP               |

---

# 🚀 Deployment Architecture

```text
                    INTERNET
                        │
                        ▼
              ┌──────────────────┐
              │      Render      │
              │   Web Service    │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │     Docker       │
              │   Container      │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │    Streamlit     │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │    LangGraph     │
              └────────┬─────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     Groq LLM       MCP Tools      PostgreSQL
        │              │              │
        ▼              ▼              ▼
     Reasoning      External APIs   Checkpoints
```

---

# 📈 Why Multi-Agent Instead of One Agent?

A single LLM could theoretically perform the entire task, but separating responsibilities provides better modularity.

| Single Agent             | Multi-Agent                  |
| ------------------------ | ---------------------------- |
| One large responsibility | Specialized responsibilities |
| Difficult debugging      | Easier debugging             |
| Harder tool management   | Agent-specific tools         |
| Less modular             | Highly modular               |
| Difficult to extend      | Easy to add new agents       |
| Complex prompts          | Smaller focused prompts      |

---

# 🔀 Conditional Routing

One of the key features is dynamic routing.

For example:

```text
User:
"What's the weather in Dubai?"
```

The Supervisor can determine:

```text
Weather Agent → Required
Flight Agent  → Not Required
Hotel Agent   → Not Required
Budget Agent  → Not Required
```

This prevents unnecessary execution.

---

# 🧱 State Management

The agents communicate through a shared state.

Conceptually:

```python
TravelState = {
    "user_request": "...",
    "selected_agents": [],
    "flight_data": {},
    "hotel_data": {},
    "weather_data": {},
    "budget_data": {},
    "itinerary": {},
    "human_approval": False,
    "final_response": ""
}
```

This shared state allows every agent to access relevant information generated earlier in the workflow.

---

# 🛡️ Security

The project follows basic secret-management practices.

Sensitive information is stored using environment variables.

```text
.env
.env.docker
.streamlit/secrets.toml
```

These files should never be committed to GitHub.

Recommended `.gitignore`:

```gitignore
.env
.env.docker
.venv/
__pycache__/
*.pyc
.streamlit/secrets.toml
```

---

# 🧰 Error Handling

The production system is designed to handle common failures such as:

* Missing API results
* Invalid user requests
* External API failures
* Database connection problems
* Empty tool responses
* Agent execution errors

The next stage of testing focuses on validating these edge cases systematically.

---

# 📸 Screenshots

Add your best application screenshots here.

```markdown
![Application Dashboard](screenshots/dashboard.png)

![Agent Execution](screenshots/agent-execution.png)

![Final Travel Plan](screenshots/final-response.png)
```

Recommended screenshots:

| Screenshot            | Purpose                       |
| --------------------- | ----------------------------- |
| Dashboard             | Shows UI                      |
| Mission Control       | Shows selected agents         |
| Execution Pipeline    | Demonstrates orchestration    |
| MCP Results           | Demonstrates tool integration |
| Final Response        | Shows user experience         |
| Production Deployment | Demonstrates live application |

---

# 🎥 Demo

Add your demo video/GIF here.

```markdown
![Demo](assets/demo.gif)
```

Or:

```markdown
## 🎥 Project Demo

Watch the complete system workflow from user request to final AI-generated travel plan.
```

---

# 📚 What This Project Demonstrates

This project demonstrates practical experience with:

```text
Python
   ↓
LangChain
   ↓
LangGraph
   ↓
Multi-Agent Systems
   ↓
Tool Calling
   ↓
MCP
   ↓
LLM Reasoning
   ↓
State Management
   ↓
PostgreSQL
   ↓
Docker
   ↓
Cloud Deployment
```

---

# 🧠 Engineering Concepts

The project applies several important production AI engineering concepts:

* Agent orchestration
* Conditional routing
* Shared state
* Tool calling
* MCP architecture
* Human-in-the-loop
* Persistent checkpoints
* Environment-based configuration
* Containerization
* Cloud deployment
* Production testing
* API integration
* Modular agent design

---

# 🔮 Future Improvements

Planned improvements include:

* [ ] Better flight API integration
* [ ] Better hotel API integration
* [ ] Real-time pricing validation
* [ ] Improved budget calculations
* [ ] Agent retry mechanisms
* [ ] Automatic error recovery
* [ ] Structured output validation
* [ ] LangSmith observability
* [ ] Rate limiting
* [ ] Authentication
* [ ] Automated CI/CD
* [ ] Unit tests
* [ ] Integration tests
* [ ] Production monitoring
* [ ] Better UI/UX
* [ ] Streaming agent responses
* [ ] More travel tools
* [ ] Multi-language support

---

# 🧪 Testing Strategy

The testing strategy follows multiple levels:

```text
Unit Tests
    ↓
Agent Tests
    ↓
Routing Tests
    ↓
Tool Tests
    ↓
Database Tests
    ↓
Integration Tests
    ↓
Docker Tests
    ↓
Production Tests
    ↓
End-to-End Smoke Test
```

---

# 🏆 Project Status

| Component            |     Status     |
| -------------------- | :------------: |
| Core Architecture    |   🟢 Complete  |
| Multi-Agent Workflow |   🟢 Complete  |
| LangGraph            |   🟢 Complete  |
| MCP Integration      |   🟢 Complete  |
| PostgreSQL           |   🟢 Complete  |
| Streamlit UI         |   🟢 Complete  |
| Docker               |   🟢 Complete  |
| GitHub               |   🟢 Complete  |
| Cloud Deployment     |   🟢 Complete  |
| Production Testing   | 🟡 In Progress |
| Advanced Monitoring  |   🔵 Planned   |
| CI/CD                |   🔵 Planned   |

---

# 👨‍💻 Author

## Ashfaque Ahmed

**AI Agent Developer | AI Automation | LangChain | LangGraph | Python**

I build AI-powered applications using:

* Python
* LangChain
* LangGraph
* Agentic AI
* MCP
* FastAPI
* Docker
* PostgreSQL
* Cloud Deployment

---

# ⭐ Support

If you found this project useful or interesting:

⭐ **Star the repository**

🍴 **Fork the project**

🐛 **Open an issue**

💡 **Suggest an improvement**

---

# 📄 License

This project is available for educational and portfolio purposes.

---

## 🚀 Final Architecture Summary

```text
                         ┌─────────────┐
                         │    USER     │
                         └──────┬──────┘
                                │
                                ▼
                         ┌─────────────┐
                         │  STREAMLIT  │
                         └──────┬──────┘
                                │
                                ▼
                         ┌─────────────┐
                         │ LANGGRAPH   │
                         └──────┬──────┘
                                │
                                ▼
                         ┌─────────────┐
                         │ SUPERVISOR  │
                         └──────┬──────┘
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
         ✈️ Flight           🏨 Hotel          🌤️ Weather
             │                  │                  │
             └──────────────────┼──────────────────┘
                                │
                                ▼
                         ┌─────────────┐
                         │   BUDGET    │
                         └──────┬──────┘
                                │
                                ▼
                         ┌─────────────┐
                         │ ITINERARY   │
                         └──────┬──────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ HUMAN APPROVAL  │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ FINAL RESPONSE  │
                       └────────┬────────┘
                                │
                                ▼
                             USER

        ┌─────────────────────────────────────────────┐
        │                    MCP                      │
        │      External APIs / Tools / Services      │
        └─────────────────────────────────────────────┘
                           │
                           ▼
                    Specialist Agents

        ┌─────────────────────────────────────────────┐
        │                 PostgreSQL                  │
        │          LangGraph Persistence              │
        └─────────────────────────────────────────────┘
```

> **Built with Python + LangGraph + LangChain + Groq + MCP + PostgreSQL + Docker + Streamlit**
