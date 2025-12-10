import streamlit as st
import pandas as pd
from datetime import datetime
from app.data.tickets import (
    add_ticket,
    get_ticket_by_id,
    change_ticket_status,
    remove_ticket
)
from app.data.db import connect_database
from openai import OpenAI

#page info
st.set_page_config(page_title="IT Operations Dashboard", layout="wide")

#login check
if not st.session_state.get("logged_in"):
    st.error("Please log in to view this page.")
    st.stop()
if st.session_state.role not in ["it_ops", "admin"]:
    st.warning("You do not have permission to access this dashboard.")
    st.stop()

# getting data frame with read function
def get_all_tickets():
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM it_tickets ORDER BY id ASC", conn)
    conn.close()
    return df

# page info
st.title("IT Operations Dashboard")
st.success(f"Welcome {st.session_state.username} ({st.session_state.role})")

# loading data
try:
    df = get_all_tickets()
except Exception as e:
    st.error(f"Failed to get tickets: {e}")
    df = pd.DataFrame()

#fixing some issues
if not df.empty:
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="ignore")
    if "id" in df.columns:
        df = df.sort_values("id", ascending=True)

# metric functions
col1, col2, col3 = st.columns(3)
col1.metric("Total tickets", len(df))
col2.metric("Open", int((df["status"].str.lower() == "open").sum()) if "status" in df.columns else 0)
col3.metric("Closed", int((df["status"].str.lower() == "closed").sum()) if "status" in df.columns else 0)

st.divider()

# tabs to match Cyber/Data layout
tab1, tab2, tab3 = st.tabs(["📋 Tickets", "📊 Analytics", "🤖 AI Assistant"])

#Tab 1: CRUD
with tab1:
    left, right = st.columns([2, 1])

    with left:
        st.subheader("All Tickets")
        table_placeholder = st.empty()
        table_placeholder.dataframe(df.head(1000), use_container_width=True)

    with right:
        st.subheader("Create Ticket")
        with st.form("create_ticket"):
            ticket_id = st.text_input("Ticket ID")
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
            category = st.text_input("Category")
            subject = st.text_input("Subject")
            description = st.text_area("Description")
            created_date = st.date_input("Created Date")
            resolved_date = st.date_input("Resolved Date", value=None)
            assigned_to = st.text_input("Assigned To")
            created_at = datetime.now().strftime("%Y-%m-%d")

            if st.form_submit_button("Create"):
                try:
                    add_ticket(
                        ticket_id=str(ticket_id),
                        priority=priority,
                        status=status,
                        category=category,
                        subject=subject,
                        description=description,
                        created_date=str(created_date),
                        resolved_date=str(resolved_date) if resolved_date else None,
                        assigned_to=assigned_to,
                        created_at=created_at
                    )
                    st.success("Ticket created.")
                    df = get_all_tickets()
                    table_placeholder.dataframe(df.head(1000), use_container_width=True)
                except Exception as e:
                    st.error(f"Failed to create ticket: {e}")

    st.divider()

    if not df.empty and "id" in df.columns:
        st.subheader("Update or Delete Ticket")
        selected_id = st.selectbox("Select Ticket ID", df["id"])
        row = df[df["id"] == selected_id].iloc[0]

        ucol, dcol = st.columns(2)
        with ucol:
            with st.form("update_ticket"):
                status_options = ["Open", "In Progress", "Resolved", "Closed"]
                new_status = st.selectbox(
                    "Status",
                    status_options,
                    index=status_options.index(row["status"]) if row["status"] in status_options else 0
                )
                if st.form_submit_button("Update"):
                    try:
                        change_ticket_status(int(selected_id), new_status)
                        st.success("Ticket updated.")
                        df = get_all_tickets()
                        table_placeholder.dataframe(df.head(1000), use_container_width=True)
                    except Exception as e:
                        st.error(f"Failed to update ticket: {e}")

        with dcol:
            if st.checkbox("Confirm deletion"):
                if st.button("Delete ticket", type="primary"):
                    try:
                        remove_ticket(int(selected_id))
                        st.success("Ticket deleted.")
                        df = get_all_tickets()
                        table_placeholder.dataframe(df.head(1000), use_container_width=True)
                    except Exception as e:
                        st.error(f"Failed to delete ticket: {e}")

#Tab 2: Analytics
with tab2:
    st.subheader("Ticket Analytics")

    # button for bar chart
    if st.button("Show Tickets by Status"):
        if not df.empty and "status" in df.columns:
            st.bar_chart(df["status"].value_counts())

    # button for pie chart
    if st.button("Show Tickets by Priority"):
        if not df.empty and "priority" in df.columns:
            import altair as alt
            priority_counts = df["priority"].value_counts().reset_index()
            priority_counts.columns = ["priority", "count"]
            pie = alt.Chart(priority_counts).mark_arc().encode(
                theta="count",
                color="priority",
                tooltip=["priority", "count"]
            )
            st.altair_chart(pie, use_container_width=True)

    # button for line chart (simple like cyber dashboard)
    if st.button("Show Tickets Over Time"):
        if not df.empty and "created_at" in df.columns:
            line_df = df.groupby(df["created_at"].dt.date).size().reset_index(name="tickets")
            line_df.columns = ["date", "tickets"]
            st.line_chart(line_df.set_index("date"))

#Tab 3: AI Assistant
with tab3:
    st.markdown("## IT Operations AI Assistant")
    st.markdown(
        """
        **Powered by OpenAI**

        Ask questions such as:
        - What is API?
        - Which issues happen most often when dealing with API?
        - What should IT focus on right now?
        """
    )

    if "it_chat" not in st.session_state:
        st.session_state.it_chat = [
            {"role": "system", "content": "You are an IT operations expert assistant."}
        ]

    for msg in st.session_state.it_chat:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    user_input = st.chat_input("Ask the IT assistant...")
    if user_input:
        st.session_state.it_chat.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        client = OpenAI(api_key="key place")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.it_chat
        )

        ai_reply = response.choices[0].message.content
        st.session_state.it_chat.append({"role": "assistant", "content": ai_reply})

        with st.chat_message("assistant"):
            st.write(ai_reply)

st.divider()

#logout option
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()
