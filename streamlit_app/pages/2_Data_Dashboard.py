import streamlit as st
import pandas as pd
from datetime import datetime
from app.data.datasets import (
    list_datasets,
    create_dataset,
    update_dataset,
    delete_dataset
)
from openai import OpenAI

#setting up page information
st.set_page_config(page_title="Data Dashboard", layout="wide")

# palce for key
OPENAI_API_KEY = "key place"
client = OpenAI(api_key=OPENAI_API_KEY)

#checking for users to login or register
if not st.session_state.get("logged_in"):
    st.error("Please log in to view this page.")
    st.stop()
if st.session_state.role not in ["data", "admin"]:
    st.warning("You do not have permission to access this dashboard.")
    st.stop()

# page info and welcome
st.title("Data Operations Dashboard")
st.success(f"Welcome {st.session_state.username} ({st.session_state.role})")

#showing the table by using read fucntion from datasets.py
def load_df():
    try:
        return list_datasets()
    except Exception as e:
        st.error(f"Failed to load datasets: {e}")
        return pd.DataFrame()

df = load_df()

#fixing some issues
if not df.empty:
    if "last_updated" in df.columns:
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="ignore")
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="ignore")
    if "id" in df.columns:
        df = df.sort_values("id", ascending=True)

#using metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Datasets", len(df))
col2.metric("Total Records", int(df["record_count"].sum()) if "record_count" in df.columns else 0)
col3.metric("Avg File Size (MB)", round(df["file_size_mb"].mean(), 2) if "file_size_mb" in df.columns else 0)

st.divider()

#Making tabs
tab1, tab2, tab3 = st.tabs(["📋 Datasets", "📊 Analytics", "🤖 AI Assistant"])

#Tab for showing CRUD functions for datasets
with tab1:

    #making 2 sides, left for showin the table and a right side for the first CRUD function in streamlit creat
    left, right = st.columns([2, 1])

    with left:
        st.subheader("All Datasets")
        if not df.empty:
            show_cols = [
                "id", "dataset_name", "category", "source",
                "last_updated", "record_count", "file_size_mb", "created_at"
            ]
            existing_cols = [c for c in show_cols if c in df.columns]
            st.dataframe(df[existing_cols], use_container_width=True)
        else:
            st.info("No datasets found.")

    with right:
        st.subheader("Add New Dataset")
        with st.form("add_dataset_form"):
            name = st.text_input("Dataset Name")
            category = st.selectbox("Category", ["operations", "sales", "security", "finance"])
            source = st.selectbox("Source", ["Database", "CSV upload", "API"])
            last_updated = st.date_input("Last Updated")
            record_count = st.number_input("Record Count", min_value=0)
            file_size_mb = st.number_input("File Size (MB)", min_value=0.0)

            submitted = st.form_submit_button("Create")

            if submitted:
                try:
                    create_dataset(
                        dataset_name=name,
                        category=category,
                        source=source,
                        last_updated=last_updated.strftime("%Y-%m-%d"),
                        record_count=int(record_count),
                        file_size_mb=float(file_size_mb),
                        created_at=datetime.now().strftime("%Y-%m-%d")
                    )
                    st.success("Dataset added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to add: {e}")

    st.divider()

    if not df.empty and "id" in df.columns:
        st.subheader("Update or Delete Dataset")
        selected_id = st.selectbox("Choose ID", df["id"].tolist())
        row = df[df["id"] == selected_id].iloc[0]

        ucol, dcol = st.columns(2)

        with ucol:
            with st.form("update_dataset_form"):
                new_name = st.text_input("Dataset Name", value=row["dataset_name"])
                new_category = st.selectbox(
                    "Category",
                    ["operations", "sales", "security", "finance"],
                    index=["operations", "sales", "security", "finance"].index(row["category"])
                    if row["category"] in ["operations", "sales", "security", "finance"] else 0
                )
                new_source = st.selectbox(
                    "Source",
                    ["Database", "CSV upload", "API"],
                    index=["Database", "CSV upload", "API"].index(row["source"])
                    if row["source"] in ["Database", "CSV upload", "API"] else 0
                )
                new_last_updated = st.date_input(
                    "Last Updated",
                    value=pd.to_datetime(row["last_updated"]).date()
                )
                new_record_count = st.number_input(
                    "Record Count", min_value=0, value=int(row["record_count"] or 0)
                )
                new_file_size = st.number_input(
                    "File Size (MB)", min_value=0.0, value=float(row["file_size_mb"] or 0.0)
                )

                if st.form_submit_button("Update"):
                    try:
                        update_dataset(
                            dataset_id=int(selected_id),
                            dataset_name=new_name,
                            category=new_category,
                            source=new_source,
                            last_updated=new_last_updated.strftime("%Y-%m-%d"),
                            record_count=int(new_record_count),
                            file_size_mb=float(new_file_size)
                        )
                        st.success("Dataset updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")

        with dcol:
            if st.checkbox("Confirm delete this dataset"):
                if st.button("DELETE", type="primary"):
                    try:
                        delete_dataset(int(selected_id))
                        st.success("Dataset deleted!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {e}")

