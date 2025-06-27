# File: agents_and_tools.py

import json
import os
import time
from typing import Optional, Type, List
import uuid

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableWithMessageHistory
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool, StructuredTool
from langchain.agents import AgentExecutor, create_tool_calling_agent, create_react_agent
from langchain_openai import ChatOpenAI
from langchain import hub
from dotenv import load_dotenv
import requests
from service.ai.chat_history import get_chat_history
from service.ai.prompts_and_model import retail_agent_prompt
from service.schemas.product import ConfirmOrderResponse, SearchProductResponse, ProductItem, ProviderInfo, SelectProductResponse

load_dotenv()

BECKN_BASE_URL = os.getenv("BECKN_BASE_URL")
BAP_ID = os.getenv("BAP_ID")
BAP_URI = os.getenv("BAP_URI")




### ----------------------------------------
### 1. Define search tool
### ----------------------------------------

class SearchProductArgs(BaseModel):
    item_name: str = Field(description="Product name or keyword to search")
    session_id: str = Field(description="The session_id of the conversation and it should be from the config passed to the agent")
    domain:str = Field(description="The domain of the product of services or schemes passed to the agent for search_request")



def search_product_fn(item_name: str, session_id: str, domain:str) -> str:
    print(f"[TOOL] Searching Beckn for: {item_name}")
    print(f"[TOOL] Session ID: {session_id}")
    print(f"[TOOL] Domain: {domain}")

    chat_history = get_chat_history(session_id)
    url = "https://bap-ps-client-deg.becknprotocol.io/search"
    headers = {"Content-Type": "application/json"}

    payload = {
        "context": {
            "domain": domain,
            "action": "search",
            "location": {
                "country": {"code": "USA"},
                "city": {"code": "NANP:628"}
            },
            "version": "1.1.0",
            "bap_id": BAP_ID,
            "bap_uri": BAP_URI,
            "bpp_id": "bpp-ps-network-deg.becknprotocol.io",
            "bpp_uri": "https://bpp-ps-network-deg.becknprotocol.io",
            "transaction_id": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4()),
            "timestamp": str(int(time.time()))
        },
        "message": {
            "intent": {
                "item": {
                    "descriptor": {"name": item_name}
                }
            }
        }
    }
    print("Search payload-----> ",payload)

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        print("chat_history-----> ",chat_history.messages)
       
        items = []
        product_selection_map = {}
        responses = data.get("responses", [])

        for r in responses:
            providers = r.get("message", {}).get("catalog", {}).get("providers", [])
            for provider in providers:
                for item in provider.get("items", []):
                    name = item.get("descriptor", {}).get("name")
                    price = item.get("price", {}).get("value")
                    currency = item.get("price", {}).get("currency")
                    rating = item.get("rating", "N/A")
                    item_id = item.get("id")
                    provider_id = provider.get("id")
                    provider_name = provider.get("descriptor", {}).get("name")
                    if name and item_id:
                        idx = len(items) + 1
                        items.append({
                            "index": idx,
                            "name": name,
                            "price": price,
                            "currency": currency,
                            "rating": rating,
                            "provider_name": provider_name
                        })
                        product_selection_map[str(idx)] = {
                            "product_id": item_id,
                            "provider_id": provider_id,
                            "product_name": name
                        }

        if not items:
            return "Sorry, I couldn’t find any matching products. Please try a different query."

        response_text = "Here are some products I found:\n\n"
        for item in items:
            response_text += (
                f"{item['index']}. **{item['name']}**\n"
                f"   - Price: ₹{item['price']} {item['currency']}\n"
                f"   - Rating: ⭐ {item['rating']}\n"
                f"   - Provider: {item['provider_name']}\n\n"
            )
        
        
        print("response_text-----> ",response_text)
        chat_history.messages.append(AIMessage(content=json.dumps({"search_response": data})))
        return response_text

    except Exception as e:
        return f"Oops! Something went wrong while searching for products: {e}"


search_tool = StructuredTool.from_function(
    func=search_product_fn,
    name="beckn_search_api",
    description="Call this tool to search for products, serivces or schemes on beckn open network",
    args_schema=SearchProductArgs,
    return_direct=True,
)




## ----------------------------------------
## 2. Define select tool
## ----------------------------------------

class BecknSelectArgs(BaseModel):
    bpp_id: str = Field(description="The bpp_id of the catalog from search_response")
    bpp_uri: str = Field(description="The bpp_uri of the catalog from search_response")
    item_id: str = Field(description="The item_id of the catalog from search_response")
    provider_id: str = Field(description="The provider_id of the item from search_response")
    domain: str = Field(description="The domain of the catalog from search_response")
    session_id:str = Field(description="The session_id of the conversation and it should be from the config passed to the agent")


