import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize OpenAI client
api_key = st.secrets["OPENAI_API_KEY"]

# ═══════════════════════════════════════════════
# STEP 1: Initialize session state for messages
# ═══════════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# ═══════════════════════════════════════════════
# STEP 2: Display existing messages
# ═══════════════════════════════════════════════
for message in st.session_state.messages:
    # Skip system messages (don't show to user)
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# ═══════════════════════════════════════════════
# STEP 3: Handle user input
# ═══════════════════════════════════════════════
user_input = st.chat_input("Type your message...", key="main_chat_input")

if user_input:
    # Display user message immediately
    with st.chat_message("user"):
        st.write(user_input)

    # Add user message to session state
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    # ═══════════════════════════════════════════════
    # STEP 4: Get AI response
    # ═══════════════════════════════════════════════
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=st.session_state.messages
    )

    # Extract AI message
    ai_message = response.choices[0].message.content

    # Display AI response
    with st.chat_message("assistant"):
        st.write(ai_message)

    # ═══════════════════════════════════════════════
    # STEP 5: Save AI response to session state
    # ═══════════════════════════════════════════════
    st.session_state.messages.append(
        {"role": "assistant", "content": ai_message}
    )


if user_input:
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Add to session state
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    
    # ═══════════════════════════════════════════════
    # STREAMING: Enable stream=True parameter
    # ═══════════════════════════════════════════════
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=st.session_state.messages,
        stream=True  # ← Enable streaming!
    )
    
    # ═══════════════════════════════════════════════
    # STEP 1: Create empty placeholder for AI response
    # ═══════════════════════════════════════════════
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # ═══════════════════════════════════════════════
        # STEP 2: Process chunks as they arrive
        # ═══════════════════════════════════════════════
        for chunk in response:
            # Extract content from chunk
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                
                # ═══════════════════════════════════════════════
                # STEP 3: Update display with cursor effect
                # ═══════════════════════════════════════════════
                message_placeholder.markdown(full_response + "▌")
        
        # ═══════════════════════════════════════════════
        # STEP 4: Final display without cursor
        # ═══════════════════════════════════════════════
        message_placeholder.markdown(full_response)
    
    # Save complete response to session state
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )


import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ═══════════════════════════════════════════════
# SIDEBAR: Chat Controls
# ═══════════════════════════════════════════════
with st.sidebar:
    st.title("💬 Chat Controls")
    
    # Show message count
    message_count = len(st.session_state.get("messages", [])) - 1
    st.metric("Messages", message_count)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        # Reset messages to initial state
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        # Rerun to refresh the interface
        st.rerun()

# ═══════════════════════════════════════════════
# Initialize session state
# ═══════════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# ═══════════════════════════════════════════════
# Display existing messages
# ═══════════════════════════════════════════════
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# ═══════════════════════════════════════════════
# Handle user input
# ═══════════════════════════════════════════════


if user_input:
    # ... (same API call logic as before)
    pass