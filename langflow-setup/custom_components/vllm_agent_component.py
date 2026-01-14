"""
vLLM Agent Component for Langflow

A custom Agent component that connects directly to vLLM (or any OpenAI-compatible API)
and can use tools from MCP servers or other tool components.

Upload this file via Langflow UI:
  Settings (gear icon) → Custom Components → Upload
"""

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool

from langflow.custom import Component
from langflow.io import (
    FloatInput,
    IntInput,
    MessageInput,
    MultilineInput,
    Output,
    SecretStrInput,
    StrInput,
    HandleInput,
)
from langflow.schema.message import Message


class VLLMAgentComponent(Component):
    display_name = "vLLM Agent"
    description = "An Agent that uses vLLM (or any OpenAI-compatible API) and can call tools."
    icon = "bot"
    name = "VLLMAgent"

    inputs = [
        # vLLM Connection Settings
        StrInput(
            name="api_base",
            display_name="vLLM API Base URL",
            info="The base URL of your vLLM server (e.g., https://litellm-prod.apps.example.com/v1)",
            value="https://litellm-prod.apps.maas.redhatworkshops.io/v1",
            required=True,
        ),
        StrInput(
            name="model_name",
            display_name="Model Name",
            info="The name of the model (e.g., qwen3-14b)",
            value="qwen3-14b",
            required=True,
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            info="API Key for the vLLM server",
            value="",
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
            info="Maximum tokens to generate",
            value=4096,
            advanced=True,
        ),

        # Agent Settings
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            info="Instructions for the agent",
            value="""You are a helpful assistant with access to tools.

When a user asks a question, think about whether you need to use a tool to answer it.
If you need information about customers, orders, or invoices, use the available tools.

Always be helpful and provide clear, concise answers.""",
        ),
        IntInput(
            name="max_iterations",
            display_name="Max Iterations",
            info="Maximum number of tool-calling iterations",
            value=10,
            advanced=True,
        ),

        # Inputs
        MessageInput(
            name="input_value",
            display_name="Input",
            info="The user's message",
            required=True,
        ),
        HandleInput(
            name="tools",
            display_name="Tools",
            info="Tools available to the agent (connect MCP or other tool components)",
            input_types=["Tool"],
            is_list=True,
            required=False,
        ),
    ]

    outputs = [
        Output(
            display_name="Response",
            name="response",
            method="run_agent",
            info="The agent's response",
        ),
    ]

    def build_model(self) -> ChatOpenAI:
        """Build the vLLM model using ChatOpenAI."""
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model_name,
            base_url=self.api_base,
            temperature=self.temperature,
            max_tokens=self.max_tokens if self.max_tokens > 0 else None,
        )

    def run_agent(self) -> Message:
        """Run the agent with the given input and tools."""

        # Get input text
        if hasattr(self.input_value, 'text'):
            input_text = self.input_value.text
        else:
            input_text = str(self.input_value)

        # Build the model
        llm = self.build_model()

        # Get tools (if any)
        tools_list = []
        if self.tools:
            if isinstance(self.tools, list):
                for tool in self.tools:
                    if isinstance(tool, list):
                        tools_list.extend(tool)
                    elif isinstance(tool, BaseTool):
                        tools_list.append(tool)
                    elif hasattr(tool, 'tools'):
                        # Handle tool components that have a .tools attribute
                        tools_list.extend(tool.tools)
            elif isinstance(self.tools, BaseTool):
                tools_list.append(self.tools)

        # If no tools, just use the LLM directly
        if not tools_list:
            response = llm.invoke([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": input_text}
            ])
            return Message(text=response.content)

        # Create agent with tools
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        try:
            # Try to create a tool-calling agent
            agent = create_tool_calling_agent(llm, tools_list, prompt)

            agent_executor = AgentExecutor(
                agent=agent,
                tools=tools_list,
                verbose=True,
                max_iterations=self.max_iterations,
                handle_parsing_errors=True,
            )

            result = agent_executor.invoke({
                "input": input_text,
                "chat_history": [],
            })

            output = result.get("output", str(result))
            return Message(text=output)

        except Exception as e:
            # If tool calling fails, fall back to direct LLM call
            self.log(f"Agent error: {e}. Falling back to direct LLM call.")

            # List available tools in the prompt
            tool_descriptions = "\n".join([
                f"- {t.name}: {t.description}" for t in tools_list
            ])

            enhanced_prompt = f"""{self.system_prompt}

Available tools:
{tool_descriptions}

Note: Tool calling encountered an error. Please answer based on your knowledge."""

            response = llm.invoke([
                {"role": "system", "content": enhanced_prompt},
                {"role": "user", "content": input_text}
            ])
            return Message(text=response.content)
