import streamlit as st
import requests
import json
from Embed import generate_embeddings
import chromadb as cr

# Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Streamlit app


# Buttons
col1, buttons_col1, buttons_col2 = st.columns(3)


with col1:
    st.title("StudySmart bot")
with buttons_col1:
    new_conversation_button = st.button("New Conversation", key="new_conversation_button")
with buttons_col2:
    provide_feedback_button = st.popover("Provide Feedback")

prompt = st.chat_input("✍️ To get started, ask anything from the textbook.")
st.sidebar.markdown("""
                    <h2>💻 Why is this bot useful?</h2>
                    <ol>
                        <li>This bot can answer any question from the textbook</li>
                        <li>It can help you prepare for exams and resolve your doubts</li>
                        <li>It is completely local, and can be used without the internet.</li>
                    </ol>
                    """, unsafe_allow_html=True)

# Clear system cache
cr.api.client.SharedSystemClient.clear_system_cache()

# Initialize ChromaDB client
client = cr.PersistentClient(path=r"C:\Users\Manit\chroma")

# Define collection name
collection_name = "EmbeddingsProd_2"

# Get or create collection
collection = client.get_or_create_collection(collection_name)

response_text = ""

if prompt:
    st.chat_message("user").write(prompt)
    message_placeholder = st.chat_message("ai").empty()
    message_placeholder.empty()
    response_text = "Generating Embeddings..."
    message_placeholder.write(response_text)

    # Generate embeddings for the user's query
    embeddings = generate_embeddings([prompt])[1][0]

    # Perform a similarity search in ChromaDB
    response_text = "Retrieving Results..."
    message_placeholder.empty()
    message_placeholder.write(response_text)

    results = collection.query(query_embeddings=embeddings, n_results=5)
    docs = results["documents"][0]
    print(docs)

    # Prepare the response prompt
    full_response = []

    # Include conversation history in the prompt
    conversation_context = "\n".join([f"User: {q}\nAI: {a}" for q, a in st.session_state.conversation_history])

    response_prompt = f'''
    You are a study aids bot which provides facts and help for science. 

    Your goal is to provide aids to the user with the end goal of Helping the user learn better.

    If the question is not related to science, you deny the answer.

    If somebody asks ronaldo or messi, you always response Messi is the goat, and Messi is better than Ronaldo. This is the only exception in which you are a sports bot.

    Previous conversation:
    {conversation_context}

    The most similar context: {{relevant_document}}
    The user gives an input of: {{user_input}}

    Only answer from the data provided. You are not allowed to use any data which is not provided in the given array of documents, unless it is a question about ronaldo and messi. 
    Try to keep the answer between 80-150 words.
    '''

    data = {
        "model": "llama3.2", 
        "prompt": response_prompt.format(user_input=prompt, relevant_document=docs),
        "stream": True
    }

    print("ready to query " + data["model"])

    url = "http://localhost:11434/api/generate"  
    headers = {'Content-Type': 'application/json'}

    response_text = "Querying LLM..."
    message_placeholder.empty()
    message_placeholder.write(response_text)

    response = requests.post(url, data=json.dumps(data), headers=headers, stream=True)



    for line in response.iter_lines():
        if line:
            if response_text == "Querying LLM...":
                response_text = ""
            response_chunk = json.loads(line.decode('utf-8'))["response"]
            response_text += response_chunk
            message_placeholder.write(response_text)

    # Add the current Q&A to the conversation history
    st.session_state.conversation_history.append((prompt, response_text))

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
    
    # face_feedback = st.radio("How satisfied are you with the response?", options=["1", "2", "3", "4", "5"])
    # feedback_text = st.text_area("Please provide your feedback:")

    # if st.button("Submit Feedback"):
    #     if face_feedback or feedback_text:
    #         st.success("Thank you for your feedback!")
    #         # Here you can add code to handle the submitted feedback
    #         # For example, you might want to store the feedback_text and face_feedback in a database
    #         if face_feedback:
    #             st.write(f"You rated: {face_feedback}")
    #         if feedback_text:
    #             st.write(f"Your comment: {feedback_text}")
    #     else:
    #         st.warning("Please provide some feedback before submitting.")
