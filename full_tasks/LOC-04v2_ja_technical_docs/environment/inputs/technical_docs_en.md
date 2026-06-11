# DataStream SDK Documentation

## Getting Started

The DataStream SDK provides real-time data processing capabilities for your application. Install the SDK using your preferred package manager.

```python
from datastream import Client, StreamConfig

client = Client(api_key="ds_xxx")
config = StreamConfig(buffer_size=1024, timeout=30)
stream = client.create_stream(config)

for event in stream.listen():
    print(f"Received: {event.payload}")
```

See [Authentication](#authentication) for details on API keys.

## Authentication

All requests require authentication via API key. See [Rate Limiting](#rate-limiting) for usage limits.

```python
from datastream.auth import TokenManager

manager = TokenManager(refresh_interval=3600)
token = manager.get_token()
headers = {"Authorization": f"Bearer {token}"}
```

## Stream Processing

The stream processor handles data transformation and filtering in real-time.

```python
from datastream.processors import FilterProcessor, MapProcessor

pipeline = client.create_pipeline([
    FilterProcessor(lambda e: e.type == "metric"),
    MapProcessor(lambda e: {"value": e.payload * 2})
])
pipeline.start()
```

For advanced configuration, refer to [Pipeline Configuration](#pipeline-configuration).

## Pipeline Configuration

Configure processing pipelines with YAML:

```yaml
pipeline:
  name: metrics-processor
  stages:
    - type: filter
      condition: "event.type == metric"
    - type: transform
      operation: multiply
      factor: 2
    - type: output
      destination: warehouse
```

## Error Handling

Implement robust error handling for production deployments:

```python
from datastream.errors import StreamError, ConnectionLost

try:
    stream.connect()
except ConnectionLost as e:
    logger.error(f"Connection lost: {e.reason}")
    stream.reconnect(max_retries=3)
except StreamError as e:
    logger.critical(f"Fatal: {e}")
```

See [Monitoring](#monitoring) for alerting setup.

## Monitoring

Set up monitoring dashboards:

```python
from datastream.monitoring import MetricsCollector

collector = MetricsCollector(namespace="myapp")
collector.track("events_processed", stream.count)
collector.track("latency_ms", stream.avg_latency)
collector.export_to("prometheus", port=9090)
```

## Rate Limiting

The API enforces rate limits of 10,000 events per minute.

```python
from datastream.limits import RateLimiter

limiter = RateLimiter(max_events=10000, window="1m")
stream.set_limiter(limiter)
```

## Batch Processing

For historical data, use batch mode:

```python
from datastream.batch import BatchProcessor

batch = BatchProcessor(chunk_size=500)
results = batch.process_file("/data/events.parquet")
print(f"Processed {results.total} events in {results.duration}s")
```

For more information, visit [https://docs.datastream.io](https://docs.datastream.io).
