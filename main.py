import streamlit as st
from flow import model
import time
import threading
# Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = ["what is the integral of 2x"]

st.session_state.inital = True

options = st.sidebar.popover("Options")
with options:
    thinking = st.toggle("Think", value=True)
    remember = st.toggle("Remember This Question?", value=True)

def render_latex_text(text: str, placeholder):
    text = (text.replace(r"\(", "$")
                 .replace(r"\)", "$")
                 .replace(r"\[", "$$")
                 .replace(r"\]", "$$"))
    placeholder.markdown(text)


def generateResponse(prompt):
    with st.chat_message("human"):
        st.write(prompt)
    if not 'a' in st.session_state:
        st.session_state.a = model()
    a:model = st.session_state.a
    if remember:
        st.session_state.conversation_history.append(prompt)
    def runPrompt():
        a.prompt(prompt, think=thinking)
    threading.Thread(target=runPrompt, daemon=True).start()
    with st.chat_message("ai"):
        placeholder = st.empty()
        while not a.done:
            render_latex_text(a.text, placeholder=placeholder)
            time.sleep(0.1)


# UI FROM HERE
#---------------------------------------------

col1, buttons_col1, buttons_col2 = st.columns(3)
placeholder = st.empty()

with col1:
    st.title("Study Bot")
with buttons_col1:
    new_conversation_button = st.button("Delete History", key="new_conversation_button")
with buttons_col2:
    provide_feedback_button = st.popover("Provide Feedback")


prompt = st.chat_input("To get started, ask anything.")
if prompt:
    st.session_state.inital = False
    with st.chat_message("human"):
        st.write(prompt)
    if not 'a' in st.session_state:
        st.session_state.a = model()
    a:model = st.session_state.a
    if remember:
        st.session_state.conversation_history.append(prompt)
    def runPrompt():
        a.prompt(prompt, think=thinking)
    threading.Thread(target=runPrompt, daemon=True).start()
    with st.chat_message("ai"):
        placeholder = st.empty()
        while not a.done:
            render_latex_text(a.text, placeholder=placeholder)
            time.sleep(0.1)
  
# Handle button clicks
if new_conversation_button:
    st.session_state.conversation_history = []
    st.session_state.inital= True
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

