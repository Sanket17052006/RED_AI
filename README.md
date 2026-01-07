#  RED AI - An Autonomous AI Agent

---
## 🔁 Current Workflow (Checkpoint 1)

User sends a message via an API request

FastAPI backend receives the request

OpenAI Chat Model processes the input

A conversational response is returned to the user

At this stage, the system behaves as a chatbot and does not yet perform autonomous actions or planning.

## 🧪 Checkpoint 1 – Current Implementation Status

✔ *Integrated OpenAI Chat Model* into the FastAPI backend
✔ System currently functions as a chat-based AI
✔ API endpoints tested locally using Postman
✔ Verified request–response flow and model integration

## 🔜 Next Objectives

Implement agentic logic using LangGraph

Add goal decomposition, planning, and decision-making

Integrate the agent with the frontend chat interface

Enhance system robustness and scalability

Prepare the application for deployment

## 📌 Project Overview

This project implements a code based AI agent capable of understanding high-level user goals, breaking them into actionable steps, making decisions, using external tools, and completing tasks end-to-end with minimal human intervention.

Unlike traditional chatbots, this system demonstrates **true agentic behavior** by combining reasoning, planning, memory, and tool usage within a single autonomous workflow.

This project is built for DECATHON 2026.
---

## 🎯 Key Capabilities

- Natural language goal understanding  
- Autonomous task decomposition and planning  
- Decision-making without step-by-step user instructions  
- Code-based tool usage (Email & Calendar)  
- Stateful memory for context retention  
- End-to-end task completion  
- Unified agent handling both chat and actions  

---

## 🧠 System Architecture Summary

- **Frontend** provides a simple chat-based interface for user interaction  
- **Backend (FastAPI)** hosts the agent runtime and exposes REST APIs  
- **LangGraph** acts as the agent brain, handling reasoning, planning, execution, and memory  
- **Tool APIs** enable real-world actions such as sending emails and creating calendar events  

LangGraph is embedded directly inside the backend and serves as the **central agent orchestrator**, ensuring full autonomy and code-level control.

---

## 🧰 Technology Stack

### Frontend
- HTML  
- CSS  
- JavaScript  

### Backend
- Python  
- FastAPI  

### Agentic AI Framework
- **LangGraph** (code-based agent orchestration)
  - Intent understanding  
  - Task planning & classification  
  - Decision making  
  - Tool invocation  
  - Result evaluation  
  - Memory management  

### AI / LLM Layer
- Large Language Model (LLM) accessed programmatically via LangGraph  

### Tool Integrations
- Email Service API (SMTP / Gmail API)  
- Google Calendar API  

### Memory & State
- In-memory or database-backed state  
- Optional vector store for contextual memory  

---

## 🔁 Agent Workflow (High-Level)

1. User submits a message or goal through the chat interface  
2. FastAPI forwards the request to the LangGraph agent  
3. The agent:
   - Understands the intent  
   - Breaks the goal into steps  
   - Decides whether a tool is required  
   - Executes actions autonomously  
   - Evaluates results  
   - Updates memory  
4. Final response or confirmation is returned to the user  

The same agent handles both **normal conversational responses** and **autonomous task execution**.

---

## ✨ Example Agent Actions

- Sending emails based on user intent  
- Creating calendar events from natural language requests  
- Responding conversationally when no action is required  

---
👥 Team Members

1.Sanket Srivastava
2.Shoumik Shourya
3.Vikas Sharma
4.Ved Prakash
5.Vivek Kumar


---

## 🏁 Conclusion

This project demonstrates a practical and scalable approach to building **autonomous agentic AI systems** using modern, code-first frameworks. By embedding LangGraph directly within a FastAPI backend, the system achieves high autonomy, clarity of reasoning, and full compliance with the hackathon requirements.
