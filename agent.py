#!/usr/bin/env python3
"""Strudel Music Assistant Agent - CLI Testing Interface"""

from pydantic_ai import Agent, RunContext
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.messages import ModelMessage, SystemPromptPart, UserPromptPart

from dotenv import load_dotenv
import os
import argparse
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import traceback
import asyncio

load_dotenv()

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Strudel Music Assistant - Live Coding Agent")
    parser.add_argument(
        "--model",
        type=str,
        default="x-ai/grok-4-fast",
        help="Model identifier to use with OpenRouter (default: x-ai/grok-4-fast)"
    )
    return parser.parse_args()

# Get command line arguments
args = parse_args()

# Set up OpenRouter based model
API_KEY = os.getenv('OPENROUTER_API_KEY')
model = OpenAIModel(
    args.model,
    provider=OpenAIProvider(
        base_url='https://openrouter.ai/api/v1',
        api_key=API_KEY
    ),
)

# MCP Server setup (no special env vars needed for filesystem-based MVP)
env = {}

mcp_servers = [
    MCPServerStdio('python', ['./mcp_server.py'], env=env),
]

# Function to filter message history
def filtered_message_history(
    result: Optional[AgentRunResult],
    limit: Optional[int] = None,
    include_tool_messages: bool = True
) -> Optional[List[Dict[str, Any]]]:
    """
    Filter and limit the message history from an AgentRunResult.

    Args:
        result: The AgentRunResult object with message history
        limit: Optional int, if provided returns only system message + last N messages
        include_tool_messages: Whether to include tool messages in the history

    Returns:
        Filtered list of messages in the format expected by the agent
    """
    if result is None:
        return None

    # Get all messages
    messages: list[ModelMessage] = result.all_messages()

    # Extract system message (always the first one with role="system")
    system_message = next((msg for msg in messages if type(msg.parts[0]) == SystemPromptPart), None)

    # Filter non-system messages
    non_system_messages = [msg for msg in messages if type(msg.parts[0]) != SystemPromptPart]

    # Apply tool message filtering if requested
    if not include_tool_messages:
        from pydantic_ai.messages import ToolCallPart, ToolReturnPart
        non_system_messages = [msg for msg in non_system_messages if not any(isinstance(part, ToolCallPart) or isinstance(part, ToolReturnPart) for part in msg.parts)]

    # Find the most recent UserPromptPart before applying limit
    latest_user_prompt_part = None
    latest_user_prompt_index = -1
    for i, msg in enumerate(non_system_messages):
        for part in msg.parts:
            if isinstance(part, UserPromptPart):
                latest_user_prompt_part = part
                latest_user_prompt_index = i

    # Apply limit if specified, but ensure paired tool calls and returns stay together
    if limit is not None and limit > 0:
        from pydantic_ai.messages import ToolCallPart, ToolReturnPart
        # Identify tool call IDs and their corresponding return parts
        tool_call_ids = {}
        tool_return_ids = set()

        for i, msg in enumerate(non_system_messages):
            for part in msg.parts:
                if isinstance(part, ToolCallPart):
                    tool_call_ids[part.tool_call_id] = i
                elif isinstance(part, ToolReturnPart):
                    tool_return_ids.add(part.tool_call_id)

        # Take the last 'limit' messages but ensure we include paired messages
        if len(non_system_messages) > limit:
            included_indices = set(range(len(non_system_messages) - limit, len(non_system_messages)))

            # Include any missing tool call messages for tool returns that are included
            for i, msg in enumerate(non_system_messages):
                if i in included_indices:
                    for part in msg.parts:
                        if isinstance(part, ToolReturnPart) and part.tool_call_id in tool_call_ids:
                            included_indices.add(tool_call_ids[part.tool_call_id])

            # Check if the latest UserPromptPart would be excluded by the limit
            if (latest_user_prompt_index >= 0 and
                latest_user_prompt_index not in included_indices and
                latest_user_prompt_part is not None and
                system_message is not None):
                # Find if system_message already has a UserPromptPart
                user_prompt_index = next((i for i, part in enumerate(system_message.parts)
                                       if isinstance(part, UserPromptPart)), None)

                if user_prompt_index is not None:
                    # Replace existing UserPromptPart
                    system_message.parts[user_prompt_index] = latest_user_prompt_part
                else:
                    # Add new UserPromptPart to system message
                    system_message.parts.append(latest_user_prompt_part)

            # Create a new list with only the included messages
            non_system_messages = [msg for i, msg in enumerate(non_system_messages) if i in included_indices]

    # Combine system message with other messages
    result_messages = []
    if system_message:
        result_messages.append(system_message)
    result_messages.extend(non_system_messages)

    return result_messages

# Set up Agent with Server
agent_name = "LiveStrudler"
def load_agent_prompt(agent: str):
    """Loads given agent replacing `time_now` var with current time"""
    print(f"Loading {agent}")
    time_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    agent_file = os.path.join(os.path.dirname(__file__), "agents", f"{agent}.md")
    with open(agent_file, "r") as f:
        agent_prompt = f.read()
    agent_prompt = agent_prompt.replace('{time_now}', time_now)
    return agent_prompt

# Load up the agent system prompt
agent_prompt = load_agent_prompt(agent_name)

# Display the selected model
print(f"Using model: {args.model}")

agent = Agent(model, mcp_servers=mcp_servers, system_prompt=agent_prompt)

async def main():
    """CLI testing in a conversation with the agent"""
    async with agent.run_mcp_servers():

        result: AgentRunResult = None

        # Chat Loop
        while True:
            if result:
                print(f"\n{result.output}")
            user_input = input("\n> ")
            err = None
            for i in range(0, 2):
                try:
                    # Use the filtered message history
                    result: AgentRunResult = await agent.run(
                        user_input,
                        message_history=filtered_message_history(
                            result,
                            limit=24,                  # Last 24 non-system messages
                            include_tool_messages=True # Include tool messages
                        )
                    )
                    break
                except Exception as e:
                    err = e
                    traceback.print_exc()
                    await asyncio.sleep(2)
            if result is None:
                print(f"\nError {err}. Try again...\n")
                continue
            elif len(result.output) == 0:
                continue


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
