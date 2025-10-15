import chromadb
import ollama as ol

class model:
    def __init__(self):
        chromadb.api.client.SharedSystemClient.clear_system_cache()
        self.llama = ol.create('llama3.2')
        self.ds = ol.create('deepseek-r1:7b')
        self.client = chromadb.PersistentClient(path=r"C:\Users\Manit\chroma")
    def prompt(message:str):
        print(message)
        
        return "hello"