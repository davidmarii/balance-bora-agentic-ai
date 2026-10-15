# Balance Bora — Agentic AI for Livestock Feed Advisory

**Track:** Agriculture  
**Project:** Climate-resilient livestock feed optimization and advisory for smallholder farmers in Kenya.

## Overview

Balance Bora is an early-stage agricultural advisory project designed to help smallholder livestock farmers make better-informed feed decisions using locally available ingredients, nutrient information, and market prices.

This repository contains a local agent prototype that connects an AI model to specialized tools through the **Model Context Protocol (MCP)**.

The prototype demonstrates how an AI agent can retrieve feed information, check price records, assess the completeness of formulation inputs, and prepare an advisory draft for human review.

## MCP integration

The agent connects to three MCP tool servers:

1. **Nutrient lookup** — retrieves recorded nutrient information for feed ingredients.
2. **Price lookup** — searches the local price workbook and filters out test-only price records.
3. **Input assessment** — checks the availability and completeness of information supplied for a feed advisory.

The agent uses the locally hosted `qwen2.5:3b` model through Ollama.

## Human-in-the-loop safeguards

The agent prepares a draft rather than automatically issuing a final feeding recommendation or placing an order.

The user can:

- Review the draft.
- Enter `APPROVE-DRAFT` to record approval of that exact draft.
- Enter `REJECT-DRAFT` to reject it.
- Press Enter to leave the draft pending.

Recording approval does not send a message, place an order, or replace professional nutritional review.

## Architecture

Farmer or operator request  
→ Local AI agent  
→ MCP tool servers  
→ Nutrient database, price workbook, and input assessment  
→ Draft advisory  
→ Human review and explicit approval

## Current status

This is an experimental local prototype, not a validated commercial feed formulation system.

- The agent and MCP tools run locally.
- Ollama must be installed and the model downloaded.
- The nutrient database and price workbook must be available and correctly configured.
- Nutrient units, analytical basis, data provenance, ingredient suitability, and current supplier prices require verification.
- The prototype should not be treated as proof that a ration meets an animal's nutritional requirements.
- The local CLI is not a publicly hosted agent demo.

## Repository contents

- `balance_bora_agent.py` — AI agent and human-review workflow.
- `balance_bora_nutrient_mcp.py` — nutrient lookup MCP server.
- `balance_bora_price_mcp.py` — feed price lookup MCP server.
- `balance_bora_assessment_mcp.py` — formulation-input assessment MCP server.
- `test_balance_bora_prices.py` — price lookup test.
- `Balance_Bora_Feed_Price_Template.xlsx` — price workbook template, subject to review before publication.

## Running locally

Requirements include Python, Ollama, and the Python dependencies required by the agent and MCP servers.

1. Install Ollama and download the model:

   ```bash
   ollama pull qwen2.5:3b
   ```

2. Install the project dependencies in separate environments as required by the agent and MCP servers.
3. Configure the local nutrient database and feed price workbook.
4. Start the agent using the project's configured Python environment:

   ```bash
   python balance_bora_agent.py
   ```

Exact dependency installation commands and database setup should be documented alongside the relevant source files before the project is considered reproducible.

## Demo

Existing Balance Bora website: https://davidmarii.github.io/Balance_Bora_website/

The website is a separate project and should not be assumed to demonstrate this repository's MCP workflow unless that integration is explicitly deployed and tested.

## Responsible use

This prototype is intended for research and demonstration. It does not replace a qualified animal nutritionist, laboratory analysis, verified supplier quotations, or farm-specific assessment.

## License

A license has not yet been selected. Reuse and redistribution permissions should be clarified before the project is presented as open source.
