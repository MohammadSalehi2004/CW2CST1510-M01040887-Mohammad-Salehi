import streamlit as st
import pandas as pd
from datetime import datetime
from app.data.tickets import add_ticket, change_ticket_status, remove_ticket
from app.data.db import connect_database
from openai import OpenAI

#page info
st.set_page_config(page_title="IT Operations Dashboard", layout="wide")

#api key variable
OPENAI_API_KEY = "key place"
client = OpenAI(api_key=OPENAI_API_KEY)

if not st.session_state.get("logged_in"):
    st.error("Please log in to view this page.")
    st.stop()
if st.session_state.role not in ["it_ops", "admin"]:
    st.warning("You do not have permission to access this dashboard.")
    st.stop()


#welcome message
st.title("IT Operations Dashboard")
st.success(f"Welcome {st.session_state.username} ({st.session_state.role})")

#loading table and acsending for order
def load_df():
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM it_tickets ORDER BY id ASC", conn)
    conn.close()
    return df

try:
    df = load_df()
except Exception as e:
    st.error(f"Failed to load tickets: {e}")
    df = pd.DataFrame()

if not df.empty:
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    if "resolved_date" in df.columns:
        df["resolved_date"] = pd.to_datetime(df["resolved_date"], errors="coerce")
    if "id" in df.columns:
        df = df.sort_values("id", ascending=True)

#metrics part
col1, col2, col3 = st.columns(3)
col1.metric("Total Tickets", len(df))
col2.metric("Open", int((df["status"].str.lower() == "open").sum()) if "status" in df.columns else 0)
col3.metric("Closed", int((df["status"].str.lower() == "closed").sum()) if "status" in df.columns else 0)

st.divider()


#making 3 tabs for CRUD handling, charts and AI part
tab1, tab2, tab3 = st.tabs(["📋 Tickets", "📊 Analytics", "🤖 AI Assistant"])

with tab1:
    left, right = st.columns([2, 1])

    with left:
        st.subheader("All Tickets")
        if not df.empty:
            show_cols = ["id","ticket_id","priority","status","category","subject",
                         "description","resolved_date","assigned_to","created_at"]
            existing_cols = [c for c in show_cols if c in df.columns]
            df_display = df.copy()
            if "resolved_date" in df_display.columns:
                df_display["resolved_date"] = pd.to_datetime(df_display["resolved_date"], errors="coerce")
                df_display["resolved_date"] = df_display["resolved_date"].dt.strftime("%Y-%m-%d").fillna("None")
            if "created_at" in df_display.columns:
                df_display["created_at"] = pd.to_datetime(df_display["created_at"], errors="coerce")
                df_display["created_at"] = df_display["created_at"].dt.strftime("%Y-%m-%d %H:%M:%S").fillna("None")
            st.dataframe(df_display[existing_cols], use_container_width=True)
        else:
            st.info("No tickets found.")

    with right:
        st.subheader("Create Ticket")
        with st.form("create_ticket_form"):
            ticket_id = st.text_input("Ticket ID")
            priority = st.selectbox("Priority", ["Low","Medium","High","Critical"])
            status = st.selectbox("Status", ["Open","In Progress","Resolved","Closed"])
            category = st.text_input("Category")
            subject = st.text_input("Subject")
            description = st.text_area("Description")
            try:
                resolved_date = st.date_input("Resolved Date (optional)", value=None, key="create_resolved_date")
            except Exception:
                resolved_date = None
            assigned_to = st.text_input("Assigned To")
            submitted = st.form_submit_button("Create")

            if submitted:
                try:
                    created_at_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    resolved_str = None
                    if resolved_date is not None:
                        try:
                            resolved_str = resolved_date.strftime("%Y-%m-%d")
                        except Exception:
                            resolved_str = None
                    add_ticket(ticket_id, priority, status, category, subject, description,
                               resolved_str, assigned_to, created_at_str)
                    st.success("Ticket created successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to create ticket: {e}")

    st.divider()

    if not df.empty and "id" in df.columns:
        st.subheader("Update or Delete Ticket")
        selected_id = st.selectbox("Choose ID", df["id"].tolist())
        row = df[df["id"] == selected_id].iloc[0]

        #two columns in update and delete section
        ucol, dcol = st.columns(2)

        #update
        with ucol:
            with st.form("update_ticket_form"):
                status_opts = ["Open", "In Progress", "Resolved", "Closed"]
                current_status = row["status"] if "status" in row and pd.notna(row["status"]) else "Open"
                new_status = st.selectbox(
                    "Status",
                    status_opts,
                    index=status_opts.index(current_status) if current_status in status_opts else 0
                )

                current_resolved = None
                try:
                    if pd.notna(row.get("resolved_date")):
                        current_resolved = pd.to_datetime(row.get("resolved_date")).date()
                except Exception:
                    current_resolved = None

                new_resolved = st.date_input("Resolved Date (optional)", value=current_resolved, key=f"update_resolved_{selected_id}")

                if st.form_submit_button("Update"):
                    try:
                        resolved_val = None
                        if new_resolved is not None:
                            try:
                                resolved_val = new_resolved.strftime("%Y-%m-%d")
                            except Exception:
                                resolved_val = None

                        change_ticket_status(int(selected_id), new_status, resolved_date=resolved_val)
                        st.success("Ticket updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")
        #delete
        with dcol:
            if st.checkbox("Confirm delete this ticket"):
                if st.button("DELETE", type="primary"):
                    try:
                        remove_ticket(int(selected_id))
                        st.success("Ticket deleted!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {e}")

