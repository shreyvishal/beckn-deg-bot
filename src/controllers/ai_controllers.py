import json
import logging
from typing import Any, cast
from unicodedata import category
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnableMap
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


from dotenv import load_dotenv

from service.ai.chat_history import get_chat_history, with_session_memory
from service.ai.prompts_and_model import categorier_model, domain_categoriser_prompt_template, general_chat_model, general_prompt_template, intent_categorier_prompt_template
from service.ai.agents_and_tools import retail_agent_executor

load_dotenv()


def log_beckn(x):
    logging.info("Input as X in BECKN_TRANSACTION", x)
    return x






def domain_categoriser_chain(data):
    return( domain_categoriser_prompt_template 
        | categorier_model 
        | StrOutputParser() 
        | RunnableLambda( lambda x: 
           {"domain":x,"input":data["input"],"category":data["category"], "chat_history":data["chat_history"]}
            ))

branches = RunnableBranch(
    (
        lambda x: isinstance(x, dict) and "BECKN_TRANSACTION" in x["category"],
        RunnableLambda(lambda x: domain_categoriser_chain(x))
        | RunnableBranch(
            (
                lambda x: "deg:retail" in x["domain"] , # type: ignore
                RunnableLambda(lambda x, config: print("In deg:retail-----> ",x, config["configurable"]["session_id"]) or retail_agent_executor.invoke({**x, "input": x["input"], "session_id": config["configurable"]["session_id"]}, config=config)) # type: ignore
               
                | RunnableLambda(lambda x: {"output":x["output"]}) # type: ignore
            ),
            (
                lambda x: "deg:schemes" in x["domain"] , # type: ignore
                RunnableLambda(lambda x, config: print("In deg:schemes-----> ",x, config["configurable"]["session_id"]) or retail_agent_executor.invoke({**x, "input": x["input"], "session_id": config["configurable"]["session_id"]}, config=config)) # type: ignore
               
                | RunnableLambda(lambda x: {"output":x["output"]}) # type: ignore
            ),    
            RunnableLambda(lambda x: {"output":x})
            
        )
        
    ),
    RunnableLambda(lambda x: print("In General-----> ",x) or x)
    | general_prompt_template | general_chat_model | StrOutputParser()
    
)




def ai_chat_controller(message: str, session_id: str = "default-session"):
    chat_history = get_chat_history(session_id)
    """Chat endpoint for AI service"""
    intent_categoriser_chain = intent_categorier_prompt_template | categorier_model | StrOutputParser() | RunnableLambda(lambda x: { "category":x, "input":message})
    intent = intent_categoriser_chain.invoke({"input":message, "chat_history":chat_history.messages})
    
    print("intent",intent)
    
    
    main_chain = branches
    
    
    main_chain_with_memory = with_session_memory(main_chain)
    data = main_chain_with_memory.invoke({"input": intent["input"], "category":intent["category"]}, config={"configurable":{"session_id":session_id}})
   
   
    print("\n\ndata",data)
    return {
        "status":"success",
        "message":data
    }
    
    
    
def ai_health_check_controller(session_id: str = "default-session"):
    """Health check endpoint for AI service"""
    print("session_id-----> ",session_id)
    chat_history = get_chat_history(session_id)
    print("chat_history-----> ",chat_history)
    return {
        "status":"healthy",
        "message":"AI service is running",
        "data":chat_history
    }