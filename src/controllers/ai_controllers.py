from unicodedata import category
from langchain_core.runnables import RunnableBranch, RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


from dotenv import load_dotenv

from service.ai.chat_history import with_session_memory
from service.ai.prompts_and_model import categorier_model, general_chat_model, general_prompt_template, intent_categorier_prompt_template

load_dotenv()


def log_beckn(x):
    print("Input as X in BECKN_TRANSACTION", x)
    return x

branches = RunnableBranch(
    (
        lambda x: isinstance(x, dict) and "BECKN_TRANSACTION" in x["category"],
        RunnableLambda(lambda x: isinstance(x, dict) and{**x, "output":x["input"]})
    ),general_prompt_template | general_chat_model | StrOutputParser()
    
)






def ai_health_check_controller():
    """Health check endpoint for AI service"""
    return {
        "status":"healthy",
        "message":"AI service is running"
    }

def ai_chat_controller(message: str, session_id: str = "default-session"):
    """Chat endpoint for AI service"""
    
    intent_categorier_chain = intent_categorier_prompt_template | categorier_model | StrOutputParser() | RunnableLambda(lambda x: {"category":x, "input":message})
    
    intent = intent_categorier_chain.invoke({"input":message})
    
    print("intent",intent)
    
    
    main_chain = branches
    
    
    main_chain_with_memory = with_session_memory(main_chain)
    data = main_chain_with_memory.invoke({"input": intent["input"], "category":intent["category"]}, config={"configurable":{"session_id":session_id}})
    print("data",data)
    return {
        "status":"success",
        "message":data
    }