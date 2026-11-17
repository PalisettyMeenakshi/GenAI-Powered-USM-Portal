GenAI-Powered Unified Service Management (USM) Portal

Project Overview

The GenAI-Powered Unified Service Management (USM) Portal is a lightweight IT Helpdesk Assistant built using Python, Streamlit, and SQLite.

It helps employees report IT issues, enables administrators to manage and assign tickets, and allows IT support agents to handle assigned incidents.

The application includes optional Google Gemini API integration for AI-based issue analysis, with a rule-based fallback when the AI service is unavailable.

Project Scope: This is an academic and interview demonstration prototype, not a complete enterprise USM platform.

Key Features

1. Role-Based Demo Access

The application provides three demo roles:

Employee: Creates IT support tickets and views personal ticket history.

IT Administrator: Views the dashboard, manages all tickets, assigns support agents, monitors SLAs, and deletes tickets.

IT Support Agent: Views tickets assigned to the selected agent and updates ticket status.

2. Ticket Management

Create IT incident tickets.

Generate unique incident IDs.

Classify issues into Network, Hardware, Software, and Access Management.

Assign ticket priority.

Generate issue summaries and suggested resolutions.

Track Open, In Progress, and Resolved statuses.

3. Agent Assignment

Administrators assign tickets to appropriate support agents.

Agents can view their assigned tickets.

Ticket assignments are stored in SQLite.

4. SLA Management

Define first-response and resolution targets based on ticket priority.

Track SLA deadlines.

Display SLA states such as Within SLA, At Risk, Breached, and Completed.

Monitor SLA performance through the administrator dashboard.

The SLA targets are demonstration values and use calendar hours.

5. Dashboard and Analytics

Total ticket count.

Open tickets.

In-progress tickets.

Resolved tickets.

SLA breach and at-risk indicators.

Ticket analytics and charts.

6. Employee Ticket History

Employees can search and view their previously submitted tickets using their name.

7. Database Persistence

SQLite stores ticket information so records remain available after restarting the application.

8. Optional Gemini AI Integration

When configured and available, Gemini analyzes IT issues and generates category, priority, summary, and resolution suggestions.

If the Gemini service is unavailable, the application uses rule-based fallback analysis.

Technology Stack

Technology

Purpose

Python

Application logic

Streamlit

Web application interface

SQLite

Ticket database

Google GenAI SDK

Optional Gemini AI integration

python-dotenv

Environment variable management

Project Structure

AI-Powered IT Helpdesk Assistant/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── .env
└── tickets.db

Note:

.env contains the private Gemini API key and must not be uploaded to GitHub.

tickets.db contains local demonstration records and should not be uploaded.

The database is created automatically when the application runs.

Installation and Setup

1. Install Python

Python 3.10 or later is recommended.

Check the installation:

python --version

2. Install Dependencies

Open the project folder in VS Code and run:

python -m pip install -r requirements.txt

3. Configure Gemini API (Optional)

Create a .env file in the project folder:

GEMINI_API_KEY=your_private_api_key

Never share or upload your actual API key.

4. Run the Application

python -m streamlit run app.py

Open the local URL displayed in the terminal, normally:

http://localhost:8501

Keep the terminal running while using the application.

Application Workflow

Employee selects the Employee role.

Employee enters their name and submits an IT issue.

The system generates an incident ticket.

The system analyzes and classifies the issue.

Administrator reviews the ticket and assigns it to a support agent.

The assigned agent views the ticket and updates its status.

The application tracks SLA deadlines.

Employees can view their ticket history.

Administrators monitor ticket statistics through the dashboard.

Database Information

The application uses SQLite and stores ticket information in tickets.db.

Ticket records include:

Ticket ID

Employee name

Issue description

Category and priority

Summary and suggested resolution

Ticket status

Assigned support agent

Creation timestamp

SLA deadlines and tracking timestamps

Important Notes and Limitations

Role selection is a demonstration mechanism, not secure authentication.

The application does not currently implement production-grade user accounts, password verification, or enterprise access control.

Employee history uses name-based lookup.

Gemini functionality depends on API availability and a valid configuration. If the API request fails, rule-based fallback analysis is used.

Rule-based classification uses keyword matching and is not a trained machine-learning model.

SLA targets are illustrative calendar-hour values, not universal industry standards.

The application is designed as a local prototype and is not hardened for enterprise multi-user deployment.

Ticket deletion permanently removes records from the local database.

Future Enhancements

Secure authentication and password management.

Production-grade role-based access control.

Email and in-app notifications.

SLA escalation and audit logging.

Knowledge-base integration using Retrieval-Augmented Generation (RAG).

Production database and cloud deployment.

Note: The Gemini API integration is optional. Describe live AI functionality according to what has actually been verified during testing