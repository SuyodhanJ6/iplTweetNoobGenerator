#!/usr/bin/env python
"""
IPL Tweet Agent - Agent for generating viral IPL cricket tweets using MCP servers
"""

import os
import asyncio
from typing import Dict, Any, Optional, List, Literal
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.prebuilt import create_react_agent

# Import the MCP client manager
from mcp_client import MCPClientManager

# Import prompt templates
from prompts.ipl_tweet_agent_prompt import IPLTweetAgentPrompts

class IPLTweetAgent:
    """Agent that generates viral IPL cricket tweets using MCP servers."""
    
    def __init__(self, model_name: str = "gpt-4o"):
        """Initialize the IPL Tweet Agent.
        
        Args:
            model_name: The name of the OpenAI model to use
        """
        self.model_name = model_name
        self.llm = None
        self.agent = None
        self.mcp_client_manager = None
        self.system_prompt = IPLTweetAgentPrompts.get_system_prompt()
    
    async def setup(self):
        """Set up the agent with the appropriate model and MCP tools."""
        # Initialize the OpenAI LLM
        self.llm = ChatOpenAI(model=self.model_name, api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize the MCP client manager
        self.mcp_client_manager = MCPClientManager()
        await self.mcp_client_manager.setup()
        
        # Get tools from the MCP client manager
        mcp_tools = self.mcp_client_manager.get_tools()
        print(f"Loaded {len(mcp_tools)} tools from MCP servers")
        
        # Create the ReAct agent with MCP tools
        self.agent = create_react_agent(
            self.llm,
            mcp_tools,
            prompt=self.system_prompt
        )
    
    async def generate_tweet(
        self, 
        cricket_moment: str, 
        tweet_type: Literal["standard", "one_liner"] = "standard"
    ) -> Dict[str, Any]:
        """Generate a viral tweet for an IPL cricket moment.
        
        Args:
            cricket_moment: Description of the cricket moment to tweet about
            tweet_type: Type of tweet to generate ("standard" or "one_liner")
            
        Returns:
            Generated tweet and analysis
        """
        if not self.agent:
            await self.setup()
            
        try:
            print(f"Generating viral {tweet_type} tweet for cricket moment: {cricket_moment[:50]}...")
            
            # Step 1: Get the viral tweet prompt using the appropriate MCP tool
            if tweet_type == "one_liner":
                prompt_request = IPLTweetAgentPrompts.get_one_liner_prompt_request_template().format(
                    cricket_moment=cricket_moment
                )
            else:
                prompt_request = IPLTweetAgentPrompts.get_prompt_request_template().format(
                    cricket_moment=cricket_moment
                )
            
            prompt_result = await self.agent.ainvoke({
                "messages": [
                    HumanMessage(content=prompt_request)
                ]
            })
            
            # Find the AI's response containing the prompt
            ai_messages = [msg for msg in prompt_result["messages"] if isinstance(msg, AIMessage)]
            
            if not ai_messages:
                return {
                    "messages": [
                        HumanMessage(content=f"Generate viral tweet for cricket moment: {cricket_moment}"),
                        AIMessage(content=f"Error: Could not generate prompt for the cricket moment.")
                    ],
                    "error": True
                }
            
            # Step 2: Generate the viral tweet using the prompt
            if tweet_type == "one_liner":
                tweet_request = IPLTweetAgentPrompts.get_one_liner_tweet_generation_template()
            else:
                tweet_request = IPLTweetAgentPrompts.get_tweet_generation_template()
            
            # Add tweet request to the conversation
            tweet_messages = prompt_result["messages"] + [HumanMessage(content=tweet_request)]
            
            # Generate the tweet
            tweet_result = await self.agent.ainvoke({
                "messages": tweet_messages
            })
            
            return tweet_result
            
        except Exception as e:
            error_message = f"An error occurred while generating the tweet: {str(e)}"
            print(error_message)
            import traceback
            print(traceback.format_exc())
            return {
                "messages": [
                    HumanMessage(content=f"Generate viral tweet for cricket moment: {cricket_moment}"),
                    AIMessage(content=error_message)
                ],
                "error": True
            }
    
    async def close(self):
        """Clean up resources."""
        if self.mcp_client_manager:
            await self.mcp_client_manager.close()

async def run_tweet_generation(
    cricket_moment: str, 
    generate_both_types: bool = False
):
    """
    Run the IPL tweet generation with the given cricket moment.
    
    Args:
        cricket_moment: Description of the cricket moment to tweet about
        generate_both_types: Whether to generate both standard and one-liner tweets
    
    Returns:
        The generated tweet(s)
    """
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\nERROR: OPENAI_API_KEY not found in .env file.")
        return None
    
    # Initialize the agent
    agent = IPLTweetAgent(model_name="gpt-4o")
    
    try:
        results = {}
        
        if generate_both_types:
            # Generate standard tweet
            print(f"Generating standard viral tweet...")
            standard_result = await agent.generate_tweet(cricket_moment, "standard")
            
            # Generate one-liner tweet
            print(f"Generating one-liner viral tweet...")
            one_liner_result = await agent.generate_tweet(cricket_moment, "one_liner")
            
            # Store results
            results["standard"] = standard_result
            results["one_liner"] = one_liner_result
            
            # Display results
            standard_messages = [msg for msg in standard_result["messages"] if isinstance(msg, AIMessage)]
            one_liner_messages = [msg for msg in one_liner_result["messages"] if isinstance(msg, AIMessage)]
            
            if standard_messages:
                print("\n==== VIRAL IPL STANDARD TWEET ====\n")
                print(standard_messages[-1].content)
            
            if one_liner_messages:
                print("\n==== VIRAL IPL ONE-LINER TWEET ====\n")
                print(one_liner_messages[-1].content)
        else:
            # Choose one tweet type
            tweet_type = "one_liner"  # Change to "standard" as needed
            print(f"Generating viral {tweet_type} tweet...")
            result = await agent.generate_tweet(cricket_moment, tweet_type)
            
            # Store result
            results[tweet_type] = result
            
            # Display result
            ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
            if ai_messages:
                print(f"\n==== VIRAL IPL {tweet_type.upper()} TWEET ====\n")
                print(ai_messages[-1].content)
        
        return results
        
    finally:
        # Clean up
        await agent.close()

async def main():
    """Example of using the run_tweet_generation function."""
    # Example cricket moment
    cricket_moment = """
    Rohit Sharma just hit a towering six off Pat Cummins that landed on the stadium roof. 
    The ball traveled approximately 110 meters and the crowd went absolutely wild.
    It was the last ball of the 18th over with Mumbai Indians needing 20 runs from 12 balls.
    """
    
    # Generate both types of tweets
    result = await run_tweet_generation(cricket_moment, generate_both_types=True)
    if result:
        print("\nTweet generation completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
