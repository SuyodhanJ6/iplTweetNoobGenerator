#!/usr/bin/env python
"""
Tweet Generator MCP Server - Provides tweet generation services via MCP protocol.
"""

import os
import sys
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP
from mcp.server import Server
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server.sse import SseServerTransport
import uvicorn

# Import the IPL tweet prompt tool
from tools.ipl_tweet_prompt_rohit_4_6 import RohitSharmaIPLTweetPrompt

# Load environment variables
load_dotenv()

# Create MCP server
mcp = FastMCP("TweetTools")

class IPLTweetPromptRequest(BaseModel):
    """Request model for IPL viral tweet prompt"""
    content_dump: str

class IPLTweetPromptResponse(BaseModel):
    """Response model for IPL viral tweet prompt"""
    prompt: str
    error: Optional[str] = None

@mcp.tool()
async def get_rohit_sharma_boundary_viral_tweet_prompt(request: IPLTweetPromptRequest) -> IPLTweetPromptResponse:
    """
    Get a structured prompt for generating viral IPL cricket tweets about Rohit Sharma's boundaries.
    
    Args:
        request: An object containing the cricket moment details.
        
    Returns:
        An object containing the complete structured prompt for generating viral tweets about Rohit's boundaries.
    """
    try:
        # Get the full prompt from the prompt tool
        prompt = RohitSharmaIPLTweetPrompt.get_viral_prompt_rohit_sharma_4_6(request.content_dump)
        
        print(f"Generated Rohit Sharma boundary viral tweet prompt for: {request.content_dump[:50]}...")
        return IPLTweetPromptResponse(
            prompt=prompt
        )
        
    except Exception as e:
        error_msg = f"Error generating prompt: {str(e)}"
        print(error_msg)
        import traceback
        print(traceback.format_exc())
        return IPLTweetPromptResponse(
            prompt="",
            error=error_msg
        )

@mcp.tool()
async def get_rohit_sharma_boundary_one_liner_tweet_prompt(request: IPLTweetPromptRequest) -> IPLTweetPromptResponse:
    """
    Get a structured prompt for generating ultra-short one-liner IPL cricket tweets (7-8 words max) about Rohit Sharma's boundaries.
    
    Args:
        request: An object containing the cricket moment details.
        
    Returns:
        An object containing the complete structured prompt for generating one-liner viral tweets about Rohit's boundaries.
    """
    try:
        # Get the one-liner prompt from the prompt tool
        prompt = RohitSharmaIPLTweetPrompt.get_one_liner_prompt_rohit_sharma_4_6(request.content_dump)
        
        print(f"Generated Rohit Sharma boundary one-liner tweet prompt for: {request.content_dump[:50]}...")
        return IPLTweetPromptResponse(
            prompt=prompt
        )
        
    except Exception as e:
        error_msg = f"Error generating one-liner prompt: {str(e)}"
        print(error_msg)
        import traceback
        print(traceback.format_exc())
        return IPLTweetPromptResponse(
            prompt="",
            error=error_msg
        )

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette app with SSE transport for the MCP server."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        """Handle SSE connections"""
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

def main():
    """Run the Tweet Generator MCP Server"""
    import argparse

    # Get MCP server instance from FastMCP
    mcp_server = mcp._mcp_server

    parser = argparse.ArgumentParser(description="Tweet Generator MCP Server")
    parser.add_argument("--port", type=int, default=3002, help="Port for server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host for server")
    
    args = parser.parse_args()
    
    print(f"Starting Tweet Generator MCP Server on {args.host}:{args.port}")
    print(f"Server-Sent Events endpoint: http://{args.host}:{args.port}/sse")
    
    # Create Starlette app with SSE transport
    starlette_app = create_starlette_app(mcp_server, debug=True)
    
    # Run the server with uvicorn
    uvicorn.run(
        starlette_app,
        host=args.host,
        port=args.port,
    )

if __name__ == "__main__":
    main()
