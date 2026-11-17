import os
import json
import uuid
import sqlite3
from datetime import datetime, timedelta

import streamlit as st
from dotenv import load_dotenv
from google import genai

# ==================================================
# 1. CONFIGURATION
# ==================================================

load_dotenv()

st.set_page_config(
    page_title="GenAI USM Portal",
    page_icon="🎫",
    layout="wide"
)


# ==================================================
# PROFESSIONAL UI THEME
# ==================================================

st.markdown("""
<style>
    :root {
        --ink: #17243a;
        --muted: #64748b;
        --accent: #2563eb;
        --accent-dark: #1d4ed8;
        --surface: #ffffff;
        --line: #e5eaf2;
    }

    .stApp {
        background: #f4f7fb;
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: rgba(244, 247, 251, 0.92);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #10233f 0%, #172f50 100%);
        border-right: 1px solid #203b5e;
    }

    [data-testid="stSidebar"] * {
        color: #edf4ff !important;
    }

    /* Keep text readable inside light sidebar form controls. */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {
        color: #17243a !important;
        -webkit-text-fill-color: #17243a !important;
        background-color: #ffffff !important;
        caret-color: #17243a !important;
    }

    [data-testid="stSidebar"] input::placeholder,
    [data-testid="stSidebar"] textarea::placeholder {
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #17243a !important;
    }

    [data-testid="stSidebar"] [role="listbox"] * {
        color: #17243a !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 9px 12px;
        border-radius: 9px;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(255,255,255,0.10);
    }

    .block-container {
        max-width: 1440px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #17243a;
        letter-spacing: -0.025em;
    }

    h1 {
        font-weight: 800 !important;
        font-size: 2.15rem !important;
    }

    h2, h3 {
        font-weight: 700 !important;
    }

    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e5eaf2;
        border-radius: 15px;
        padding: 18px 20px;
        box-shadow: 0 4px 16px rgba(23, 36, 58, 0.045);
    }

    [data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: #17243a !important;
        font-weight: 800;
    }

    div[data-testid="stForm"],
    div[data-testid="stExpander"] {
        background: #ffffff;
        border: 1px solid #e5eaf2;
        border-radius: 14px;
        box-shadow: 0 3px 12px rgba(23, 36, 58, 0.035);
    }

    div[data-testid="stForm"] {
        padding: 18px;
    }

    div[data-testid="stExpander"] summary {
        font-weight: 650;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: 9px;
        font-weight: 650;
        min-height: 2.65rem;
        border: 1px solid #cbd8ea;
        transition: all 0.15s ease;
    }

    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {
        background: #2563eb;
        border-color: #2563eb;
        color: white;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        border-color: #2563eb;
        color: #1d4ed8;
    }

    input, textarea, [data-baseweb="select"] > div {
        border-radius: 9px !important;
    }

    [data-testid="stAlert"] {
        border-radius: 11px;
    }

    hr {
        border-color: #e3eaf3;
    }

    .hero-panel {
        background: linear-gradient(115deg, #102b4e 0%, #1d4f85 62%, #2878a8 100%);
        padding: 27px 30px;
        border-radius: 18px;
        color: #ffffff;
        margin: 0 0 22px 0;
        box-shadow: 0 10px 28px rgba(16, 43, 78, 0.15);
    }

    .hero-panel h2 {
        color: #ffffff !important;
        margin: 0 0 7px 0;
        font-size: 1.65rem;
    }

    .hero-panel p {
        color: #dbeafe !important;
        margin: 0;
        font-size: 0.98rem;
    }

    .section-kicker {
        color: #2563eb;
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.11em;
        text-transform: uppercase;
        margin-bottom: 5px;
    }

    .small-note {
        color: #64748b;
        font-size: 0.9rem;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 1rem 2rem 1rem;
        }
        h1 {
            font-size: 1.7rem !important;
        }
        .hero-panel {
            padding: 21px;
        }
    }
</style>
""", unsafe_allow_html=True)

