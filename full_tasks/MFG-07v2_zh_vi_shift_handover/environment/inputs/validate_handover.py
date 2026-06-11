#!/usr/bin/env python3
"""Validate handover document format."""
import sys
import json
from pathlib import Path

def validate(filepath):
    checks = []
    content = Path(filepath).read_text(encoding="utf-8")
    # Check 1: Has required sections (at least 4)
    sections = content.count("## ") + content.count("# ")
    checks.append({"name": "has_sections", "passed": sections >= 4})
    # Check 2: Has production data
    has_prod = "1185" in content or "978" in content or "812" in content
    checks.append({"name": "has_production_data", "passed": has_prod})
    # Check 3: Has quality info
    has_qual = "defect" in content.lower() or "不良" in content or "lỗi" in content
    checks.append({"name": "has_quality_info", "passed": has_qual})
    # Check 4: Length adequate
    checks.append({"name": "adequate_length", "passed": len(content) > 500})
    # Check 5: Has safety section
    has_safe = "安全" in content or "safety" in content.lower() or "an toàn" in content.lower()
    checks.append({"name": "has_safety_section", "passed": has_safe})
    passed = all(c["passed"] for c in checks)
    return {"validation_passed": passed, "checks": checks}

if __name__ == "__main__":
    fp = sys.argv[1] if len(sys.argv) > 1 else "/workspace/output/handover_zh.md"
    result = validate(fp)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["validation_passed"] else 1)
