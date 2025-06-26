# File: agents_and_tools.py

import os
import time
from typing import Optional, Type, List
import uuid

from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain import hub
from dotenv import load_dotenv
import requests
from service.ai.prompts_and_model import retail_agent_prompt

load_dotenv()

### ----------------------------------------
### 🧠 1. Define tool schemas
### ----------------------------------------

class SearchProductArgs(BaseModel):
    query: str = Field(description="Product name or keyword to search")


class SelectProductArgs(BaseModel):
    product_id: str = Field(description="The ID of the product to select")
    provider_id: str = Field(description="The ID of the product's provider")
    context: Optional[dict] = Field(
        None, description="Context from the previous Beckn search call"
    )


class ConfirmOrderArgs(BaseModel):
    product_id: str = Field(description="ID of the product to confirm order for")

class SearchProductTool(BaseTool):
    name: str = "search_products_api"
    description: str = "Search for products using Beckn API and return a human-friendly list with product details"
    args_schema: Type[BaseModel] = SearchProductArgs

    def _run(self, query: str) -> str:
        print(f"[TOOL] Searching Beckn for: {query}")

        url = "https://bap-ps-client-deg.becknprotocol.io/search"
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "context": {
                "domain": "deg:retail",
                "action": "search",
                "location": {
                    "country": {"code": "USA"},
                    "city": {"code": "NANP:628"}
                },
                "version": "1.1.0",
                "bap_id": "bap-ps-network-deg.becknprotocol.io",
                "bap_uri": "https://bap-ps-network-deg.becknprotocol.io",
                "bpp_id": "bpp-ps-network-deg.becknprotocol.io",
                "bpp_uri": "https://bpp-ps-network-deg.becknprotocol.io",
                "transaction_id": str(uuid.uuid4()),
                "message_id": str(uuid.uuid4()),
                "timestamp": str(int(time.time()))
            },
            "message": {
                "intent": {
                    "item": {
                        "descriptor": {"name": query}
                    }
                }
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            items = []
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
                            items.append({
                                "id": item_id,
                                "name": name,
                                "price": price,
                                "currency": currency,
                                "rating": rating,
                                "provider": {
                                    "id": provider_id,
                                    "name": provider_name
                                }
                            })

            if not items:
                return "Sorry, I couldn't find any matching products. Please try a different query."

            # Build user-friendly output
            response_text = "Here are some products I found:\n\n"
            for idx, item in enumerate(items, start=1):
                response_text += f"{idx}. {item['name']}\n   Price: {item['price']} {item['currency']} | Rating: {item['rating']}\n   Provider: {item['provider']['name']}\n\n"
            response_text += "\nPlease type the number of the product you'd like to select."

            # TODO: Store items mapping (idx to product_id) in conversation context/memory
            return response_text

        except Exception as e:
            return f"Oops! Something went wrong while searching for products: {e}"

class SelectProductTool(BaseTool):
    name: str = "select_product_api"
    description: str = "Select a product from the list using the product ID and provider ID"
    args_schema: Type[BaseModel] = SelectProductArgs

    def _run(self, product_id: str, provider_id: str, context: Optional[dict] = None) -> str:
        print(f"[TOOL] Selecting product: {product_id} from provider: {provider_id}")

        try:
            url = "https://bap-ps-client-deg.becknprotocol.io/select"
            headers = {"Content-Type": "application/json"}

            # Use context from previous search if available, else fallback to defaults
            ctx = context or {
                "domain": "deg:retail",
                "action": "select",
                "location": {
                    "country": {"code": "USA"},
                    "city": {"code": "NANP:628"}
                },
                "version": "1.1.0",
                "bap_id": "bap-ps-network-deg.becknprotocol.io",
                "bap_uri": "https://bap-ps-network-deg.becknprotocol.io",
                "bpp_id": "bpp-ps-network-deg.becknprotocol.io",
                "bpp_uri": "https://bpp-ps-network-deg.becknprotocol.io"
            }

            ctx.update({
                "transaction_id": str(uuid.uuid4()),
                "message_id": str(uuid.uuid4()),
                "timestamp": str(int(time.time()))
            })

            payload = {
                "context": ctx,
                "message": {
                    "order": {
                        "provider": {
                            "id": provider_id
                        },
                        "items": [
                            {
                                "id": product_id
                            }
                        ]
                    }
                }
            }

            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Optional: Check for expected keys or success indicators
            return f"✅ Product with ID `{product_id}` from provider `{provider_id}` has been selected successfully."

        except Exception as e:
            return f"❌ Failed to select the product due to: {str(e)}"


class ConfirmOrderTool(BaseTool):
    name: str = "confirm_order_api"
    description: str = "Confirm the order for a selected product"
    args_schema: Type[BaseModel] = ConfirmOrderArgs

    def _run(self, product_id: str) -> str:
        print(f"[TOOL] Confirming order for: {product_id}")
        return f"Order placed successfully for {product_id}. Order ID: ORD1234"

### ----------------------------------------
### 🤖 3. Build the agent
### ----------------------------------------

# Tools list
tools = [
    SearchProductTool(),
    SelectProductTool(),
    ConfirmOrderTool()
]

# Load default agent prompt from LangChain hub
# prompt = hub.pull("hwchase17/openai-tools-agent")

# Load OpenAI LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

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