DB_NAME = "tickets.db"
MODEL_NAME = "gemini-3.8-flash"

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


# ==================================================
# 2. DATABASE MANAGEMENT
# ==================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


SUPPORT_AGENTS = [
    "Unassigned",
    "Rahul - Network Support",
    "Priya - Hardware Support",
    "Arjun - Software Support",
    "Sneha - Access Support",
]

# Example calendar-hour targets: (first-response hours, resolution hours).
SLA_TARGETS = {
    "Critical": (0.25, 2),
    "High": (0.5, 4),
    "Medium": (2, 8),
    "Low": (4, 24),
}


def get_sla_deadlines(priority, created_at):
    response_hours, resolution_hours = SLA_TARGETS.get(
        priority, SLA_TARGETS["Medium"]
    )
    return (
        (created_at + timedelta(hours=response_hours)).strftime("%Y-%m-%d %H:%M:%S"),
        (created_at + timedelta(hours=resolution_hours)).strftime("%Y-%m-%d %H:%M:%S"),
    )


def get_sla_state(ticket):
    now = datetime.now()
    try:
        response_due = datetime.strptime(ticket["response_due"], "%Y-%m-%d %H:%M:%S")
        resolution_due = datetime.strptime(ticket["resolution_due"], "%Y-%m-%d %H:%M:%S")
        created_at = datetime.strptime(ticket["created"], "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return "SLA dates unavailable"

    response_breached = (
        ticket["status"] == "Open"
        and not ticket.get("first_response_at")
        and now > response_due
    )
    resolution_breached = (
        ticket["status"] != "Resolved" and now > resolution_due
    )

    if response_breached or resolution_breached:
        return "Breached"
    if ticket["status"] == "Resolved":
        return "Completed"

    total_window = max((resolution_due - created_at).total_seconds(), 1)
    remaining = (resolution_due - now).total_seconds()
    if remaining <= total_window * 0.2:
        return "At Risk"
    return "Within SLA"


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                employee TEXT NOT NULL,
                issue TEXT NOT NULL,
                category TEXT,
                priority TEXT,
                summary TEXT,
                resolution TEXT,
                source TEXT,
                status TEXT,
                created TEXT,
                assigned_to TEXT,
                response_due TEXT,
                resolution_due TEXT,
                first_response_at TEXT,
                resolved_at TEXT
            )
        """)

        # Add new fields safely to an existing tickets.db database.
        existing = {
            row[1] for row in conn.execute("PRAGMA table_info(tickets)").fetchall()
        }
        additions = {
            "assigned_to": "TEXT",
            "response_due": "TEXT",
            "resolution_due": "TEXT",
            "first_response_at": "TEXT",
            "resolved_at": "TEXT",
        }
        for column, column_type in additions.items():
            if column not in existing:
                conn.execute(f"ALTER TABLE tickets ADD COLUMN {column} {column_type}")

        # Backfill SLA deadlines for older tickets.
        rows = conn.execute(
            "SELECT id, priority, created, response_due, resolution_due FROM tickets"
        ).fetchall()
        for ticket_id, priority, created, response_due, resolution_due in rows:
            if created and (not response_due or not resolution_due):
                try:
                    created_at = datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
                    response_hours, resolution_hours = SLA_TARGETS.get(
                        priority, SLA_TARGETS["Medium"]
                    )
                    conn.execute("""
                        UPDATE tickets
                        SET response_due = COALESCE(response_due, ?),
                            resolution_due = COALESCE(resolution_due, ?)
                        WHERE id = ?
                    """, (
                        (created_at + timedelta(hours=response_hours)).strftime("%Y-%m-%d %H:%M:%S"),
                        (created_at + timedelta(hours=resolution_hours)).strftime("%Y-%m-%d %H:%M:%S"),
                        ticket_id,
                    ))
                except (TypeError, ValueError):
                    pass


def save_ticket(ticket):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO tickets
            (id, employee, issue, category, priority,
             summary, resolution, source, status, created,
             assigned_to, response_due, resolution_due,
             first_response_at, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket["id"], ticket["employee"], ticket["issue"],
            ticket["category"], ticket["priority"], ticket["summary"],
            ticket["resolution"], ticket["source"], ticket["status"],
            ticket["created"], ticket.get("assigned_to"),
            ticket.get("response_due"), ticket.get("resolution_due"),
            ticket.get("first_response_at"), ticket.get("resolved_at"),
        ))


def get_tickets():
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM tickets ORDER BY created DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def update_ticket_status(ticket_id, status):
    now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        if status == "Open":
            conn.execute(
                "UPDATE tickets SET status = ? WHERE id = ?",
                (status, ticket_id)
            )
        elif status == "Resolved":
            conn.execute("""
                UPDATE tickets
                SET status = ?,
                    first_response_at = COALESCE(first_response_at, ?),
                    resolved_at = ?
                WHERE id = ?
            """, (status, now_text, now_text, ticket_id))
        else:
            conn.execute("""
                UPDATE tickets
                SET status = ?,
                    first_response_at = COALESCE(first_response_at, ?),
                    resolved_at = NULL
                WHERE id = ?
            """, (status, now_text, ticket_id))


def update_ticket_assignee(ticket_id, assigned_to):
    with get_connection() as conn:
        conn.execute(
            "UPDATE tickets SET assigned_to = ? WHERE id = ?",
            (None if assigned_to == "Unassigned" else assigned_to, ticket_id)
        )


def delete_ticket(ticket_id):
    """Delete one ticket permanently from the SQLite database."""
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM tickets WHERE id = ?",
            (ticket_id,)
        )


def delete_all_tickets():
    """Delete every ticket permanently from the SQLite database."""
    with get_connection() as conn:
        conn.execute("DELETE FROM tickets")


initialize_database()


# ==================================================
# 3. FALLBACK ISSUE CLASSIFICATION
# ==================================================

def fallback_analysis(issue):

    text = issue.lower()

    if any(word in text for word in [
        "wifi", "internet", "network", "connection"
    ]):
        category = "Network"
        resolution = (
            "Check Wi-Fi settings, restart the router "
            "and reconnect to the network."
        )

    elif any(word in text for word in [
        "laptop", "keyboard", "mouse", "monitor", "hardware"
    ]):
        category = "Hardware"
        resolution = (
            "Check device connections and restart "
            "the affected hardware."
        )

    elif any(word in text for word in [
        "password", "login", "access", "account"
    ]):
        category = "Access Management"
        resolution = (
            "Verify your account credentials and "
            "request a password reset if necessary."
        )

    else:
        category = "Software"
        resolution = (
            "Restart the application and check "
            "for available software updates."
        )

    priority = "High" if any(word in text for word in [
        "urgent", "critical", "not working", "down"
    ]) else "Medium"

    return {
        "category": category,
        "priority": priority,
        "summary": issue[:150],
        "resolution": resolution,
        "source": "Fallback analysis",
        "error": None
    }


# ==================================================
# 4. GEMINI AI ANALYSIS
# ==================================================

def analyze_issue(issue, use_gemini):

    if not use_gemini:
        return fallback_analysis(issue)

    if not client:
        result = fallback_analysis(issue)
        result["error"] = (
            "GEMINI_API_KEY was not found. "
            "Please check your .env file."
        )
        return result

    try:

        prompt = f"""
        You are an IT Service Management assistant.

        Analyze the following employee IT issue:

        {issue}

        Return ONLY valid JSON with these fields:

        category: Choose one of Network, Hardware,
                  Software, Access Management.

        priority: Choose one of Low, Medium, High, Critical.

        summary: A short summary of the problem.

        resolution: Provide practical troubleshooting steps.

        Do not include markdown or code fences.
        """

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        response_text = response.text.strip()

        if response_text.startswith("```"):
            response_text = response_text.replace("```json", "")
            response_text = response_text.replace("```", "").strip()

        result = json.loads(response_text)

        categories = [
            "Network",
            "Hardware",
            "Software",
            "Access Management"
        ]

        priorities = [
            "Low",
            "Medium",
            "High",
            "Critical"
        ]

        if result.get("category") not in categories:
            raise ValueError("Gemini returned an invalid category.")

        if result.get("priority") not in priorities:
            raise ValueError("Gemini returned an invalid priority.")

        return {
            "category": result["category"],
            "priority": result["priority"],
            "summary": result.get("summary", issue),
            "resolution": result.get(
                "resolution",
                "Contact the IT support team."
            ),
            "source": "Gemini AI",
            "error": None
        }

    except Exception as error:

        result = fallback_analysis(issue)

        result["error"] = (
            f"{type(error).__name__}: {str(error)}"
        )

        return result


# ==================================================
# 5. SIDEBAR NAVIGATION
# ==================================================

st.sidebar.title("🎫 USM Portal")
st.sidebar.caption("Unified Service Management")

# Demo role selector (not production authentication).
role = st.sidebar.selectbox(
    "Demo Login Role",
    ["Employee", "IT Support Agent", "IT Administrator"]
)

current_employee = ""
current_agent = ""
if role == "Employee":
    current_employee = st.sidebar.text_input("Employee name", key="demo_employee").strip()
elif role == "IT Support Agent":
    current_agent = st.sidebar.selectbox(
        "Agent account",
        SUPPORT_AGENTS[1:]
    )

if role == "Employee":
    allowed_pages = ["Create Ticket", "Employee History"]
elif role == "IT Support Agent":
    allowed_pages = ["My Assigned Tickets"]
else:
    allowed_pages = ["Dashboard", "Manage Tickets"]

page = st.sidebar.radio("Navigation", allowed_pages)

st.sidebar.caption(f"Active role: {role}")
st.sidebar.divider()

use_gemini = st.sidebar.toggle(
    "Enable Gemini AI",
    value=False
)

if use_gemini and not client:
    st.sidebar.error("Gemini API key not found.")

st.sidebar.divider()

st.sidebar.caption("GenAI-Powered IT Support System")


# ==================================================
# 6. LOAD DATABASE RECORDS
# ==================================================

tickets = get_tickets()

total = len(tickets)

open_count = sum(
    t["status"] == "Open" for t in tickets
)

progress_count = sum(
    t["status"] == "In Progress" for t in tickets
)

resolved_count = sum(
    t["status"] == "Resolved" for t in tickets
)

breached_count = sum(get_sla_state(t) == "Breached" for t in tickets)
at_risk_count = sum(get_sla_state(t) == "At Risk" for t in tickets)


# ==================================================
# 7. DASHBOARD
# ==================================================

if page == "Dashboard":

    st.markdown("""
    <div class="hero-panel">
        <div class="section-kicker" style="color:#bfdbfe;">SERVICE OPERATIONS</div>
        <h2>Service Management Dashboard</h2>
        <p>Monitor incidents, follow ticket progress, and get a quick view of support activity.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-kicker">AT A GLANCE</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Tickets", total)
    c2.metric("Open Tickets", open_count)
    c3.metric("In Progress", progress_count)
    c4.metric("Resolved", resolved_count)

    s1, s2 = st.columns(2)
    s1.metric("SLA Breached", breached_count)
    s2.metric("SLA At Risk", at_risk_count)

    st.divider()

    st.markdown('<div class="section-kicker">PERFORMANCE OVERVIEW</div>', unsafe_allow_html=True)
    st.subheader("Ticket Analytics")

    col1, col2 = st.columns(2)

    with col1:

        st.write("**Tickets by Status**")

        status_data = {
            "Open": open_count,
            "In Progress": progress_count,
            "Resolved": resolved_count
        }

        st.bar_chart(status_data)

    with col2:

        st.write("**Tickets by Priority**")

        priority_data = {
            priority: sum(
                t["priority"] == priority for t in tickets
            )
            for priority in [
                "Critical", "High", "Medium", "Low"
            ]
        }

        st.bar_chart(priority_data)

    st.divider()

    st.markdown('<div class="section-kicker">LATEST ACTIVITY</div>', unsafe_allow_html=True)
    st.subheader("Recent Tickets")

    if tickets:

        for ticket in tickets[:5]:

            with st.expander(
                f"{ticket['id']} | "
                f"{ticket['employee']} | "
                f"{ticket['status']}"
            ):

                st.write("**Issue:**", ticket["issue"])
                st.write("**Category:**", ticket["category"])
                st.write("**Priority:**", ticket["priority"])
                st.write("**Assigned Agent:**", ticket.get("assigned_to") or "Unassigned")
                st.write("**SLA Status:**", get_sla_state(ticket))
                st.write("**Resolution Due:**", ticket.get("resolution_due") or "Not available")
                st.write("**Resolution:**", ticket["resolution"])

    else:
        st.info("No tickets available yet.")


