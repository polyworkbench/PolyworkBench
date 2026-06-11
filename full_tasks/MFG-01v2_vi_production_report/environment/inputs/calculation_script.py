#!/usr/bin/env python3
"""Verification calculation script for production data."""
import csv
import json
import sys

def calculate_yield(csv_path):
    total_output = 0
    total_good = 0
    by_line = {}
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            line = row["产线"]
            actual = int(row["实际产量"])
            good = int(row["合格品"])
            total_output += actual
            total_good += good
            if line not in by_line:
                by_line[line] = {"actual": 0, "good": 0}
            by_line[line]["actual"] += actual
            by_line[line]["good"] += good
    overall_yield = (total_good / total_output * 100) if total_output > 0 else 0
    line_yields = {k: round(v["good"]/v["actual"]*100, 2) for k,v in by_line.items()}
    return {"total_output": total_output, "total_good": total_good, "overall_yield": round(overall_yield, 2), "by_line": line_yields}

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/inputs/mes_data_zh.csv"
    result = calculate_yield(path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
