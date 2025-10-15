import streamlit as st
from flow import prompt as pm
# Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []


# Buttons
col1, buttons_col1, buttons_col2 = st.columns(3)


with col1:
    st.title("StudySmart bot")
with buttons_col1:
    new_conversation_button = st.button("New Conversation", key="new_conversation_button")
with buttons_col2:
    provide_feedback_button = st.popover("Provide Feedback")

prompt = st.chat_input("To get started, ask anything.")
if prompt:
    response = pm(prompt)
    st.chat_message(response)

# Handle button clicks
if new_conversation_button:
    st.session_state.conversation_history = []
    st.toast("✅ New conversation started!")

with provide_feedback_button:
    st.write("Please provide your feedback.")
    face_feedback = st.feedback("faces")
    txt= st.text_area("Enter any specific comments here.")
    submit = st.button("Submit Feedback")
    if submit:
        if face_feedback:
            open("feedback.txt", "a").write(f"Face Feedback: {face_feedback}\n")
        else:
            st.error("Please provide a face feedback.")    
        if txt!="":
            open("feedback.txt", "a").write(f"Text Feedback: {txt}\n")
        st.toast("Thank you for your feedback.")

st.sidebar.write()