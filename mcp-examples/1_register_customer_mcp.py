from llama_stack_client import Client
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("LLAMA_STACK_BASE_URL")
API_KEY = os.getenv("LLAMA_STACK_API_KEY")
CUSTOMER_MCP_SERVER_URL = os.getenv("CUSTOMER_MCP_SERVER_URL")

client = Client(
    base_url=BASE_URL,
    api_key=API_KEY
)

def register_customer_mcp():
    """Register the customer MCP server"""
    logger.info("Registering customer MCP server at %s", CUSTOMER_MCP_SERVER_URL)
    client.toolgroups.register(
        toolgroup_id="customer_mcp",
        provider_id="model-context-protocol",
        mcp_endpoint={"uri": CUSTOMER_MCP_SERVER_URL}
    )
    logger.info("Customer MCP server registered successfully")
    return True


if __name__ == "__main__":
    register_customer_mcp()