# ==================================================
# 8. CREATE TICKET
# ==================================================

elif page == "Create Ticket":

    st.markdown("""
    <div class="hero-panel">
        <div class="section-kicker" style="color:#bfdbfe;">NEW SERVICE REQUEST</div>
        <h2>Create an IT Support Ticket</h2>
        <p>Describe the issue clearly so the support team can classify and resolve it.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("ticket_form"):

        if role == "Employee":
            st.text_input("Employee Name", value=current_employee, disabled=True)
            employee = current_employee
        else:
            employee = st.text_input("Employee Name")

        issue = st.text_area(
            "Describe your IT issue",
            height=130
        )

        submitted = st.form_submit_button(
            "Submit Ticket"
        )

        if submitted:

            if employee.strip() and issue.strip():

                with st.spinner(
                    "Analyzing the IT issue..."
                ):

                    analysis = analyze_issue(
                        issue,
                        use_gemini
                    )

                created_at = datetime.now()
                created_text = created_at.strftime("%Y-%m-%d %H:%M:%S")
                response_due, resolution_due = get_sla_deadlines(
                    analysis["priority"], created_at
                )

                ticket = {
                    "id": "INC-" + uuid.uuid4().hex[:6].upper(),
                    "employee": employee.strip(),
                    "issue": issue.strip(),
                    "category": analysis["category"],
                    "priority": analysis["priority"],
                    "summary": analysis["summary"],
                    "resolution": analysis["resolution"],
                    "source": analysis["source"],
                    "status": "Open",
                    "created": created_text,
                    "assigned_to": None,
                    "response_due": response_due,
                    "resolution_due": resolution_due,
                    "first_response_at": None,
                    "resolved_at": None,
                }

                save_ticket(ticket)

                if analysis["error"]:
                    st.error(
                        "Gemini API Error: "
                        + analysis["error"]
                    )

                st.success(
                    f"Ticket created successfully: {ticket['id']}"
                )

                st.write("**Category:**", ticket["category"])
                st.write("**Priority:**", ticket["priority"])
                st.write("**Summary:**", ticket["summary"])
                st.write(
                    "**Suggested Resolution:**",
                    ticket["resolution"]
                )

                st.info(
                    "Analysis method: " + ticket["source"]
                )

                st.rerun()

            else:
                st.warning(
                    "Please enter employee name and issue description."
                )


# ==================================================
# 9. MANAGE TICKETS
# ==================================================

elif page in ["Manage Tickets", "My Assigned Tickets"]:

    st.markdown("""
    <div class="hero-panel">
        <div class="section-kicker" style="color:#bfdbfe;">SUPPORT WORKSPACE</div>
        <h2>Ticket Management</h2>
        <p>Search incidents, narrow the list with filters, update progress, and manage records.</p>
    </div>
    """, unsafe_allow_html=True)

    if role == "IT Support Agent":
        st.info(f"Signed in as {current_agent}. You can update status only for tickets assigned to you.")
        search = ""
    else:
        search = st.text_input(
            "🔍 Search by Ticket ID or Employee Name"
        )

    col1, col2, col3 = st.columns(3)

    with col1:

        priority_filter = st.selectbox(
            "Priority",
            ["All", "Low", "Medium", "High", "Critical"]
        )

    with col2:

        status_filter = st.selectbox(
            "Status",
            ["All", "Open", "In Progress", "Resolved"]
        )

    with col3:

        category_filter = st.selectbox(
            "Category",
            [
                "All",
                "Network",
                "Hardware",
                "Software",
                "Access Management"
            ]
        )

    filtered_tickets = tickets
    if role == "IT Support Agent":
        filtered_tickets = [t for t in filtered_tickets if (t.get("assigned_to") or "") == current_agent]

    if search:

        filtered_tickets = [
            t for t in filtered_tickets
            if search.lower() in t["id"].lower()
            or search.lower() in t["employee"].lower()
        ]

    if priority_filter != "All":

        filtered_tickets = [
            t for t in filtered_tickets
            if t["priority"] == priority_filter
        ]

    if status_filter != "All":

        filtered_tickets = [
            t for t in filtered_tickets
            if t["status"] == status_filter
        ]

    if category_filter != "All":

        filtered_tickets = [
            t for t in filtered_tickets
            if t["category"] == category_filter
        ]

    st.write(
        f"Showing {len(filtered_tickets)} of {total} tickets"
    )

    if filtered_tickets:

        for ticket in filtered_tickets:

            with st.expander(
                f"{ticket['id']} | "
                f"{ticket['employee']} | "
                f"{ticket['priority']} Priority"
            ):

                st.write("**Issue:**", ticket["issue"])
                st.write("**Category:**", ticket["category"])
                st.write("**Priority:**", ticket["priority"])
                st.write("**Summary:**", ticket["summary"])
                st.write("**Resolution:**", ticket["resolution"])
                st.write("**Created:**", ticket["created"])
                st.write("**Assigned Agent:**", ticket.get("assigned_to") or "Unassigned")

                sla_state = get_sla_state(ticket)
                if sla_state == "Breached":
                    st.error("SLA Status: Breached")
                elif sla_state == "At Risk":
                    st.warning("SLA Status: At Risk")
                elif sla_state == "Completed":
                    st.success("SLA Status: Completed")
                else:
                    st.info("SLA Status: " + sla_state)

                st.write("**First Response Due:**", ticket.get("response_due") or "Not available")
                st.write("**Resolution Due:**", ticket.get("resolution_due") or "Not available")

                st.caption(
                    "Analysis method: " + ticket["source"]
                )

                if role == "IT Administrator":
                    assigned_agent = ticket.get("assigned_to") or "Unassigned"
                    agent_options = SUPPORT_AGENTS.copy()
                    if assigned_agent not in agent_options:
                        agent_options.insert(0, assigned_agent)
                    selected_agent = st.selectbox(
                        "Assign to IT Support Agent",
                        agent_options,
                        index=agent_options.index(assigned_agent),
                        key=f"assignee_{ticket['id']}"
                    )
                    if selected_agent != assigned_agent:
                        update_ticket_assignee(ticket["id"], selected_agent)
                        st.rerun()

                statuses = [
                    "Open",
                    "In Progress",
                    "Resolved"
                ]

                new_status = st.selectbox(
                    "Update Status",
                    statuses,
                    index=statuses.index(ticket["status"]),
                    key=ticket["id"]
                )

                if new_status != ticket["status"]:

                    update_ticket_status(
                        ticket["id"],
                        new_status
                    )

                    st.rerun()

    else:

        st.info(
            "No tickets match your search or filters."
        )

    # --------------------------------------------------
    # DELETE TICKETS (administrator only)
    # --------------------------------------------------

    if role == "IT Administrator":
        st.divider()
        st.subheader("🗑️ Delete Tickets")
        st.warning(
            "Deleted tickets are permanently removed from the database "
            "and cannot be recovered."
        )

        if tickets:
            ticket_options = [
                f"{ticket['id']} — {ticket['employee']} "
                f"({ticket['status']})"
                for ticket in tickets
            ]
            ticket_id_by_label = {
                f"{ticket['id']} — {ticket['employee']} "
                f"({ticket['status']})": ticket["id"]
                for ticket in tickets
            }

            with st.form("delete_individual_ticket_form"):
                st.markdown("**Delete an individual ticket**")
                selected_ticket = st.selectbox(
                    "Select the ticket to delete",
                    ticket_options,
                    key="delete_ticket_selection"
                )
                confirm_one = st.checkbox(
                    "I understand this ticket will be permanently deleted.",
                    key="confirm_delete_one"
                )
                delete_one_submitted = st.form_submit_button(
                    "Delete Selected Ticket",
                    type="primary"
                )

                if delete_one_submitted:
                    if confirm_one:
                        selected_id = ticket_id_by_label[selected_ticket]
                        delete_ticket(selected_id)
                        st.success(f"Ticket {selected_id} was deleted.")
                        st.rerun()
                    else:
                        st.error("Please confirm before deleting the ticket.")

            with st.form("delete_all_tickets_form"):
                st.markdown("**Delete all tickets**")
                confirm_all = st.checkbox(
                    "I understand this will permanently delete ALL tickets.",
                    key="confirm_delete_all"
                )
                delete_all_submitted = st.form_submit_button(
                    "Delete All Tickets"
                )

                if delete_all_submitted:
                    if confirm_all:
                        delete_all_tickets()
                        st.success("All tickets have been deleted.")
                        st.rerun()
                    else:
                        st.error("Please confirm before deleting all tickets.")
        else:
            st.info("There are no tickets to delete.")


# ==================================================
# 10. EMPLOYEE TICKET HISTORY
# ==================================================

elif page == "Employee History":

    st.markdown("""
    <div class="hero-panel">
        <div class="section-kicker" style="color:#bfdbfe;">EMPLOYEE SERVICES</div>
        <h2>Employee Ticket History</h2>
        <p>Review the support requests previously submitted by an employee.</p>
    </div>
    """, unsafe_allow_html=True)

    if role == "Employee":
        history_name = current_employee
        st.info(f"Showing ticket history for {current_employee or 'your account'}.")
    else:
        history_name = st.text_input("Enter Employee Name")

    if history_name.strip():

        employee_tickets = [
            t for t in tickets
            if t["employee"].strip().lower()
            == history_name.strip().lower()
        ]

        if employee_tickets:

            st.success(
                f"Found {len(employee_tickets)} tickets."
            )

            for ticket in employee_tickets:

                with st.expander(
                    f"{ticket['id']} | "
                    f"{ticket['status']} | "
                    f"{ticket['priority']}"
                ):

                    st.write("**Issue:**", ticket["issue"])
                    st.write("**Category:**", ticket["category"])
                    st.write("**Priority:**", ticket["priority"])
                    st.write("**Summary:**", ticket["summary"])
                    st.write("**Resolution:**", ticket["resolution"])
                    st.write("**Current Status:**", ticket["status"])
                    st.write("**Assigned Agent:**", ticket.get("assigned_to") or "Unassigned")
                    st.write("**SLA Status:**", get_sla_state(ticket))
                    st.write("**Resolution Due:**", ticket.get("resolution_due") or "Not available")
                    st.write("**Created:**", ticket["created"])

        else:

            st.info(
                "No ticket history found for this employee."
            )

    else:

        st.caption(
            "Enter an employee name to view their ticket history."
        )
