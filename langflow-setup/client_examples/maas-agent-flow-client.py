import requests
import os
import uuid

# Pull from environment variables
api_key = os.environ.get('LANGFLOW_API_KEY')
langflow_url = os.environ.get('LANGFLOW_URL')
flow_id = os.environ.get('LANGFLOW_FLOW_ID', 'b6a5c46b-f254-459b-ae22-3e365f0aa465')

if not api_key:
    raise ValueError("LANGFLOW_API_KEY environment variable is not set")
if not langflow_url:
    raise ValueError("LANGFLOW_URL environment variable is not set")

url = f"{langflow_url}/api/v1/run/{flow_id}"

# Request payload configuration
payload = {
    "output_type": "chat",
    "input_type": "chat",
    "input_value": "hello world!"
}
payload["session_id"] = str(uuid.uuid4())

headers = {"x-api-key": api_key}

try:
    # Send API request
    response = requests.request("POST", url, json=payload, headers=headers)
    response.raise_for_status()  # Raise exception for bad status codes

    # Print response
    print(response.text)

except requests.exceptions.RequestException as e:
    print(f"Error making API request: {e}")
except ValueError as e:
    print(f"Error parsing response: {e}")