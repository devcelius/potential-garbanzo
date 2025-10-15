from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer, AutoModel
import chromadb
import torch
from tqdm import tqdm
import ollama as ol
import asyncio
import pymupdf


class Encoder:
    def __init__(self):
        chromadb.api.client.SharedSystemClient.clear_system_cache()
        self.client = chromadb.PersistentClient(path=r"C:\Users\Manit\chroma")
        collection_name = "Maine2.0_DEV1"
        self.collection = self.client.get_or_create_collection(collection_name)
        self.tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
        self.model = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')
        
    async def generate_embeddings(self, book):
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
        print(len(blocks))
        Final_Responses = []
        for p,page_number in tqdm(blocks):
            # print(p)
            # print(len(paragraphs))
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
            # print(resp)
            responses = []
            a = resp.message.content.split('\n')
            if not a.__contains__("MONKEY"):
                for f in a:
                    responses.append(f)
                    print("Block page number:"+str(page_number))
            Final_Responses.append([responses, page_number])
        print(Final_Responses)
        # for doc, page_number in Final_Responses:
        #     for i in doc:
        #         tokenized = self.tokenizer(
        #             i,
        #             padding=True,
        #             truncation=True,
        #             add_special_tokens=True,
        #             return_attention_mask=True, 
        #             return_tensors="pt"
        #         )
        # chunked_parts = self.splitter.split_text(book)
        
        # vectors = []
        # for doc in tqdm(responses):
        #     tokenized = self.tokenizer(
        #         doc,
        #         padding=True,
        #         truncation=True,
        #         add_special_tokens=True,
        #         return_attention_mask=True, 
        #         return_tensors="pt"
        #     )

        #     with torch.no_grad():
        #         embedding = self.model(**tokenized)
        #     vector = embedding.last_hidden_state.mean(dim=1).squeeze().numpy()
        #     self.collection.add(vector)
        #     vectors.append(vector)  
        

encode = Encoder()
asyncio.run(encode.generate_embeddings("C:\\Users\\Manit\\Cod\\rag1\\pdfs\\rhk.pdf"))