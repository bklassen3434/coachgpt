import streamlit as st
from router import route_user_prompt

# ---- Streamlit App ---- #
st.set_page_config(page_title="Softball Coach Assistant", page_icon="🥎", layout="centered")
st.title("🥎 Softball Coach Assistant")

# Session State to hold chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Display past messages
for message in st.session_state['messages']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Input box for new questions
user_input = st.chat_input("Ask your softball question...")

if user_input:
    # Add user message to history
    st.session_state['messages'].append({"role": "user", "content": user_input})

    # Call router to get response and updated chat history
    answer, updated_chat_history, optional_plot = route_user_prompt(user_input, st.session_state['chat_history'])

    # Update session chat history
    st.session_state['chat_history'] = updated_chat_history

    # Add assistant response to history
    st.session_state['messages'].append({"role": "assistant", "content": answer})

    # Display the assistant response
    with st.chat_message("assistant"):
        st.markdown(answer)
        if optional_plot:
            st.image(optional_plot, caption="Generated Visualization", use_column_width=True)

