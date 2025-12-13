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

client = Client(
    base_url=BASE_URL,
    api_key=API_KEY
)

def unregister_customer_mcp():
    """Unregister the customer MCP server"""
    logger.info("Unregistering customer MCP toolgroup")
    client.toolgroups.unregister(
        toolgroup_id="customer_mcp"
    )
    logger.info("Customer MCP toolgroup unregistered successfully")
    return True


if __name__ == "__main__":
    unregister_customer_mcp()
