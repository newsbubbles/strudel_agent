"""WebSocket connection manager."""

import asyncio
import logging
from typing import Dict, Optional, Any
from uuid import uuid4
from fastapi import WebSocket
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class SessionContext(BaseModel):
    """Session context for WebSocket connections."""
    session_id: str
    metadata: Dict[str, Any] = {}

class ConnectionManager:
    """Manages WebSocket connections and message routing."""
    
    def __init__(self):
        # session_id -> {connection_id -> WebSocket}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        
        # session_id -> SessionContext
        self.session_contexts: Dict[str, SessionContext] = {}
        
        # session_id -> {request_id -> Future}
        self.pending_tool_requests: Dict[str, Dict[str, asyncio.Future]] = {}
    
    async def connect(
        self,
        websocket: WebSocket,
        session_id: str,
        connection_type: str = 'pwa'
    ) -> tuple[SessionContext, str]:
        """Register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            session_id: Session ID
            connection_type: 'pwa' or 'mcp'
        
        Returns:
            (SessionContext, connection_id)
        """
        # Generate unique connection ID
        connection_id = f"{connection_type}-{uuid4().hex[:8]}"
        
        # Store connection
        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}
        self.active_connections[session_id][connection_id] = websocket
        
        # Get or create session context
        if session_id in self.session_contexts:
            context = self.session_contexts[session_id]
        else:
            context = SessionContext(session_id=session_id)
            self.session_contexts[session_id] = context
        
        logger.info(f"Connection {connection_id} registered for session {session_id}")
        return context, connection_id
    
    def disconnect(self, session_id: str, connection_id: Optional[str] = None):
        """Unregister a WebSocket connection.
        
        Args:
            session_id: Session ID
            connection_id: Connection ID (if None, removes all connections)
        """
        if session_id not in self.active_connections:
            return
        
        if connection_id:
            # Remove specific connection
            self.active_connections[session_id].pop(connection_id, None)
            logger.info(f"Connection {connection_id} disconnected from session {session_id}")
            
            # Clean up session if no more connections
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
                self.session_contexts.pop(session_id, None)
                self.pending_tool_requests.pop(session_id, None)
        else:
            # Remove all connections for session
            del self.active_connections[session_id]
            self.session_contexts.pop(session_id, None)
            self.pending_tool_requests.pop(session_id, None)
            logger.info(f"All connections disconnected from session {session_id}")
    
    async def send_message(
        self,
        session_id: str,
        message: Dict[str, Any],
        target: str = 'pwa'
    ) -> bool:
        """Send message to WebSocket connections.
        
        Args:
            session_id: Session ID
            message: Message to send
            target: 'pwa', 'mcp', or 'all'
        
        Returns:
            True if sent successfully
        """
        if session_id not in self.active_connections:
            logger.warning(f"No connections for session {session_id}")
            return False
        
        connections = self.active_connections[session_id]
        
        # Determine targets
        if target == 'all':
            targets = list(connections.items())
        else:
            # Find connections matching type prefix
            targets = [
                (conn_id, ws) for conn_id, ws in connections.items()
                if conn_id.startswith(f"{target}-")
            ]
        
        if not targets:
            logger.warning(f"No {target} connections for session {session_id}")
            return False
        
        # Send to all matched connections
        for conn_id, ws in targets:
            try:
                await ws.send_json(message)
                logger.info(f"Sent message type={message.get('type')} to {conn_id}")
            except Exception as e:
                logger.error(f"Error sending to {conn_id}: {e}")
                # Don't disconnect here, let the main loop handle it
        
        return True
    
    async def send_handshake_ack(
        self,
        session_id: str,
        connection_id: str,
        is_reconnect: bool = False,
        connection_type: str = 'pwa',
        session_info: Optional[Dict[str, Any]] = None
    ):
        """Send handshake acknowledgment."""
        await self.send_message(
            session_id,
            {
                'type': 'handshake_ack',
                'session_id': session_id,
                'connection_id': connection_id,
                'is_reconnect': is_reconnect,
                'session_info': session_info or {},
            },
            target=connection_type
        )
    
    async def send_tool_request(
        self,
        session_id: str,
        tool_name: str,
        parameters: Dict[str, Any],
        timeout_ms: int = 30000
    ) -> Any:
        """Send tool request to PWA and wait for response.
        
        Args:
            session_id: Session ID
            tool_name: Tool name
            parameters: Tool parameters
            timeout_ms: Timeout in milliseconds
        
        Returns:
            Tool response data
        
        Raises:
            RuntimeError: If request fails
            asyncio.TimeoutError: If request times out
        """
        request_id = str(uuid4())
        
        # Create future for response
        future = asyncio.get_running_loop().create_future()
        if session_id not in self.pending_tool_requests:
            self.pending_tool_requests[session_id] = {}
        self.pending_tool_requests[session_id][request_id] = future
        
        # Send tool request to PWA
        await self.send_message(
            session_id,
            {
                'type': 'tool_request',
                'request_id': request_id,
                'tool_name': tool_name,
                'parameters': parameters,
                'timeout_ms': timeout_ms,
            },
            target='pwa'
        )
        
        # Wait for response
        try:
            result = await asyncio.wait_for(future, timeout=timeout_ms/1000.0)
            return result
        finally:
            # Clean up
            if session_id in self.pending_tool_requests:
                self.pending_tool_requests[session_id].pop(request_id, None)
    
    async def handle_tool_response(self, session_id: str, response_data: Dict[str, Any]):
        """Handle tool response from client.
        
        Args:
            session_id: Session ID
            response_data: Response data with request_id, success, data/error
        """
        request_id = response_data.get('request_id')
        
        if (session_id in self.pending_tool_requests and
            request_id in self.pending_tool_requests[session_id]):
            future = self.pending_tool_requests[session_id][request_id]
            
            if response_data.get('success'):
                future.set_result(response_data.get('data'))
            else:
                future.set_exception(RuntimeError(response_data.get('error', 'Unknown error')))
        else:
            logger.warning(f"Received tool response for unknown request: {request_id}")

# Global connection manager instance
manager = ConnectionManager()
