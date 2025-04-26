"""
Version 1 API routes for the IPL Tweet Generator
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Literal
import asyncio
from agent import IPLTweetAgent
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(
    prefix="/v1",
    tags=["v1"]
)

# Request and Response Models
class TweetRequest(BaseModel):
    """Request model for tweet generation"""
    cricket_moment: str = Field(..., 
        description="Description of the cricket moment to tweet about",
        example="Rohit Sharma hit a towering six that landed on the stadium roof, 110 meters away.")
    tweet_type: Optional[Literal["standard", "one_liner"]] = Field("standard", 
        description="Type of tweet to generate")
    generate_both_types: Optional[bool] = Field(False, 
        description="Whether to generate both standard and one-liner tweets")

class TweetContent(BaseModel):
    """Model for a generated tweet"""
    content: str = Field(..., description="The generated tweet content")
    tweet_type: str = Field(..., description="Type of tweet")

class TweetResponse(BaseModel):
    """Response model for tweet generation"""
    tweets: List[TweetContent] = Field(..., description="Generated tweets")
    request_id: str = Field(..., description="Unique request identifier")
    status: str = Field("success", description="Status of the request")

# Background task to log requests
def log_request(request_data: Dict[str, Any], request_id: str):
    """Log request details for analytics"""
    logger.info(f"Request {request_id}: {request_data}")

# Dependency to get agent instance
async def get_agent():
    """Get an instance of the IPL Tweet Agent"""
    agent = IPLTweetAgent()
    try:
        yield agent
    finally:
        # Clean up agent resources
        await agent.close()

@router.post("/tweets", response_model=TweetResponse)
async def generate_tweets(
    request: TweetRequest,
    background_tasks: BackgroundTasks,
    agent: IPLTweetAgent = Depends(get_agent)
):
    """
    Generate viral IPL tweets based on a cricket moment.
    
    - **cricket_moment**: Description of the cricket moment
    - **tweet_type**: Type of tweet to generate (standard or one_liner)
    - **generate_both_types**: Whether to generate both types
    
    Returns a list of generated tweets.
    """
    import uuid
    request_id = str(uuid.uuid4())
    
    # Log request in background
    background_tasks.add_task(log_request, request.dict(), request_id)
    
    try:
        results = {}
        tweets = []
        
        if request.generate_both_types:
            # Generate standard tweet
            logger.info(f"Request {request_id}: Generating standard viral tweet")
            standard_result = await agent.generate_tweet(request.cricket_moment, "standard")
            
            # Generate one-liner tweet
            logger.info(f"Request {request_id}: Generating one-liner viral tweet")
            one_liner_result = await agent.generate_tweet(request.cricket_moment, "one_liner")
            
            # Extract tweets from results
            standard_messages = [msg.content for msg in standard_result["messages"] 
                            if hasattr(msg, 'type') and msg.type == 'ai']
            one_liner_messages = [msg.content for msg in one_liner_result["messages"] 
                              if hasattr(msg, 'type') and msg.type == 'ai']
            
            if standard_messages:
                tweets.append(TweetContent(content=standard_messages[-1], tweet_type="standard"))
            
            if one_liner_messages:
                tweets.append(TweetContent(content=one_liner_messages[-1], tweet_type="one_liner"))
        else:
            # Generate single tweet type
            logger.info(f"Request {request_id}: Generating {request.tweet_type} viral tweet")
            result = await agent.generate_tweet(request.cricket_moment, request.tweet_type)
            
            # Extract tweet from result
            ai_messages = [msg.content for msg in result["messages"] 
                        if hasattr(msg, 'type') and msg.type == 'ai']
            
            if ai_messages:
                tweets.append(TweetContent(content=ai_messages[-1], tweet_type=request.tweet_type))
        
        if not tweets:
            raise HTTPException(status_code=500, detail="Failed to generate any tweets")
        
        return TweetResponse(
            tweets=tweets,
            request_id=request_id,
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Request {request_id}: Error - {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating tweets: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint for the API"""
    return {"status": "healthy", "version": "1.0.0"} 