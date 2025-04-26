# IPL Tweet Generator - Logging and Metrics Service

This service provides logging, monitoring, and metrics collection for the IPL Tweet Generator application using Prometheus and Grafana.

## Features

- Prometheus metrics collection for IPL tweet generation
- Grafana dashboards for visualization
- Centralized logging service
- Health status monitoring

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11 or higher (for local development)

### Environment Variables

Create a `.env` file with the following variables:

```
METRICS_PORT=9090
METRICS_HOST=0.0.0.0
ENVIRONMENT=development

# Grafana credentials
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin

# Log settings
LOG_LEVEL=INFO
```

### Running with Docker Compose

Start the service using Docker Compose:

```bash
docker-compose up --build -d
```

This will start:
- The metrics server on port 9090
- Prometheus on port 9091
- Grafana on port 3000

### Accessing the Services

- Metrics Server: http://localhost:9090
- Prometheus: http://localhost:9091
- Grafana: http://localhost:3000 (login with the credentials from your .env file)

## Key Metrics

The service collects the following metrics:

1. **Tweet Requests Total**: Count of tweet generation requests by type
2. **Tweet Generation Time**: Histogram of time taken to generate tweets
3. **Tweet Character Count**: Distribution of tweet character counts
4. **API Health Status**: Health status of the agent API

## Client Integration

To integrate with your agent, use the `metrics_client.py` module. Example:

```python
from metrics_client import MetricsClient

# Initialize client
metrics_client = MetricsClient()

# Record tweet generation
await metrics_client.record_tweet_generation(
    request_id="abc-123",
    tweet_type="standard",
    generation_time=1.5,
    tweet_content="Generated tweet content here"
)

# Log events
await metrics_client.log_event(
    level="info",
    message="Tweet generated successfully",
    service="agent",
    request_id="abc-123"
)

# Update health status
await metrics_client.update_health_status(True)

# Clean up
await metrics_client.close()
```

## Directory Structure

```
logs_metrics/
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Dockerfile for the metrics server
├── metrics_client.py       # Client for agent integration
├── metrics_server.py       # Metrics server implementation
├── pyproject.toml          # Python package configuration
├── prometheus/             # Prometheus configuration
└── grafana/                # Grafana configuration and dashboards
``` 