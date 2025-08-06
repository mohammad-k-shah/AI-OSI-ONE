# 🧠 Product Requirements Document (PRD)

## Product Name
**OSI ONE AGENT** – AI-Powered Desktop Assistant for OSI Digital Engineers

---

## 1. Product Vision

"OSI ONE AGENT" is an AI-powered **desktop assistant** that runs locally on OSI Digital office laptops. It allows engineers to perform routine tasks via **natural language** (NLP), streamlining workflows and eliminating repetitive manual operations across platforms like OSI One, Azure DevOps, and Microsoft Teams.

---

## 2. Core Functional Requirements

### ✅ OSI One Timesheet Automation
- Retrieve past entries and submit timesheets via browser automation (Playwright).
- Support summarization of weekly activity from DevOps/Calendar for auto-fill.

### ✅ Azure DevOps Integration
- Fetch assigned tasks, user stories, and pull requests.
- Perform full CRUD operations on Azure Boards and Git Repositories.
- Support natural language interaction (e.g., “Show tasks for this sprint”).

### ✅ Microsoft Teams Assistant
- Read user's calendar events.
- Draft/send messages to specific users (via Graph API if available).
- Schedule meetings if possible.

### ✅ NLP Interface
- Accept natural language commands via terminal or UI.
- Classify user intent and route to appropriate agent/tool.

---

## 3. Non-Functional Requirements

- **Platform:** Runs locally on Windows (office laptop).
- **Security:** No sensitive data stored; tokens managed securely.
- **Performance:** Respond within 2-3 seconds per query.
- **Scalability:** Modular design to support future tools/integrations.

---

## 4. Access Constraints

| Platform         | Access Level         | Workaround Strategy                      |
|------------------|----------------------|------------------------------------------|
| OSI One Portal   | User-only, no API    | Use Playwright for web automation        |
| Microsoft Teams  | No admin access      | Use Graph API with delegated token       |
| Azure DevOps     | Full access via API  | Direct REST API integration              |

---

## 5. Target Users

- Engineers, Tech Leads, Project Managers working at OSI Digital.
- Users with OSI email credentials and Azure DevOps access.

---

## 6. MVP Scope (Milestone 1)

### 🎯 Goals:
- Support 3 use cases end-to-end:
  - Fetch current DevOps tasks
  - Autofill OSI One timesheet using last week’s task + meeting summary
  - Read upcoming calendar events

### 👨‍💻 User Prompt Examples:
- “Fill my timesheet based on last week’s PRs.”
- “What are my assigned tasks for today?”
- “Do I have any meetings with John this week?”

---

## 7. Tech Stack Overview

| Layer         | Tool / Framework                   |
|---------------|-------------------------------------|
| NLP           | OpenAI GPT-4 API / Ollama (Llama3) |
| Agent Runtime | LangChain                          |
| Automation    | Selenium WebDriver (MVP) / Playwright (Future) |
| DevOps API    | Azure DevOps REST API              |
| Calendar API  | Microsoft Graph API (delegated)    |
| UI (Optional) | PyQt5 / Electron                   |

---

## 8. Risks & Mitigations

| Risk                                      | Mitigation                             |
|-------------------------------------------|----------------------------------------|
| Teams Bot Registration Not Allowed        | Simulate chat/notification via Graph API |
| OSI One Changes UI Frequently             | Use robust selectors + retraining      |
| LLM Cost/API Rate Limit                   | Use local LLM for dev, OpenAI for prod |
| User Data Privacy                         | Store no data locally, secure tokens   |

---

## 9. Success Metrics

- ⏱️ 50% time reduction in weekly task completion
- ✅ 100% accurate timesheet submission via agent
- 📈 Positive feedback from pilot group (5–10 engineers)

---

## 10. Future Enhancements

- Add Slack/Outlook/Zoom support
- Use RAG (retrieval augmented generation) with OSI docs
- Add GitHub and JIRA plugins
- Full MS Teams bot deployment post-IT approval
