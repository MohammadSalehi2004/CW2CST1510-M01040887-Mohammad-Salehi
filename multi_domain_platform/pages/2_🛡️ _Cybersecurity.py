import streamlit as st
import pandas as pd
from datetime import datetime
from openai import OpenAI

from services.database_manager import DatabaseManager
from models.security_incident import SecurityIncident

# page config
st.set_page_config(page_title="Cybersecurity Dashboard", layout="wide")

# login check
if not st.session_state.get("logged_in"):
    st.error("Please log in")
    st.stop()

user = st.session_state.current_user
if user.get_role() not in ["cyber", "admin"]:
    st.warning("Access denied")
    st.stop()

# db manager (Week 11)
db = DatabaseManager("database/platform.db")
db.connect()

# AI client (unchanged logic)
client = OpenAI(api_key="key place")

# fetch incidents (Week 11 refactor)
rows = db.fetch_all("""
    SELECT id, date, incident_type, severity, status,
           description, reported_by, created_at
    FROM security_incidents
    ORDER BY id
""")

incidents: list[SecurityIncident] = []
for row in rows:
    incidents.append(
        SecurityIncident(
            incident_id=row[0],
            date=row[1],
            incident_type=row[2],
            severity=row[3],
            status=row[4],
            description=row[5],
            reported_by=row[6],
            created_at=row[7],
        )
    )

# convert to DataFrame for UI only
df = pd.DataFrame([{
    "id": i.get_id(),
    "date": i.get_date(),
    "incident_type": i.get_incident_type(),
    "severity": i.get_severity(),
    "status": i.get_status(),
    "description": i.get_description(),
    "reported_by": i.get_reported_by(),
    "created_at": i.get_created_at()
} for i in incidents])

# header
st.title("🔐 Cyber Operations Dashboard")
st.success(f"Welcome {user.get_username()} ({user.get_role()})")

# metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Incidents", len(df))
col2.metric("Critical", int((df["severity"] == "critical").sum()) if not df.empty else 0)
col3.metric("Open", int((df["status"] == "open").sum()) if not df.empty else 0)

st.divider()

tab1, tab2, tab3 = st.tabs(["💻 Incidents", "📊 Analytics", "🤖 AI Assistant"])

#incidents tab
with tab1:
    st.subheader("All Incidents")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No incidents found")

    st.subheader("Add Incident")
    with st.form("add_incident"):
        date = st.date_input("Date")
        itype = st.text_input("Incident Type")
        sev = st.selectbox("Severity", ["low", "medium", "high", "critical"])
        status = st.selectbox("Status", ["open", "investigating", "resolved", "closed"])
        desc = st.text_area("Description")
        reported = st.text_input("Reported By")

        if st.form_submit_button("Create"):
            db.execute_query("""
                INSERT INTO security_incidents
                (date, incident_type, severity, status, description, reported_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                date.strftime("%Y-%m-%d"),
                itype,
                sev,
                status,
                desc,
                reported,
                datetime.now().strftime("%Y-%m-%d")
            ))
            st.success("Incident added")
            st.rerun()

#chrat tab
with tab2:
    if not df.empty:
        st.bar_chart(df["severity"].value_counts())

# AI tab
with tab3:
    st.markdown("## 🤖 Cybersecurity AI Assistant")

    if "cyber_chat" not in st.session_state:
        st.session_state.cyber_chat = [
            {"role": "system", "content": "You are a cybersecurity expert assistant."}
        ]

    for msg in st.session_state.cyber_chat:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    user_input = st.chat_input("Ask the assistant...")
    if user_input:
        st.session_state.cyber_chat.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.cyber_chat
        )

        reply = response.choices[0].message.content
        st.session_state.cyber_chat.append({"role": "assistant", "content": reply})

        with st.chat_message("assistant"):
            st.write(reply)

# logout
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.rerun()
