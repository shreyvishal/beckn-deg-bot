# File: agents_and_tools.py

import os
import time
from typing import Type, List
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
    query: str = Field(description="Query to search for products")


class SelectProductArgs(BaseModel):
    product_id: str = Field(description="ID of the selected product")


class ConfirmOrderArgs(BaseModel):
    product_id: str = Field(description="ID of the product to confirm order for")

class SearchProductTool(BaseTool):
    name: str = "search_products_api"
    description: str = "Search for products using Beckn API and return a list of product names"
    args_schema: Type[BaseModel] = SearchProductArgs

    def _run(self, query: str) -> str:
        print(f"[TOOL] Searching Beckn for: {query}")

        url = "https://bap-ps-client-deg.becknprotocol.io/search"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "context": {
                "domain": "deg:retail",
                "action": "search",
                "location": {
                    "country": {
                        "code": "USA"
                    },
                    "city": {
                        "code": "NANP:628"
                    }
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
                        "descriptor": {
                            "name": query
                        }
                    }
                }
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Parse item names from response
            items = []
            catalog = data.get("message", {}).get("catalog", {})
            providers = catalog.get("providers", [])
            for provider in providers:
                for item in provider.get("items", []):
                    name = item.get("descriptor", {}).get("name")
                    id_ = item.get("id")
                    if name and id_:
                        items.append(f"- {name} (ID: {id_})")

            if items:
                return "Found the following products:\n" + "\n".join(items)
            else:
                return "No products found for the given query."

        except Exception as e:
            return f"Error while calling Beckn search API: {e}"

class SelectProductTool(BaseTool):
    name: str = "select_product_api"
    description: str = "Select a product from the list using the product ID"
    args_schema: Type[BaseModel] = SelectProductArgs

    def _run(self, product_id: str) -> str:
        print(f"[TOOL] Selecting product: {product_id}")
        return f"Product with ID {product_id} has been selected."


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
