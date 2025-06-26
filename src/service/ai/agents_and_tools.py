# File: agents_and_tools.py

import json
import os
import time
from typing import Optional, Type, List
import uuid

from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain import hub
from dotenv import load_dotenv
import requests
from service.ai.prompts_and_model import retail_agent_prompt
from service.schemas.product import ConfirmOrderResponse, SearchProductResponse, ProductItem, ProviderInfo, SelectProductResponse

load_dotenv()

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

def search_product_fn(query: str) -> str:
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

        response_text += "Please select a product by typing the number (e.g., 1, 2, 3)."

        response_text += (
            "\n\n[INTERNAL_METADATA] product_selection_map = " +
            json.dumps(product_selection_map)
        )

        return response_text

    except Exception as e:
        return f"Oops! Something went wrong while searching for products: {e}"

def select_product_fn(product_id: str, provider_id: str, context: Optional[dict] = None) -> SelectProductResponse:
    print(f"[TOOL] Selecting product: {product_id} from provider: {provider_id}")

    try:
        url = "https://bap-ps-client-deg.becknprotocol.io/select"
        headers = {"Content-Type": "application/json"}

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

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        return SelectProductResponse(
            success=True,
            message=f"✅ Product with ID `{product_id}` from provider `{provider_id}` has been selected successfully.",
            context=ctx
        )

    except Exception as e:
        return SelectProductResponse(
            success=False,
            message=f"❌ Failed to select the product due to: {str(e)}",
            context=context
        )

def confirm_order_fn(product_id: str) -> ConfirmOrderResponse:
    print(f"[TOOL] Confirming order for: {product_id}")

    try:
        order_id = "ORD1234"

        return ConfirmOrderResponse(
            success=True,
            message=f"✅ Order placed successfully for product ID `{product_id}`.",
            order_id=order_id,
            product_id=product_id
        )

    except Exception as e:
        return ConfirmOrderResponse(
            success=False,
            message=f"❌ Failed to confirm the order: {str(e)}",
            product_id=product_id
        )

search_tool = StructuredTool.from_function(
    func=search_product_fn,
    name="search_products_api",
    description="Search for products using Beckn API and return a formatted product list.",
    args_schema=SearchProductArgs,
    return_direct=False,
)

select_tool = StructuredTool.from_function(
    func=select_product_fn,
    name="select_product_api",
    description="Select a product by product_id and provider_id.",
    args_schema=SelectProductArgs,
    return_direct=False,
)

confirm_tool = StructuredTool.from_function(
    func=confirm_order_fn,
    name="confirm_order_api",
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
