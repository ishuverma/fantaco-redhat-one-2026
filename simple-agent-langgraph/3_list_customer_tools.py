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


def list_customer_tools():
    """List all tools available in the customer MCP server"""

    logger.info("=" * 50)
    logger.info("Customer MCP Server Tools")
    logger.info("=" * 50)
    logger.info("MCP Server URL: %s", CUSTOMER_MCP_SERVER_URL)
    logger.info("")

    # These tools are defined in the customer MCP server implementation
    tools = [
        {
            "name": "search_customers",
            "description": "Search for customers by various fields with partial matching",
            "parameters": {
                "company_name": "Filter by company name (partial matching, optional)",
                "contact_name": "Filter by contact person name (partial matching, optional)",
                "contact_email": "Filter by contact email address (partial matching, optional)",
                "phone": "Filter by phone number (partial matching, optional)"
            }
        },
        {
            "name": "get_customer",
            "description": "Get customer by ID - Retrieves a single customer record by its unique identifier",
            "parameters": {
                "customer_id": "The unique 5-character identifier of the customer"
            }
        }
    ]

    for tool in tools:
        logger.info("Tool Name: %s", tool['name'])
        logger.info("Description: %s", tool['description'])
        logger.info("Parameters:")
        for param_name, param_desc in tool['parameters'].items():
            logger.info("  - %s: %s", param_name, param_desc)
        logger.info("-" * 50)

    logger.info("=" * 50)
    logger.info("Total tools: %d", len(tools))
    logger.info("=" * 50)

    return tools


if __name__ == "__main__":
    list_customer_tools()
