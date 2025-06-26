from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.tools import tool
from service.ai.prompts_and_model import retail_agent_model, retail_agent_prompt


@tool
def search_products_api(query: str) -> list:
    """Search for products by query and return a list of available items."""
    # Replace with your actual API logic
    return [
        {"id": "prod1", "name": "Laptop"},
        {"id": "prod2", "name": "Smartphone"},
    ]

@tool
def select_product_api(product_id: str) -> str:
    """Select a product from the list of available items."""
    return f"Product {product_id} selected"

@tool
def confirm_order_api(product_id: str) -> str:
    """Confirm an order for a product from the list of available items."""
    return f"Order {product_id} confirmed"

# tools
tools = [search_products_api, select_product_api, confirm_order_api]

# Create the agent
retail_agent = create_openai_functions_agent(
    llm=retail_agent_model,
    tools=tools,
    prompt=retail_agent_prompt
)

# agent executor
retail_agent_executor = AgentExecutor(agent=retail_agent, tools=tools, verbose=True)
