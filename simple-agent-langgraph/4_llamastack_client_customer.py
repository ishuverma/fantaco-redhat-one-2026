"""
Customer Search using Llama Stack Client

This script attempts to search for customers using the Llama Stack Client.

CURRENT STATUS:
- Successfully registers and lists the customer_mcp toolgroup
- tool_runtime.invoke_tool() doesn't have access to MCP toolgroup tools
- agent.turn.create() with toolgroups parameter returns error:
  "Toolgroup customer_mcp not found" despite it being in the available list

This appears to be a Llama Stack server configuration or API issue where
MCP toolgroups are registered but not properly accessible by the runtime.
"""

from llama_stack_client import Client
from llama_stack_client.types import AgentConfig
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
INFERENCE_MODEL = os.getenv("INFERENCE_MODEL")

client = Client(
    base_url=BASE_URL,
    api_key=API_KEY
)


def search_customer_by_email(email="thomashardy@example.com"):
    """Search for customer using Llama Stack tool_runtime to invoke customer MCP tool directly"""

    try:
        # Log initialization details
        logger.info("Llama Stack Base URL: %s", BASE_URL)
        logger.info("")

        # Execute tool invocation
        logger.info("=" * 50)
        logger.info("Searching for customer with email: %s", email)
        logger.info("=" * 50)

        # Invoke the search_customers tool directly
        result = client.tool_runtime.invoke_tool(
            tool_name="customer_mcp::search_customers",
            kwargs={"contact_email": email}
        )

        logger.info("Tool invocation result:")
        logger.info("%s", result)

        logger.info("=" * 50)
        logger.info("Customer search completed")
        logger.info("=" * 50)

        return result

    except Exception as e:
        logger.error("Error during customer search: %s", str(e))
        logger.exception("Stack trace:")
        return False


if __name__ == "__main__":
    search_customer_by_email()
