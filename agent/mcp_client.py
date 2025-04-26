#!/usr/bin/env python
"""
MCP Client Manager - Handles connections to multiple MCP servers
"""

import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.tools import BaseTool

# Load environment variables from .env file
load_dotenv()

class MCPClientManager:
    """Manages connections to multiple MCP servers."""
    
    def __init__(self):
        """Initialize the MCP Client Manager."""
        self.mcp_client = None
        self.tweet_mcp_port = os.getenv("TWEET_MCP_PORT", "3002")
        self.mcp_host = os.getenv("MCP_HOST", "tweet-mcp")
        self.tools = []
    
    async def setup(self):
        """Set up connections to all MCP servers."""
        try:
            # Define MCP server URLs
            tweet_mcp_url = f"http://{self.mcp_host}:{self.tweet_mcp_port}/sse"
            
            # Connect to MCP servers
            self.mcp_client = MultiServerMCPClient(
                {
                    "tweettools": {
                        "url": tweet_mcp_url,
                        "transport": "sse",
                    }
                }
            )
            
            await self.mcp_client.__aenter__()
            
            # Get tools from the MCP servers
            self.tools = self.mcp_client.get_tools()
            
            print(f"Connected to MCP servers:")
            print(f"- Tweet MCP: {tweet_mcp_url}")
            print(f"Total tools loaded: {len(self.tools)}")
            
        except Exception as e:
            print(f"Error connecting to MCP servers: {str(e)}")
            print("Make sure the Tweet MCP server is running at the specified URL")
            raise
    
    def get_tools(self) -> List[BaseTool]:
        """Get all tools from the connected MCP servers.
        
        Returns:
            List of available tools
        """
        return self.tools
    
    async def close(self):
        """Clean up resources."""
        if self.mcp_client:
            await self.mcp_client.__aexit__(None, None, None)
