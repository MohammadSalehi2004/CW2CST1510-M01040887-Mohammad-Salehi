import streamlit as st
import pandas as pd
import numpy as np
st.title ("Hi, I am Mohammad!")
st.header("This is my header")
st.subheader("This is my subheader")
st.write("This is my first streamlit program")
st.markdown("Hi **How** `R` *U*")
st.caption("Wow caption")

df=pd.DataFrame({
    "name":["Alice","Bob","Charlie"],
    "age":[25,32,29]
})
st.dataframe(df)

st.divider()

st.image(
    "C:\\Users\\mohammad\\Desktop\\image.png",
    use_container_width=True
)

data = pd.DataFrame(
np.random.randn(20,5),
columns=["A","B","C","D","E"]
)

st.line_chart(data)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "users" not in st.session_state:
    st.session_state.users = {}

st.session_state.logged_in=True
st.session_state.username="Alice"
st.session_state.role="Admin"

if st.session_state.logged_in:
    st.write(
        f"Welcome, {st.session_state.username}!"
    )
st.write(
    f"Role: {st.session_state.role}"
)

