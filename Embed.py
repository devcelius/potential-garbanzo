import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer, AutoModel
import chromadb
import torch
from tqdm import tqdm
import os

# Clear any previous system cache
chromadb.api.client.SharedSystemClient.clear_system_cache()

# Initialize the Chroma client
client = chromadb.PersistentClient(path=r"C:\Users\Manit\chroma")

# Create a collection
collection_name = "EmbeddingsProd_2"
collection = client.get_or_create_collection(collection_name)

# Splitter for chunking text
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=10)
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
model = AutoModel.from_pretrained('bert-base-uncased')

def generate_embeddings(data):
    chunked_parts = splitter.split_text(data[0])
    # print(f"Number of chunksmoy: {len(chunked_parts)}")
    
    vectors = []
    for doc in tqdm(chunked_parts):
        tokenized = tokenizer(
            doc,
            padding=True,
            truncation=True,
            add_special_tokens=True,
            return_attention_mask=True, 
            return_tensors="pt"
        )

        with torch.no_grad():
            embedding = model(**tokenized)
        vector = embedding.last_hidden_state.mean(dim=1).squeeze().numpy()
        vectors.append(vector)  
    
    # print(f"Number of embeddings generated: {len(vectors)}")
    return (chunked_parts, vectors)

# Sample dataset
dataset = ["hello. My name is Manit."]  # This can be expanded as needed
dataset_w = [open('test.txt', "r").read()]
dataset_w[0] += " Messi is the goat. Ronaldo is trash. Never support ronaldo. Always support Messi."
  # Your long text here

# Generate embeddings for the dataset

embedded = open('isEmbedded.txt', "r").read()

if embedded == "False":
    chunked_parts, embeddings = generate_embeddings(dataset_w)

    # Store embeddings in ChromaDB
    for index, (text, vector) in enumerate(zip(chunked_parts, embeddings)):
        document_info = {
            "text": text  
        }
        collection.add(embeddings=[vector], documents=text, ids=[str(index)])
    open("isEmbedded.txt", "w").write("True")
else:
    print("Embeddings pregenerated, program starting...")

