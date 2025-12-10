import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from app.data.incidents import (
    get_incidents,
    add_incident,
    change_incident_status,
    remove_incident
)
from openai import OpenAI

#setting up page information
st.set_page_config(page_title="Cybersecurity Dashboard", layout="wide")

# variable for key
OPENAI_API_KEY = "key place" #either mine or the bob one
client = OpenAI(api_key=OPENAI_API_KEY)

#checking for users to login or register
if not st.session_state.get("logged_in"):
    st.error("Please log in to view this page.")
    st.stop()
if st.session_state.role not in ["cyber", "admin"]:
    st.warning("You do not have permission to access this dashboard.")
    st.stop()

# page info and welcome
st.title("Cyber Operations Dashboard")
st.success(f"Welcome {st.session_state.username} ({st.session_state.role})")

#showing the table by using read fucntion from incidents.py
def load_df():
    try:
        df_data = get_incidents()
        return df_data
    except Exception as e:
        st.error(f"Failed to load incidents: {e}")
        return pd.DataFrame()

df = load_df()

#fixing some issues
if not df.empty:
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="ignore")
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="ignore")
    if "id" in df.columns:
        df = df.sort_values("id", ascending=True)

#using metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Incidents", len(df))
col2.metric("Critical", int((df["severity"] == "critical").sum()) if "severity" in df.columns else 0)
col3.metric("Open", int((df["status"] == "open").sum()) if "status" in df.columns else 0)

st.divider()

#Making tabs
tab1, tab2, tab3 = st.tabs(["📋 Incidents", "📊 Analytics", "🤖 AI Assistant"])

#Tab for showing CRUD functions for incidents
with tab1:

    #making 2 sides, left for showin the table and a right side for the first CRUD function in streamlit creat
    left, right = st.columns([2, 1])

    with left:
        st.subheader("All Incidents")
        if not df.empty:
            show_cols = ["id", "date", "incident_type", "severity", "status", "description", "reported_by", "created_at"]
            existing_cols = [c for c in show_cols if c in df.columns]
            st.dataframe(df[existing_cols], use_container_width=True)
        else:
            st.info("No incidents found.")

    with right:
        st.subheader("Add New Incident")
        with st.form("add_incident_form"):
            incident_date = st.date_input("Date")
            incident_type = st.text_input("Incident Type")
            severity = st.selectbox("Severity", ["low", "medium", "high", "critical"])
            status = st.selectbox("Status", ["open", "investigating", "resolved", "closed"])
            description = st.text_area("Description")
            reported_by = st.text_input("Reported By")

            submitted = st.form_submit_button("Create")

            if submitted:
                try:
                    add_incident(
                        date=incident_date.strftime("%Y-%m-%d"),
                        incident_type=incident_type,
                        severity=severity,
                        status=status,
                        description=description,
                        reported_by=reported_by,
                        created_at=datetime.now().strftime("%Y-%m-%d")
                    )
                    st.success("Incident added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to add: {e}")

    st.divider()

    if not df.empty and "id" in df.columns:
        st.subheader("Update or Delete Incident")
        selected_id = st.selectbox("Choose ID", df["id"].tolist())
        row = df[df["id"] == selected_id].iloc[0]

        #making update columns and delete columns
        ucol, dcol = st.columns(2)

        with ucol:
            with st.form("update_incident_form"):
                severity_opt = ["low", "medium", "high", "critical"]
                status_opt = ["open", "investigating", "resolved", "closed"]

                new_sev = st.selectbox("Severity", severity_opt,
                    index=severity_opt.index(row["severity"]) if row["severity"] in severity_opt else 0)
                new_status = st.selectbox("Status", status_opt,
                    index=status_opt.index(row["status"]) if row["status"] in status_opt else 0)
                new_desc = st.text_area("Description", value=row["description"])

                if st.form_submit_button("Update"):
                    try:
                        change_incident_status(int(selected_id), new_sev, new_status, new_desc)
                        st.success("Updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")

        with dcol:
            if st.checkbox("Confirm delete this incident"):
                if st.button("DELETE", type="primary"):
                    try:
                        remove_incident(int(selected_id))
                        st.success("Incident deleted!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {e}")

#tab for charts
with tab2:
    st.subheader("Incident Analytics")

    # Button for severity bar chart
    if st.button("Show Severity Bar Chart"):
        if not df.empty:
            import altair as alt
            severity_df = df["severity"].value_counts().reset_index()
            severity_df.columns = ["severity", "count"]

            bar = alt.Chart(severity_df).mark_bar().encode(
                x=alt.X("severity", sort="-y"),
                y="count",
                color="severity",
                tooltip=["severity", "count"]
            )
            st.altair_chart(bar, use_container_width=True)

    # Button for status pie chart
    if st.button("Show Status Pie Chart"):
        if not df.empty:
            import altair as alt
            status_ct = df["status"].value_counts().reset_index()
            status_ct.columns = ["status", "count"]
            status_ct["percent"] = (status_ct["count"] / status_ct["count"].sum()) * 100

            pie = alt.Chart(status_ct).mark_arc().encode(
                theta="count",
                color="status",
                tooltip=["status", alt.Tooltip("percent", format=".1f")]
            )
            st.altair_chart(pie, use_container_width=True)

    # Button for line chart
    if st.button("Show Incidents Over Time"):
        if not df.empty and "date" in df.columns:
            df_chart = df.copy()
            df_chart["date_dt"] = pd.to_datetime(df_chart["date"], errors="coerce")
            df_valid = df_chart[df_chart["date_dt"].notna()]

            if not df_valid.empty:
                line_df = df_valid.groupby(df_valid["date_dt"].dt.date).size().reset_index(name="count")
                line_df.columns = ["date", "incidents"]
                st.line_chart(line_df.set_index("date"))
            else:
                st.info("No valid dates to plot.")

#Tab for AI
with tab3:

    #making left and right sides 
    top_left, top_right = st.columns([4, 1])

    with top_left:
        st.markdown("##  Cybersecurity AI Assistant")

    #adding clear chat button so its easier for user to use in a clean way
    with top_right:
        if st.button("Clear chat"):
            st.session_state.cyber_chat = [
                {"role": "system", "content": "You are a cybersecurity expert assistant."}
            ]
            st.rerun()

    st.markdown(
        """
        **Powered by OpenAI**

        Ask questions such as:
        - What is Bcrypt?
        - Explain the difference between a virus and a worm?
        - Recommend cyber programms
        """
    )

    if "cyber_chat" not in st.session_state:
        st.session_state.cyber_chat = [
            {"role": "system", "content": "You are a cybersecurity expert assistant."}
        ]

    for msg in st.session_state.cyber_chat:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    user_input = st.chat_input("Ask the cybersecurity assistant...")
    if user_input:
        st.session_state.cyber_chat.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.cyber_chat
        )

        ai_reply = response.choices[0].message.content
        st.session_state.cyber_chat.append({"role": "assistant", "content": ai_reply})

        with st.chat_message("assistant"):
            st.write(ai_reply)

st.divider()

if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.success("Logged out!")