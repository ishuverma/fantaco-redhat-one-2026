import json

from langchain_openai import ChatOpenAI
from pydantic.v1 import SecretStr

from langflow.custom import Component
from langflow.io import DropdownInput, FloatInput, IntInput, MessageInput, Output, SecretStrInput, StrInput
from langflow.schema.message import Message

# MaaS Models
models = json.loads('''
{
  "data": [
    {"id": "nomic-embed-text-v1-5"},
    {"id": "granite-4-0-h-tiny"},
    {"id": "Llama-Guard-3-1B"},
    {"id": "llama-scout-17b"},
    {"id": "qwen3-14b"}
  ]
}
''')

MAAS_MODELS = [item["id"] for item in models["data"]]


class MaaSModelComponent(Component):
    display_name = "MaaS Model"
    description = "Connects to MaaS (LiteLLM) via OpenAI-compatible API."
    icon = "server"
    name = "MaaSModel"

    inputs = [
        StrInput(
            name="api_base",
            display_name="API Base URL",
            info="The base URL of the MaaS/LiteLLM server",
            value="https://litellm-prod.apps.maas.redhatworkshops.io/v1",
            required=True,
        ),
        DropdownInput(
            name="model_name",
            display_name="Model Name",
            options=MAAS_MODELS,
            value="qwen3-14b",
            info="Select a model from MaaS",
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            info="API Key for MaaS/LiteLLM",
            required=True,
        ),
        FloatInput(
            name="temperature",
            display_name="Temperature",
            info="Controls randomness (0.0 = deterministic, 1.0 = creative)",
            value=0.1,
        ),
        IntInput(
            name="max_tokens",
            display_name="Max Tokens",
            info="Maximum tokens to generate (0 = unlimited)",
            value=4096,
            advanced=True,
        ),
        IntInput(
            name="timeout",
            display_name="Timeout (seconds)",
            info="Request timeout",
            value=120,
            advanced=True,
        ),
        MessageInput(
            name="input_value",
            display_name="Input",
            info="Input message for direct chat (optional)",
            required=False,
        ),
    ]

    outputs = [
        Output(
            display_name="Language Model",
            name="model_output",
            method="build_model",
            info="Connect this to an Agent's Language Model input",
        ),
        Output(
            display_name="Text Response",
            name="text_output",
            method="text_response",
            info="Direct text response (for non-Agent use)",
        ),
    ]

    def build_model(self) -> ChatOpenAI:
        """Build and return the model as a LangChain ChatOpenAI instance."""
        api_key = self.api_key if self.api_key else "EMPTY"

        # Convert max_tokens to int if it's a string
        max_tokens_value = None
        if self.max_tokens:
            try:
                max_tokens_int = int(self.max_tokens)
                if max_tokens_int > 0:
                    max_tokens_value = max_tokens_int
            except (ValueError, TypeError):
                pass

        model = ChatOpenAI(
            api_key=api_key,
            model=self.model_name,
            base_url=self.api_base,
            temperature=float(self.temperature) if self.temperature else 0.1,
            max_tokens=max_tokens_value,
            timeout=int(self.timeout) if self.timeout else 120,
        )

        return model

    def text_response(self) -> Message:
        """Generate a response directly (for non-Agent use cases)."""
        if not self.input_value:
            return Message(text="No input provided")

        model = self.build_model()

        # Get the input text
        if hasattr(self.input_value, 'text'):
            input_text = self.input_value.text
        else:
            input_text = str(self.input_value)

        # Generate response
        response = model.invoke(input_text)

        return Message(text=response.content)
