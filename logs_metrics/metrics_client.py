#!/usr/bin/env python
"""
Metrics Client for IPL Tweet Generator
Handles sending metrics to the metrics server
"""

import os
import time
import datetime
import httpx
import logging
from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class MetricsClient:
    """Client for sending metrics to the metrics server."""
    
    def __init__(self, base_url: Optional[str] = None):
        """Initialize the metrics client.
        
        Args:
            base_url: The base URL of the metrics server (default: http://localhost:9090)
        """
        self.base_url = base_url or os.getenv("METRICS_URL", "http://localhost:9090")
        self.client = httpx.AsyncClient(timeout=10.0)
        logger.info(f"Metrics client initialized with URL: {self.base_url}")
    
    async def record_tweet_generation(
        self, 
        request_id: str, 
        tweet_type: str, 
        generation_time: float,
        tweet_content: str
    ) -> bool:
        """Record tweet generation metrics.
        
        Args:
            request_id: Unique request identifier
            tweet_type: Type of tweet generated
            generation_time: Time taken to generate the tweet (in seconds)
            tweet_content: Content of the generated tweet
            
        Returns:
            True if metrics were successfully recorded, False otherwise
        """
        try:
            payload = {
                "request_id": request_id,
                "tweet_type": tweet_type,
                "generation_time_seconds": generation_time,
                "characters": len(tweet_content),
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            response = await self.client.post(f"{self.base_url}/record", json=payload)
            
            if response.status_code == 200:
                logger.info(f"Metrics recorded for request {request_id}")
                return True
            else:
                logger.warning(f"Failed to record metrics for request {request_id}: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error recording metrics: {str(e)}")
            return False
    
    async def log_event(
        self,
        level: Literal["debug", "info", "warning", "error", "critical"],
        message: str,
        service: str = "agent",
        request_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send a log event to the metrics server.
        
        Args:
            level: Log level
            message: Log message
            service: Name of the service sending the log
            request_id: Optional request identifier
            additional_data: Optional additional data to include in the log
            
        Returns:
            True if log was successfully sent, False otherwise
        """
        try:
            payload = {
                "level": level,
                "message": message,
                "timestamp": datetime.datetime.now().isoformat(),
                "service": service,
                "request_id": request_id,
                "additional_data": additional_data or {}
            }
            
            response = await self.client.post(f"{self.base_url}/logs", json=payload)
            
            if response.status_code == 200:
                return True
            else:
                logger.warning(f"Failed to send log: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending log: {str(e)}")
            return False
    
    async def update_health_status(self, is_healthy: bool) -> bool:
        """Update the health status of the API.
        
        Args:
            is_healthy: Whether the API is healthy
            
        Returns:
            True if status was successfully updated, False otherwise
        """
        try:
            response = await self.client.post(f"{self.base_url}/health/update", json=is_healthy)
            
            if response.status_code == 200:
                logger.info(f"Health status updated to: {'healthy' if is_healthy else 'unhealthy'}")
                return True
            else:
                logger.warning(f"Failed to update health status: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating health status: {str(e)}")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Example usage
async def main():
    """Example of using the metrics client."""
    client = MetricsClient()
    
    try:
        # Record a tweet generation
        await client.record_tweet_generation(
            request_id="test-123",
            tweet_type="standard",
            generation_time=1.5,
            tweet_content="This is a test tweet with some content to measure character count!"
        )
        
        # Send a log event
        await client.log_event(
            level="info",
            message="Test log message",
            service="metrics-client-test",
            request_id="test-123"
        )
        
        # Update health status
        await client.update_health_status(True)
        
    finally:
        await client.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 