#tab for charts
with tab2:
    st.subheader("Dataset Analytics")

    if st.button("Show Category Bar Chart"):
        if not df.empty:
            import altair as alt
            cat_df = df["category"].value_counts().reset_index()
            cat_df.columns = ["category", "count"]
            bar = alt.Chart(cat_df).mark_bar().encode(
                x=alt.X("category", sort="-y"),
                y="count",
                color="category",
                tooltip=["category", "count"]
            )
            st.altair_chart(bar, use_container_width=True)

    if st.button("Show Source Pie Chart"):
        if not df.empty:
            import altair as alt
            src = df["source"].value_counts().reset_index()
            src.columns = ["source", "count"]
            src["percent"] = (src["count"] / src["count"].sum()) * 100
            pie = alt.Chart(src).mark_arc().encode(
                theta="count",
                color="source",
                tooltip=["source", alt.Tooltip("percent", format=".1f")]
            )
            st.altair_chart(pie, use_container_width=True)

    if st.button("Show Datasets Over Time"):
        if not df.empty and "created_at" in df.columns:
            df_chart = df.copy()
            df_chart["created_at_dt"] = pd.to_datetime(df_chart["created_at"], errors="coerce")
            df_valid = df_chart[df_chart["created_at_dt"].notna()]
            if not df_valid.empty:
                df_valid["month"] = df_valid["created_at_dt"].dt.strftime("%b %Y")
                line_df = df_valid.groupby("month").size().reset_index(name="datasets")
                st.line_chart(line_df.set_index("month"))
            else:
                st.info("No valid dates to plot.")

#Tab for AI
with tab3:

    top_left, top_right = st.columns([4, 1])

    with top_left:
        st.markdown("##  Data Operations AI Assistant")

    with top_right:
        if st.button("🗑 Clear chat"):
            st.session_state.data_chat = [
                {"role": "system", "content": "You are a data analytics expert."}
            ]
            st.rerun()

    st.markdown(
        """
        **Powered by OpenAI**

        Ask questions such as:
        - Summarize dataset trends
        - Which datasets are outdated?
        - Recommend data management strategies
        """
    )

    if "data_chat" not in st.session_state:
        st.session_state.data_chat = [
            {"role": "system", "content": "You are a data analytics expert."}
        ]

    for msg in st.session_state.data_chat:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    user_input = st.chat_input("Ask the data assistant...")
    if user_input:
        st.session_state.data_chat.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.data_chat
        )

        ai_reply = response.choices[0].message.content
        st.session_state.data_chat.append({"role": "assistant", "content": ai_reply})

        with st.chat_message("assistant"):
            st.write(ai_reply)

st.divider()

if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.success("Logged out!")