from transformers import AutoTokenizer, AutoModel
import chromadb
import torch
from tqdm import tqdm
import ollama as ol
import pymupdf
import random
import math

class Encoder:
    def __init__(self):
        chromadb.api.client.SharedSystemClient.clear_system_cache()
        self.client = chromadb.PersistentClient(path=r"C:\Users\Manit\chroma")
        collection_name = "Maine2.0_DEV4"
        self.collection = self.client.get_or_create_collection(collection_name)
        self.tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
        self.model = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')
        self.progress = ""
        self.done = False
        
    def generate_embeddings(self, book:str, bookName:str) -> None:
        self.done = False
        self.progress = "Parsing File"
        """
        Generates Embeddings for a pdf file of a given path
        Requires a path rstring and a full book name
        """
        reader = pymupdf.open(book)
        print("Started!")
        blocks = []
        for page in reader:
            if page.number < 16:
                pass
            else:
                text = page.get_text_blocks()
                for p in text:
                    blocks.append([p[4],page.number])
                if page.number > 16:
                    break
        print("text paragraphized")
        self.progress = "Evaluating Responses: 0%"
        print(len(blocks))
        Final_Responses = []
        counter = 0
        for p,page_number in tqdm(blocks):
            resp = ol.chat(model='llama3.2', messages=[
                {
                    'role':'user',
                    'content': f"""
You will be given an excerpt from a textbook. The excerpt may contain noise or be badly formatted.

Your task is to extract **only clean, precise scientific facts or definitions**.

Follow these rules strictly:
1. Extract only scientific facts, formulas, or definitions (e.g., values of constants, formulas, units, named laws).
2. Ignore all questions, introductions, examples, or instructions.
3. Preserve the mathematical structure of formulas.
4. If the excerpt contains no valid scientific content, respond with the keyword: MONKEY.
5. Return each extracted fact on a **separate line**.
6. Do not rewrite or rephrase — extract exactly what is present in the excerpt.

Examples of valid output:
- The value of the speed of light is 3×10^8 m/s
- The formula for force is mass times acceleration
- Acceleration due to gravity is 9.8 m/s²

Now extract from the following excerpt:

{p}


"""
                }
            ])
            self.progress = f"Evaluating Responses: {(counter/(len(blocks)))*100}%"
            responses = []
            a = resp.message.content.split('\n')
            counter+=1
            if not a.__contains__("MONKEY"):
                for f in a:
                    responses.append(f)
                    print("Block page number:"+str(page_number))
            Final_Responses.append([responses, page_number])
        print(Final_Responses)
        self.progress = "Generating Embeddings!"
        ids=[]
        vectors=[]
        documents=[]
        metadatas=[]
        for (doc, page_number) in tqdm(Final_Responses):
            for i in doc:
                if not i.strip():
                    continue
                tokenized = self.tokenizer(
                    i,
                    padding=True,
                    truncation=True,
                    add_special_tokens=True,
                    return_attention_mask=True,
                    return_tensors="pt"
                )

                with torch.no_grad():
                    embedding = self.model(**tokenized)

                vector = embedding.last_hidden_state[:, 0].squeeze().numpy()  # Use CLS token

                # Save all data for batch add
                vectors.append(vector)
                documents.append(i)
                metadatas.append({"page": page_number, book:bookName})
                
                ids.append(str(random.random()))
        self.progress = "Saving files!"
        self.collection.add(
            ids=ids,
            embeddings=vectors,
            documents=documents,
            metadatas=metadatas
        )
        self.progress = f"✅ Added {len(vectors)} text chunks to ChromaDB."
        print(f"✅ Added {len(vectors)} text chunks to ChromaDB.")
        self.done = True
    def query(self, query:str) -> list:
        """
        Takes a query and searches the chromadb collection for closest matches\n
        Returns a list of all the results and their metadata (page numbers and books.)
        """
        tokenized = self.tokenizer(
            query,
            padding=True,
            truncation=True,
            add_special_tokens=True,
            return_attention_mask=True,
            return_tensors="pt"
        )

        with torch.no_grad():
            query_embedding = self.model(**tokenized).last_hidden_state.mean(dim=1).squeeze().numpy()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )
        a = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            a.append([doc.strip(), meta['page']])
        return a
        