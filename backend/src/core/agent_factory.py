"""Agent factory for Strudel Agent."""

import os
import logging
from uuid import UUID
from pathlib import Path
from datetime import datetime

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
# TODO: MCP integration not yet available in pydantic-ai
# from pydantic_ai_mcp import MCPServerStdio

from src.db.models import SessionCreate

logger = logging.getLogger(__name__)

def create_agent(session_id: UUID, config: SessionCreate) -> Agent:
    """Create a Pydantic-AI agent for Strudel.
    
    Args:
        session_id: Session UUID
        config: Session configuration
    
    Returns:
        Configured Agent instance
    """
    # Load agent prompt
    prompt = load_agent_prompt("LiveStrudler")
    
    # Create model (OpenRouter only)
    model = create_model(config)
    
    # Create MCP servers (temporarily disabled)
    # mcp_servers = create_mcp_servers(session_id, config)
    
    # Create agent
    agent = Agent(
        model=model,
        # mcp_servers=mcp_servers,  # Temporarily disabled
        system_prompt=prompt,
    )
    
    logger.info(f"Created agent for session {session_id}: {config.agent_name}")
    return agent

def create_model(config: SessionCreate) -> OpenAIModel:
    """Create OpenAI model (via OpenRouter).
    
    Args:
        config: Session configuration
    
    Returns:
        OpenAIModel instance
    """
    model_name = "x-ai/grok-4-fast"
    
    # Use OpenRouter
    model = OpenAIModel(
        model_name,
        provider=OpenAIProvider(
            base_url='https://openrouter.ai/api/v1',
            api_key=os.getenv('OPENROUTER_API_KEY')
        )
    )
    
    logger.info(f"Created model: {model_name} via OpenRouter")
    return model

def create_mcp_servers(session_id: UUID, config: SessionCreate) -> list:
    """Create MCP servers for agent.
    
    Args:
        session_id: Session UUID
        config: Session configuration
    
    Returns:
        List of MCPServerStdio instances
    """
    # TODO: Implement MCP server integration
    # mcp_servers = [
    #     # Hypergraph memory
    #     MCPServerStdio(
    #         'python',
    #         ['hypergraph_memory/src/server.py'],
    #         env={
    #             'HYPERGRAPH_MEMORY_FILE': f"memory/sessions/{session_id}/memory.json",
    #             'SESSION_ID': str(session_id),
    #         }
    #     ),
    #     
    #     # Strudel-specific tools
    #     MCPServerStdio(
    #         'python',
    #         ['backend/src/mcp/strudel_server.py'],
    #         env={
    #             'STRUDEL_SESSION_ID': str(session_id),
    #             'STRUDEL_PROJECT_ID': config.project_id,
    #             'STRUDEL_ITEM_TYPE': config.session_type,
    #             'STRUDEL_ITEM_ID': config.item_id,
    #         }
    #     ),
    # ]
    
    logger.warning("MCP server integration temporarily disabled")
    return []

def load_agent_prompt(agent_name: str) -> str:
    """Load agent system prompt from file.
    
    Args:
        agent_name: Agent name (e.g., 'strudel')
    
    Returns:
        System prompt string
    """
    prompt_path = Path(f"agents/{agent_name}.md")
    
    if not prompt_path.exists():
        logger.warning(f"Agent prompt not found: {prompt_path}")
        return f"You are {agent_name}, a helpful assistant."
    
    prompt = prompt_path.read_text()
    
    # Replace time variable
    prompt = prompt.replace('{time_now}', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    logger.info(f"Loaded agent prompt from {prompt_path}")
    return prompt
