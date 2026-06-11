# CloudSync API Documentation v2.4

## Overview

The CloudSync API provides a comprehensive set of endpoints for managing cloud storage synchronization across distributed systems. This document covers authentication, file operations, and webhook configuration.

**Base URL**: `https://api.cloudsync.io/v2`

For support, visit [our developer portal](https://developers.cloudsync.io/support) or email dev-support@cloudsync.io.

## Authentication

All API requests require Bearer token authentication. Obtain your token from the [API credentials page](https://dashboard.cloudsync.io/credentials).

```python
import requests

API_KEY = "cs_live_xxxxxxxxxxxxx"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "X-Request-ID": "req_unique_identifier_here"
}

response = requests.get("https://api.cloudsync.io/v2/status", headers=headers)
print(response.json())
```

> **Note**: Tokens expire after 24 hours. Use the refresh endpoint to obtain new tokens.

## File Upload

Upload files using multipart form data. The maximum file size is 500MB per request.

```python
import os
from pathlib import Path

def upload_file(file_path: str, destination: str) -> dict:
    """Upload a single file to the specified destination folder."""
    file_size = os.path.getsize(file_path)
    file_name = Path(file_path).name
    with open(file_path, "rb") as f:
        files = {"file": (file_name, f, "application/octet-stream")}
        data = {"destination": destination, "overwrite": "false"}
        response = requests.post(
            "https://api.cloudsync.io/v2/files/upload",
            headers=headers, files=files, data=data
        )
    return response.json()
```

The `upload_file` function returns a response containing the `file_id` and `upload_timestamp`.
## Batch Operations

For bulk file operations, use the batch endpoint. This reduces API calls and improves throughput.

```javascript
const CloudSync = require("@cloudsync/sdk");
const client = new CloudSync({ apiKey: process.env.CLOUDSYNC_API_KEY });

async function batchUpload(files) {
    const operations = files.map(file => ({
        action: "upload",
        source: file.localPath,
        destination: file.remotePath,
        metadata: { uploaded_by: "batch_processor", priority: "normal" }
    }));
    const result = await client.batch.execute(operations);
    console.log(`Processed ${result.successful}/${result.total} files`);
    return result;
}
```

## Webhook Configuration

Configure webhooks to receive real-time notifications about file events.

```json
{
    "webhook_url": "https://yourapp.com/webhooks/cloudsync",
    "events": ["file.uploaded", "file.deleted", "file.moved", "sync.completed"],
    "secret": "whsec_your_signing_secret",
    "retry_policy": { "max_retries": 3, "backoff_multiplier": 2 },
    "filters": { "file_types": [".pdf", ".docx", ".xlsx"], "min_size_bytes": 1024 }
}
```

> **Warning**: Webhook endpoints must respond within 30 seconds or the delivery will be marked as failed.

## Error Handling

The API returns standard HTTP error codes. Here is how to implement robust error handling:

```python
import time
from typing import Optional

class CloudSyncError(Exception):
    """Base exception for CloudSync API errors."""
    def __init__(self, status_code: int, message: str, request_id: str):
        self.status_code = status_code
        self.message = message
        self.request_id = request_id
        super().__init__(f"[{status_code}] {message} (req: {request_id})")

def api_call_with_retry(url: str, max_retries: int = 3) -> dict:
    """Make an API call with exponential backoff retry logic."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 2 ** attempt))
                time.sleep(wait_time)
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                raise CloudSyncError(408, "Request timeout", "unknown")
    raise CloudSyncError(429, "Rate limit exceeded after retries", "unknown")
```
## Sync Status Monitoring

Monitor synchronization status across all connected devices:

```python
def get_sync_status(device_id: Optional[str] = None) -> dict:
    """
    Retrieve current synchronization status.
    This function connects to the monitoring endpoint and returns
    a comprehensive status report including pending files, transfer
    speeds, and any errors encountered during the sync process.
    The report is essential for understanding system health.
    """
    endpoint = f"https://api.cloudsync.io/v2/sync/status"
    params = {}
    if device_id:
        params["device_id"] = device_id
    response = requests.get(endpoint, headers=headers, params=params)
    status_data = response.json()
    # Calculate overall health score based on multiple factors
    health_score = calculate_health(status_data)
    status_data["health_score"] = health_score
    return status_data
```

The response includes the `sync_progress` percentage and `estimated_completion` timestamp.

## Conflict Resolution

When file conflicts are detected, use the resolution API:

```python
def resolve_conflict(conflict_id: str, strategy: str = "latest_wins") -> dict:
    """
    Resolve a file synchronization conflict using the specified strategy.
    Available strategies: latest_wins, manual, merge_if_possible
    """
    payload = {
        "conflict_id": conflict_id,
        "resolution_strategy": strategy,
        "notify_users": True,
        "create_backup": True
    }
    response = requests.post(
        f"https://api.cloudsync.io/v2/conflicts/{conflict_id}/resolve",
        headers=headers, json=payload
    )
    return response.json()
```

## Storage Quota Management

Check and manage storage quotas for your organization:

```bash
# Check current usage
curl -X GET "https://api.cloudsync.io/v2/quota" \
  -H "Authorization: Bearer $CLOUDSYNC_API_KEY" \
  -H "Content-Type: application/json"

# Response format:
# {
#   "used_bytes": 5368709120,
#   "total_bytes": 10737418240,
#   "percentage_used": 50.0,
#   "largest_files": [...]
# }
```
## Event Streaming

For real-time event processing, connect to the SSE endpoint:

```python
import sseclient

def stream_events(event_types: list = None):
    """
    Connect to the Server-Sent Events stream for real-time file updates.
    The stream provides a continuous flow of events that represent every
    change happening across all synchronized folders in your account.
    This is particularly useful for building dashboards and monitoring
    systems that need to react immediately to file changes.
    """
    url = "https://api.cloudsync.io/v2/events/stream"
    params = {"types": ",".join(event_types)} if event_types else {}
    response = requests.get(url, headers=headers, params=params, stream=True)
    client = sseclient.SSEClient(response)
    for event in client.events():
        yield {"event_type": event.event, "data": json.loads(event.data), "timestamp": event.id}
```

See the [Event Types Reference](https://docs.cloudsync.io/events/types) for all available event types.

## File Versioning

Access file version history and restore previous versions:

```python
def get_file_versions(file_id: str, limit: int = 10) -> list:
    """Retrieve version history for a specific file."""
    response = requests.get(
        f"https://api.cloudsync.io/v2/files/{file_id}/versions",
        headers=headers, params={"limit": limit, "include_metadata": True}
    )
    versions = response.json()["versions"]
    return sorted(versions, key=lambda v: v["created_at"], reverse=True)

def restore_version(file_id: str, version_id: str) -> dict:
    """Restore a file to a specific previous version."""
    response = requests.post(
        f"https://api.cloudsync.io/v2/files/{file_id}/versions/{version_id}/restore",
        headers=headers
    )
    return response.json()
```

## Shared Links

Generate and manage shared links for files:

```python
from datetime import datetime, timedelta

def create_shared_link(file_id: str, expires_in_days: int = 7) -> dict:
    """Create a publicly accessible shared link for a file."""
    expiry = datetime.utcnow() + timedelta(days=expires_in_days)
    payload = {
        "file_id": file_id, "permissions": "read_only",
        "expiry": expiry.isoformat() + "Z",
        "password_protected": False, "download_limit": 100
    }
    response = requests.post("https://api.cloudsync.io/v2/links/create", headers=headers, json=payload)
    return response.json()
```

For more details on shared links, visit the [Sharing Documentation](https://docs.cloudsync.io/features/sharing).
## Team Permissions

Manage team access to synchronized folders. See [Team Management Guide](https://docs.cloudsync.io/teams/management) for details.

```yaml
# team_permissions.yaml - Configuration example
teams:
  - name: engineering
    folders:
      - path: /projects/frontend
        access: read_write
      - path: /projects/backend
        access: read_write
      - path: /deployments
        access: read_only
  - name: design
    folders:
      - path: /assets/designs
        access: read_write
      - path: /projects/frontend/mockups
        access: read_write
```

## Rate Limiting

The API enforces rate limits of 1000 requests per minute per API key. Monitor your usage via the `X-RateLimit-Remaining` header.

```python
def check_rate_limit(response) -> dict:
    """Extract rate limit information from API response headers."""
    return {
        "limit": int(response.headers.get("X-RateLimit-Limit", 1000)),
        "remaining": int(response.headers.get("X-RateLimit-Remaining", 0)),
        "reset_at": response.headers.get("X-RateLimit-Reset", ""),
        "retry_after": int(response.headers.get("Retry-After", 0))
    }
```

## SDK Installation

Install the official SDK for your platform:

```bash
# Python
pip install cloudsync-sdk==2.4.0

# Node.js
npm install @cloudsync/sdk@2.4.0

# Go
go get github.com/cloudsync/sdk-go@v2.4.0
```

For the complete API reference, visit [https://docs.cloudsync.io/api/v2](https://docs.cloudsync.io/api/v2).