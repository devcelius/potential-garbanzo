import chromadb
import ollama as ol
from embed import Encoder
import time
import typing

class model:
    """
    stitches together all the components to create on seamless flow \n
    includes db queries, model prompting, COT architecture etc. \n
    """
    def __init__(self) -> None:
        
        self.text:str = "Initiating model..." 
        self.done = False
        chromadb.api.client.SharedSystemClient.clear_system_cache()
        self.client = chromadb.PersistentClient(path=r"C:\Users\Manit\chroma")
        self.collection = self.client.get_collection("Maine2.0_DEV4")
        

    def prompt(self, message:str, think:typing.Literal[True] = True) -> ol.ChatResponse:
        self.done = False
        self.text = ""
        """
        Main Flow Of Questions. Stitches together all the components to create one seamless flow. \n
        """
        classification = ""
        chromaDBQuery=[]
        self.text = "Classifying problem..."
        # Assign Easy Or Difficult

        classification = ol.chat(model='llama3.2', messages=[
            {
                'role':'user',
                'content': 
f"""
You Will be given a query. If the query is a numerical, or something more complex than a simple fact based question, then you are to return the word MONKEY.
Or else you will generate from the query a scentence which can be used to search a database for the required info.
You Are not to return anything else including including small talk.

Example:
Query:
hey there, could you tell me the value of g which in this case is accelaratin due to gravty.
Response:
What is the accelaration due to gravity?

Query: {message}

"""
        
            }
        ])

        # If Easy then simply append or query more advanced model.

        if not classification.message.content.__contains__("MONKEY"):
            self.text = "Simple query, generating database query using llama"
            print("Simple Query!")
            chromaDBQuery.append(classification.message.content)
        else:
            self.text = "Complex query, generating database query using r1"
            classification = ol.chat('llama3.2', messages=[
                {
                    'role': 'user',
                    'content': 
f"""
Generate a list of facts or formulae required to solve the following problem in the form of quesstions.
These will be queried in the database to return the required items.
You can generate multiple questions. Each of them should be separated by a '-'

Example Answer:
    -What is the formula for horizontal range of a projectile?

Here is your prompt:
{message}
"""
                }
            ])
            print(classification.message.content.split('-'))
            chromaDBQuery = classification.message.content.split('-')
            
        self.text = "Running database query"
            # Begin the DB Query
        results = []
        for queryString in chromaDBQuery:
            monkey = Encoder()
            a = monkey.query(queryString)
            for doc in a:
                results.append(doc)
            print(results)

        self.text = "beginning chain of thought..."
        response = ol.chat('deepseek-r1:7b', messages=[{
                'role': 'user',
                'content': 
f"""
You are a helpful problem solving bot, who solves STEM problems. here is your question:

{message}

Solve the above problem, if any of the below strings can be used to help solve the problem, mention them in a list along with their associated numbers at the end of the answer.
{results}
"""
            }], stream=True, think=True, )
        in_thinking = False
        for chunk in response:
            if think:     
                if chunk.message.thinking:
                    if not in_thinking:
                        in_thinking = True
                        self.text = 'Thinking:\n'
                    self.text +=chunk.message.thinking
                    print(self.text)
            if not think:
                if not chunk.message.content:
                    self.text = "Thinking..."
            if chunk.message.content:
                if in_thinking:
                    in_thinking = False
                    self.text +='\n\nAnswer:\n'
                self.text+=chunk.message.content
        self.done = True
            