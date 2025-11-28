import streamlit as st
from openai import OpenAI
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)


import streamlit as st

# Display user messagewith st.chat_message("user"):
st.write("Hello, ChatGPT!")

# Display AI messagewith st.chat_message("assistant"):
st.write("Hello! How can I help?")