def select_product_fn(bpp_id:str, bpp_uri:str, item_id:str, provider_id:str, domain:str, session_id:str):
    """ Can be used to call beckn select api"""
    print(f"[TOOL] Calling beckn select api for: {item_id} with provider: {provider_id} and session: {session_id}")
    url = f"{BECKN_BASE_URL}/select"
    headers = {"Content-Type": "application/json"}
    payload = {
            "context": {
                "domain": domain,
                "action": "select",
                "location": {
                    "country": {
                        "code": "USA"
                    },
                    "city": {
                        "code": "NANP:628"
                    }
                },
                "version": "1.1.0",
                "bap_id": BAP_ID,
                "bap_uri": BAP_URI,
                "bpp_id": bpp_id,
                "bpp_uri": bpp_uri,
                "timestamp": "1750945005"
            },
            "message": {
                "order": {
                    "provider": {
                        "id": provider_id
                    },
                    "items": [
                        {
                            "id": item_id
                        }
                    ]
                }
            }
        }
    print("\n\nselect payload-----> ",payload, "\n\n")
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    print("data-----> ",data.get("responses", {}))
    chat_history = get_chat_history(session_id)
    chat_history.messages.append(AIMessage(content=json.dumps({"select_response": data})))
    return data
   
select_tool = StructuredTool.from_function(
    func=select_product_fn,
    name="beckn_select_api",
    description="Call the beckn select api to select an item and provider",
    args_schema=BecknSelectArgs,
    return_direct=False,
)





## ----------------------------------------
## 3. Define confirm tool
## ----------------------------------------


class ConfirmOrderArgs(BaseModel):
    bpp_id: str = Field(description="The bpp_id of the catalog from select_response")
    bpp_uri: str = Field(description="The bpp_uri of the catalog from select_response")
    item_id: str = Field(description="The item_id of the catalog from select_response")
    provider_id: str = Field(description="The provider_id of the item from select_response")
    domain: str = Field(description="The domain of the catalog from select_response")
    fulfillment_id: str = Field(description="The fulfillment_id of the item from select_response")
    session_id:str = Field(description="The session_id of the conversation and it should be from the config passed to the agent")


def confirm_order_fn(bpp_id: str, bpp_uri: str, item_id: str, provider_id: str, domain: str, fulfillment_id: str, session_id: str) -> ConfirmOrderResponse:
    print(f"[TOOL] Confirming order for: {item_id} with provider: {provider_id} and session: {session_id}")

    try:
        url = f"{BECKN_BASE_URL}/confirm"
        headers = {"Content-Type": "application/json"}

        payload = {
            "context": {
                "domain": domain,
                "action": "confirm",
                "location": {
                    "country": {"code": "USA"},
                    "city": {"code": "NANP:628"}
                },
                "version": "1.1.0",
                "bap_id": BAP_ID,
                "bap_uri": BAP_URI,
                "bpp_id": bpp_id,
                "bpp_uri": bpp_uri,
                "transaction_id": str(uuid.uuid4()),
                "message_id": str(uuid.uuid4()),
                "timestamp": str(int(time.time()))
            },
            "message": {
                "order": {
                    "provider": {
                        "id": provider_id
                    },
                    "items": [
                        {
                            "id": item_id
                        }
                    ],
                    "fulfillments": [
                        {
                            "id": fulfillment_id,
                            "customer": {
                                "person": {
                                    "name": "Lisa"
                                },
                                "contact": {
                                    "phone": "876756454",
                                    "email": "LisaS@mailinator.com"
                                }
                            }
                        }
                    ]
                }
            }
        }

        print(f"[TOOL] Sending confirm order request: {payload}")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        chat_history = get_chat_history(session_id)
        chat_history.messages.append(AIMessage(content=json.dumps({"confirm_order_response": data})))

        return data

    except requests.exceptions.RequestException as e:
        return ConfirmOrderResponse(
            success=False,
            message=f"❌ Failed to confirm the order due to network error: {str(e)}",
            product_id=item_id
        )
    except Exception as e:
        return ConfirmOrderResponse(
            success=False,
            message=f"❌ Failed to confirm the order: {str(e)}",
            product_id=item_id
        )




confirm_tool = StructuredTool.from_function(
    func=confirm_order_fn,
    name="beckn_confirm_api",
    description="Confirm an order by providing product_id.",
    args_schema=ConfirmOrderArgs,
    return_direct=False,
)









# Tools list
tools = [
    search_tool,
    select_tool,
    confirm_tool
]

# Load OpenAI LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# Create the tool-using agent
retail_agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=retail_agent_prompt
)

# Agent executor (you can inject memory later here)
retail_agent_executor = AgentExecutor.from_agent_and_tools(
    agent=retail_agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    
)
