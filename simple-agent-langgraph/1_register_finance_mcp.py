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
FINANCE_MCP_SERVER_URL = os.getenv("FINANCE_MCP_SERVER_URL")

client = Client(
    base_url=BASE_URL,
    api_key=API_KEY
)

def register_finance_mcp():
    """Register the finance MCP server"""
    logger.info("Registering finance MCP server at %s", FINANCE_MCP_SERVER_URL)
    client.toolgroups.register(
        toolgroup_id="finance_mcp",
        provider_id="model-context-protocol",
        mcp_endpoint={"uri": FINANCE_MCP_SERVER_URL}
    )
    logger.info("Finance MCP server registered successfully")
    return True


if __name__ == "__main__":
    register_finance_mcp()
