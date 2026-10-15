# Balance Bora Agentic AI

**An AI-powered livestock feed advisory prototype for climate-resilient livestock production in Kenya.**

[![Live API](https://img.shields.io/badge/API-Deployed%20on%20Render-blue)](https://balance-bora-agentic-ai.onrender.com/)
[![API Docs](https://img.shields.io/badge/API%20Docs-Swagger-green)](https://balance-bora-agentic-ai.onrender.com/docs)
[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)

## 1. Problem Statement

Smallholder livestock farmers in Kenya face high feed costs, inconsistent access to quality feed ingredients, limited access to reliable nutrient-composition information, and difficulty formulating affordable, balanced rations using locally available resources.

Poor feed decisions can reduce livestock productivity and profitability. Farmers and extension officers need accessible tools that bring together feed composition, ingredient prices, and livestock requirements to support better feeding decisions.

## 2. Solution Overview

Balance Bora is developing an AI-powered feed advisory agent that connects livestock nutrition information, feed-price data, and livestock assessment tools.

The intended workflow is to help users:

- Describe their livestock, production level, and feeding objectives.
- Identify locally available feed ingredients.
- Retrieve relevant nutrient-composition information.
- Consult available ingredient-price information.
- Assess feeding options and receive understandable guidance.
- Review recommendations before using them in livestock production.

The long-term goal is to make livestock nutrition advice more accessible through farmer-friendly channels, including WhatsApp and other mobile-based interfaces.

**Current status:** The API is deployed on Render. The public service currently exposes the API home page, health endpoint, and interactive documentation. Full AI-agent and MCP-tool integration in the hosted deployment remains under development and must be verified before the service is presented as a fully operational advisory agent.

## 3. Target Users

- **Smallholder livestock farmers:** seeking affordable feeding options and practical livestock nutrition guidance.
- **Livestock extension officers:** supporting farmers with feeding and management decisions.
- **Animal nutritionists and researchers:** assessing feed composition and livestock feeding requirements.
- **Farmer cooperatives and producer organizations:** supporting members with feed planning and access to feed information.
- **Feed suppliers:** potentially supporting more transparent access to ingredient prices and availability.

## 4. System Architecture

The intended architecture separates the user-facing API, agent reasoning, specialist tools, and underlying data.

```text
Farmer / Extension Officer
            |
            v
      FastAPI Interface
            |
            v
     PydanticAI Agent
            |
            v
      MCP Client Layer
       /      |       \
      v       v        v
 Nutrient   Price   Livestock
  Server   Server   Assessment
      \       |        /
       v      v       v
   Feed Data / Price Data
            |
            v
   Advisory Response
            |
            v
     Human Review
```

This diagram describes the **intended integrated workflow**. The deployed API does not yet have all MCP servers connected at runtime.

## 5. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application and agent implementation |
| FastAPI | HTTP API and application endpoints |
| Uvicorn | ASGI server |
| PydanticAI | Agent orchestration and model integration |
| OpenAI-compatible model interface | Connects the agent to a compatible language model provider |
| Ollama / Qwen | Local model configuration used during development |
| Model Context Protocol (MCP) | Interface between the agent and specialist tools |
| SQLite | Local structured feed-data storage |
| OpenPyXL | Reading spreadsheet-based feed-price data |
| Render | Public API hosting |
| GitHub | Source-code version control |

The exact model provider and MCP configuration depend on the execution environment. A local Ollama endpoint is not automatically accessible from a cloud-hosted service.

## 6. Agent Architecture

The agent is designed to coordinate specialist tools rather than relying solely on free-form language generation.

The intended processing sequence is:

1. Receive a livestock-feeding question.
2. Interpret the user's request and identify relevant information.
3. Call appropriate specialist tools when available.
4. Use returned nutrient, price, or livestock-assessment information to inform the response.
5. Explain the resulting advice and identify missing information or assumptions.
6. Return the response for human review.

The agent uses PydanticAI and an OpenAI-compatible model interface. Tool availability depends on successful MCP server initialization and model configuration.

## 7. MCP Implementation

The project uses the Model Context Protocol (MCP) to separate specialist functionality from the main agent.

Each specialist server exposes tools that the agent can access through an MCP client. During local development, the servers communicate with the client through standard input/output (stdio).

The current codebase contains three specialist server modules:

- `balance_bora_nutrient_mcp.py`
- `balance_bora_price_mcp.py`
- `balance_bora_assessment_mcp.py`

The hosted deployment currently starts the FastAPI application without initializing these MCP servers. Therefore, the complete MCP workflow is **not yet operational on the public Render service**.

## 8. MCP Tools and Servers

### Nutrient server

**File:** `balance_bora_nutrient_mcp.py`

Designed to access feed nutrient-composition information stored in the local SQLite database, `Balance_Bora_Feed.db`.

### Price server

**File:** `balance_bora_price_mcp.py`

Designed to retrieve ingredient-price information from the feed-price workbook, `Balance_Bora_Feed_Price_Template.xlsx`.

Price information must be checked for completeness, freshness, and verification status. Example or placeholder prices must not be represented as current market prices.

### Livestock assessment server

**File:** `balance_bora_assessment_mcp.py`

Designed to support livestock-related assessment tasks that inform feeding advice.

The availability and outputs of each tool should be verified through integration tests before the full agent is used for practical feeding decisions.

## 9. Setup and Installation

### Prerequisites

- Python 3.x
- Git
- A compatible language-model provider
- The project data files required by the nutrient and price servers

Clone the repository:

```bash
git clone https://github.com/davidmarii/balance-bora-agentic-ai.git
cd balance-bora-agentic-ai
```

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux or macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The dependency versions and MCP server environment must be made compatible before starting the complete integrated agent. The current cloud deployment workaround does not activate the MCP servers.

### Model configuration

Configure the environment variables expected by `balance_bora_agent.py` for your chosen OpenAI-compatible provider:

```text
BALANCE_BORA_MODEL=<provider-supported-model>
OPENAI_BASE_URL=<provider-api-base-url>
OPENAI_API_KEY=<provider-api-key>
```

Use the actual values supplied by your provider. Keep API keys private and never commit secrets to GitHub.

For local Ollama development, ensure the model is installed and the Ollama service is running. A cloud-hosted Render service needs a model endpoint that is reachable from Render.

## 10. Usage Instructions

### Start the deployed API

Open:

- API home: https://balance-bora-agentic-ai.onrender.com/
- Health check: https://balance-bora-agentic-ai.onrender.com/health
- Interactive documentation: https://balance-bora-agentic-ai.onrender.com/docs

The home endpoint returns the API name, status, documentation path, and health path.

The health endpoint is intended to confirm that the web application is responding. It does not verify that the model or MCP tools are operational.

### Start locally

After dependencies and model configuration are compatible:

```bash
uvicorn app:app --host 127.0.0.1 --port 8000
```

Visit `http://127.0.0.1:8000/docs` to inspect the API.

### Chat endpoint

The API defines a `POST /chat` endpoint that accepts a message. A representative request is:

```json
{
  "message": "I have a dairy cow producing 20 litres of milk per day. What information is needed to formulate an affordable balanced ration using locally available feeds?"
}
```

The endpoint's successful response and full advisory behavior must be tested after model and MCP integration is restored. The example illustrates the intended use; it is not a claim that the current hosted service already produces a verified ration.

## 11. Human-in-the-Loop Workflow

Human oversight is important because livestock feeding recommendations can affect animal health, production, and farm finances.

The intended workflow includes:

1. The farmer or extension officer supplies livestock and feeding information.
2. The agent retrieves relevant information from available tools.
3. The agent prepares an advisory response, including assumptions and missing information where appropriate.
4. A farmer, extension officer, or qualified animal nutritionist reviews the advice.
5. The user confirms or adjusts the information before applying a feeding recommendation.
6. Feedback and observed livestock performance can be used to improve the system.

The prototype should not be treated as a replacement for professional animal-nutrition assessment or appropriate feed testing.

## 12. Limitations

- The public Render API is deployed, but the complete MCP tool workflow is not yet connected in the hosted application.
- A responding health endpoint does not demonstrate successful AI inference or correct feed formulation.
- Local Ollama configuration cannot be assumed to work from a cloud deployment.
- Feed composition varies by ingredient quality, processing method, location, and other factors.
- Ingredient prices can become outdated and require verification.
- Nutrient data and livestock requirements need appropriate validation for the intended species and production stages.
- The prototype has not been established as a validated commercial ration-formulation system.
- Recommendations should be reviewed by a qualified person before being applied to livestock.

## 13. Future Improvements

Planned development priorities include:

1. **Complete MCP integration:** make the nutrient, price, and assessment servers compatible with the deployed agent environment.
2. **Hosted model integration:** configure and test a reliable cloud-accessible model endpoint.
3. **Ration formulation:** integrate and validate least-cost optimization against relevant livestock nutrient requirements and ingredient constraints.
4. **Data engineering:** improve feed-data quality, provenance, versioning, and validation.
5. **Price verification:** establish workflows for updating ingredient prices and distinguishing verified prices from placeholders.
6. **Testing and evaluation:** add unit, integration, safety, and livestock-nutrition validation tests.
7. **Farmer-facing interface:** connect the agent to a WhatsApp-based workflow and explore SMS access for feature-phone users.
8. **Offline and low-connectivity support:** make the system more accessible in rural areas with limited internet connectivity.
9. **Human feedback:** capture farmer and extension-officer feedback to improve usability and advisory quality.
10. **Monitoring and security:** improve logging, error handling, access control, and deployment monitoring.

## 14. Project Structure

```text
balance-bora-agentic-ai/
├── app.py
├── balance_bora_agent.py
├── balance_bora_nutrient_mcp.py
├── balance_bora_price_mcp.py
├── balance_bora_assessment_mcp.py
├── Balance_Bora_Feed.db
├── Balance_Bora_Feed_Price_Template.xlsx
├── requirements.txt
├── Procfile
└── README.md
```

The files listed above describe the expected project structure; individual local or deployment environments may contain additional configuration files.

## 15. Contributing

Contributions that improve data quality, livestock-nutrition validation, MCP reliability, security, and farmer usability are welcome.

Before submitting changes:

- Do not commit API keys, secrets, local virtual environments, or audit logs.
- Test changes locally where possible.
- Document any changes to model configuration, MCP tools, or data schemas.
- Clearly distinguish tested functionality from planned functionality.

## 16. Project Links

- **Source code:** https://github.com/davidmarii/balance-bora-agentic-ai
- **Deployed API:** https://balance-bora-agentic-ai.onrender.com/
- **Interactive API documentation:** https://balance-bora-agentic-ai.onrender.com/docs
- **Balance Bora website:** https://davidmarii.github.io/Balance_Bora_website/

---

**Project status:** Early-stage prototype. The API is publicly deployed; full AI-agent and MCP integration, testing, and validation remain active development priorities.
