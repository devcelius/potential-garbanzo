import streamlit as st
from main import generateResponse
import ollama as ol
from flow import model
import threading
import time

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = ["what is the integral of 2x"]
if 'questionDisplayed' not in st.session_state:
    st.session_state.questionDisplayed = False
if 'generatedQuestion' not in st.session_state:
    st.session_state.generatedQuestion = ""

def render_latex_text(text: str, placeholder):
    text = (text.replace(r"\(", "$")
                 .replace(r"\)", "$")
                 .replace(r"\[", "$$")
                 .replace(r"\]", "$$"))
    placeholder.markdown(text)


def generateResponse(prompt):
    print("Hallo")
    print(prompt)
    if not 'a' in st.session_state:
        st.session_state.a = model()
    a:model = st.session_state.a
    def runPrompt():
        a.prompt(prompt, think=True)
    threading.Thread(target=runPrompt, daemon=True).start()
    with st.chat_message("ai"):
        placeholder = st.empty()
        while not a.done:
            render_latex_text(a.text, placeholder=placeholder)
            time.sleep(0.1)

if (st.session_state.conversation_history == []) or (not st.session_state.conversation_history):
    st.header("Oh Noes! Please go and solve some of your doubts to help us understand your level!")
else:
    if 'questionDisplayed' not in st.session_state:
        st.session_state.questionDisplayed = False
    button = st.button("Generate question")
    if button:
        st.session_state.questionDisplayed = True
        placeholder = st.empty()
        placeholder.markdown("generating a question....")
        response = ol.chat("llama3.2", messages=[{
            'role':'user',
            'content':
f"""
You are a helpful bot generating problems to help user's prepare for their exams. You are to return one singular question. the content of this question is to be based on the user's knowledge level, which will be extrapolated by you from the given set of questions the user has previously asked.

Previously asked questions:
{st.session_state.conversation_history}
"""
}])
        placeholder.markdown(response.message.content)
        st.session_state.generatedQuestion = response.message.content
    if st.session_state.questionDisplayed:
        genRes = st.button("Generate Response")
        if genRes:
            print("Hallo!")
            generateResponse(st.session_state.generatedQuestion)