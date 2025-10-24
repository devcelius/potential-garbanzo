import streamlit as st
from embed import Encoder
import threading
import time

st.header("Upload A Book!")

uploaded_file = st.file_uploader("Upload File Here", accept_multiple_files=False)
if uploaded_file is not None:
    with open(f"C:\\Users\\Manit\\Cod\\rag1\\pdfs\\{uploaded_file.name}", "wb") as f:
        f.write(uploaded_file.getbuffer())
        st.success("File Saved! Beginning Embedding!")
    if not 'b' in st.session_state:
        st.session_state.b = Encoder()
    a:Encoder = st.session_state.b
    def runPrompt():
        a.generate_embeddings(f"C:\\Users\\Manit\\Cod\\rag1\\pdfs\\{uploaded_file.name}", uploaded_file.name)
    threading.Thread(target=runPrompt, daemon=True).start()
    placeholder = st.empty()
    while not a.done:
        placeholder.info(a.progress)
        time.sleep(0.01)
    