#chart tab for all 3 charts
with tab2:
    st.subheader("Ticket Analytics")

    if st.button("Show Tickets by Status bar chart"):
        if not df.empty and "status" in df.columns:
            import altair as alt
            status_df = df["status"].value_counts().reset_index()
            status_df.columns = ["status", "count"]

            bar = alt.Chart(status_df).mark_bar().encode(
                x=alt.X("status", sort="-y"),
                y="count",
                color="status",
                tooltip=["status", "count"]
            )
            st.altair_chart(bar, use_container_width=True)

    if st.button("Show Tickets by Priority pie chart"):
        if not df.empty and "priority" in df.columns:
            import altair as alt
            pri_df = df["priority"].value_counts().reset_index()
            pri_df.columns = ["priority", "count"]
            pri_df["percent"] = (pri_df["count"] / pri_df["count"].sum()) * 100

            pie = alt.Chart(pri_df).mark_arc().encode(
                theta="count",
                color="priority",
                tooltip=["priority", alt.Tooltip("percent", format=".1f")]
            )
            st.altair_chart(pie, use_container_width=True)

    if st.button("Show Tickets Over Time line chart"):
        if not df.empty and "created_at" in df.columns:
            df_chart = df.copy()
            df_chart["created_at_dt"] = pd.to_datetime(df_chart["created_at"], errors="coerce")
            df_valid = df_chart[df_chart["created_at_dt"].notna()]
            if not df_valid.empty:
                line_df = df_valid.groupby(df_valid["created_at_dt"].dt.date).size().reset_index(name="tickets")
                line_df.columns = ["date", "tickets"]
                st.line_chart(line_df.set_index("date"))
            else:
                st.info("No valid dates to plot.")

#AI tab section
with tab3:
    top_left, top_right = st.columns([4, 1])

    with top_left:
        st.markdown("## IT Operations AI Assistant")

    with top_right:
        if st.button("Clear chat"):
            st.session_state.it_chat = [
                {"role": "system", "content": "You are an IT operations expert assistant."}
            ]
            st.rerun()

    st.markdown(
        """
        *Powered by OpenAI*

        Ask questions such as:
        - What is API?
        - Which IT issues happen most often?
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

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.it_chat
        )

        ai_reply = response.choices[0].message.content
        st.session_state.it_chat.append({"role": "assistant", "content": ai_reply})

        with st.chat_message("assistant"):
            st.write(ai_reply)

st.divider()

if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.success("Logged out!")