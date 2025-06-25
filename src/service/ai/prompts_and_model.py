from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


general_chat_model = ChatOpenAI(model="gpt-4o", temperature=0.6)

categorier_model = ChatOpenAI(model="gpt-4o", temperature=0)


intent_categorier_prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are a categorier agent that is capable to categorize the user's message into a category.
        - The user's message: {input}
        - The category:
        """),
    # ("placeholder", "{chat_history}"),
    ("user", """
     User will send you a query and you will categorize the query into a category on below criteria:
     - If the query is about energy then it is a energy query
     - If the user is asking or looking for some product or service then return "BECKN_TRANSACTION"
     - If the user is asking to select a product or service then return "BECKN_TRANSACTION"
     - If the user is asking to confirm an order or transaction then return "BECKN_TRANSACTION"
     - If the user is asking to query related to any topic then return "GENERAL"
     User's message: {input}
     AI Response:
     
     **NOTE:**
     - Only return the category name, do not return any other text or explanation
     """),
])







general_prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are Luma an AI Agent that is capable to perform:
        - Beckn Open Network transactions for energy domains and their subdomains are
            - Retail: Buy retail energy appliance eg. Battery, Solar Panel, etc.
            - Schemes: Subscribe to energy schemes eg. DFP (Demand Flexibility Program) and get discounts on energy consumption
        - Answer general queries on any topic
        - If the user greets you then, greet the user, by introducing yourself introduce the user to your capabilities 
        """),
    ("placeholder", "{chat_history}"),
    ("user", """
     User will provide a message to you, and you will respond to the user based on your capabilities and the user's message
     User's message: {input}
     AI Response:
     """),
])  
