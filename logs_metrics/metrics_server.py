#!/usr/bin/env python
"""
Metrics Server for IPL Tweet Generator
Exposes Prometheus metrics and handles logging visualization with Grafana
"""

import os
import time
import logging
from typing import Dict, Any
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import (
    Counter, Histogram, Gauge, 
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry
)
import uvicorn
from pydantic import BaseModel
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="IPL Tweet Generator Metrics",
    description="Prometheus metrics for IPL Tweet Generator",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Prometheus metrics registry
registry = CollectorRegistry()

# Define metrics
tweet_requests_total = Counter(
    "tweet_requests_total", 
    "Total number of tweet generation requests",
    ["tweet_type"],
    registry=registry
)

tweet_generation_time = Histogram(
    "tweet_generation_time_seconds", 
    "Time to generate tweets",
    ["tweet_type"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0),
    registry=registry
)

tweet_characters = Histogram(
    "tweet_characters", 
    "Number of characters in generated tweets",
    ["tweet_type"],
    buckets=(10, 30, 50, 100, 140, 200, 280),
    registry=registry
)

api_health = Gauge(
    "api_health",
    "Health status of the API (1=healthy, 0=unhealthy)",
    registry=registry
)

# Initialize health as healthy
api_health.set(1)

# Models for API
class MetricsPayload(BaseModel):
    """Payload for recording metrics"""
    request_id: str
    tweet_type: str
    generation_time_seconds: float
    characters: int
    timestamp: str

class LogEvent(BaseModel):
    """Log event model"""
    level: str
    message: str
    timestamp: str
    service: str
    request_id: str = None
    additional_data: Dict[str, Any] = None

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Process Time: {process_time:.4f}s"
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request: {request.method} {request.url.path} "
            f"- Error: {str(e)} "
            f"- Process Time: {process_time:.4f}s"
        )
        raise

# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Expose Prometheus metrics"""
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)

# Endpoint to record metrics
@app.post("/record")
async def record_metrics(payload: MetricsPayload):
    """Record metrics from tweet generation"""
    # Record metrics
    tweet_requests_total.labels(payload.tweet_type).inc()
    tweet_generation_time.labels(payload.tweet_type).observe(payload.generation_time_seconds)
    tweet_characters.labels(payload.tweet_type).observe(payload.characters)
    
    logger.info(
        f"Recorded metrics for request {payload.request_id}: "
        f"type={payload.tweet_type}, "
        f"time={payload.generation_time_seconds:.2f}s, "
        f"chars={payload.characters}"
    )
    
    return {"status": "success", "recorded_at": datetime.datetime.now().isoformat()}

# Endpoint to record logs
@app.post("/logs")
async def record_logs(log_event: LogEvent):
    """Record log events"""
    # Map log level string to logging method
    log_methods = {
        "debug": logger.debug,
        "info": logger.info,
        "warning": logger.warning,
        "error": logger.error,
        "critical": logger.critical
    }
    
    # Get the appropriate logging method (default to info)
    log_method = log_methods.get(log_event.level.lower(), logger.info)
    
    # Format the log message
    request_id_str = f" [Request: {log_event.request_id}]" if log_event.request_id else ""
    log_message = f"[{log_event.service}]{request_id_str} {log_event.message}"
    
    # Log the message
    log_method(log_message, extra=log_event.additional_data or {})
    
    return {"status": "success", "recorded_at": datetime.datetime.now().isoformat()}

# Health check endpoint (for the metrics server itself)
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

# Update API health status
@app.post("/health/update")
async def update_health(status: bool):
    """Update the API health status gauge"""
    api_health.set(1 if status else 0)
    logger.info(f"API health status updated to: {'healthy' if status else 'unhealthy'}")
    return {"status": "updated", "health": status}

if __name__ == "__main__":
    port = int(os.getenv("METRICS_PORT", "9090"))
    host = os.getenv("METRICS_HOST", "0.0.0.0")
    
    logger.info(f"Starting metrics server on {host}:{port}")
    
    uvicorn.run(
        "metrics_server:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT", "production") == "development",
    )
