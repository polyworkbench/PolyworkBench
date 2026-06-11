#!/usr/bin/env python3
"""Validation script for code block preservation in translated API docs."""
import re, sys, json
from pathlib import Path

REQUIRED_MARKERS = [
    "cs_live_xxxxxxxxxxxxx",
    "async function batchUpload(files)",
    "whsec_your_signing_secret",
    "class CloudSyncError(Exception):",
    "health_score = calculate_health(status_data)",
    "resolution_strategy",
    "api.cloudsync.io/v2/quota",
    "sseclient.SSEClient(response)",
    "include_metadata",
    "password_protected",
    "read_write",
    "X-RateLimit-Limit",
    "cloudsync-sdk==2.4.0",
    "uploaded_by",
    "req_unique_identifier_here",
]

REQUIRED_LINKS = [
    "https://developers.cloudsync.io/support",
    "https://dashboard.cloudsync.io/credentials",
    "https://docs.cloudsync.io/events/types",
    "https://docs.cloudsync.io/features/sharing",
    "https://docs.cloudsync.io/teams/management",
    "https://docs.cloudsync.io/api/v2",
]

INLINE_CODE_MARKERS = [
    "`file_id`",
    "`upload_timestamp`",
    "`sync_progress`",
    "`estimated_completion`",
    "`X-RateLimit-Remaining`",
    "`upload_file`",
]


def validate_translation(filepath):
    """Validate that translated file preserves code blocks."""
    if not Path(filepath).exists():
        return {"error": "File not found: " + filepath, "validation_passed": False}
    content = Path(filepath).read_text(encoding="utf-8")
    results = {
        "total_code_blocks": 15,
        "preserved_blocks": 0,
        "broken_blocks": [],
        "inline_code_preserved": True,
        "links_valid": True,
        "validation_passed": False,
    }
    preserved = 0
    for i, marker in enumerate(REQUIRED_MARKERS):
        if marker in content:
            preserved += 1
        else:
            results["broken_blocks"].append(i + 1)
    results["preserved_blocks"] = preserved
    for link in REQUIRED_LINKS:
        if link not in content:
            results["links_valid"] = False
            break
    for marker in INLINE_CODE_MARKERS:
        if marker not in content:
            results["inline_code_preserved"] = False
            break
    results["validation_passed"] = (
        preserved == 15 and results["links_valid"] and results["inline_code_preserved"]
    )
    return results


if __name__ == "__main__":
    fp = sys.argv[1] if len(sys.argv) > 1 else "/workspace/output/api_docs_es.md"
    results = validate_translation(fp)
    print(json.dumps(results, indent=2))
    if results["validation_passed"]:
        print("VALIDATION PASSED")
        sys.exit(0)
    else:
        broken = 15 - results["preserved_blocks"]
        print("VALIDATION FAILED: " + str(broken) + " blocks broken")
        sys.exit(1)
