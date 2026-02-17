#!/usr/bin/env python3
import json
import sys
from pathlib import Path

FLAG_FILE = Path(".report-in-progress")
QA_REPORT = Path("output/qa-report.json")
ITERATION_FILE = Path("output/.qa-iteration-count")

# Only gate report-generation sessions
if not FLAG_FILE.exists():
    sys.exit(0)

# Parse stdin for stop_hook_active
try:
    hook_input = json.loads(sys.stdin.read())
    stop_hook_active = hook_input.get("stop_hook_active", False)
except (json.JSONDecodeError, Exception):
    stop_hook_active = False

# Track iterations to prevent infinite loops
if stop_hook_active:
    iteration = int(ITERATION_FILE.read_text().strip()) if ITERATION_FILE.exists() else 0
    iteration += 1
    ITERATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    ITERATION_FILE.write_text(str(iteration))
    if iteration >= 3:
        FLAG_FILE.unlink(missing_ok=True)
        ITERATION_FILE.unlink(missing_ok=True)
        sys.exit(0)  # Max reached, let Claude stop

# No QA report yet — block
if not QA_REPORT.exists():
    print(json.dumps({
        "decision": "block",
        "reason": "No QA report found. Complete the full pipeline per the Agent Orchestration Protocol in CLAUDE.md."
    }))
    sys.exit(0)

# Check QA status
try:
    qa = json.loads(QA_REPORT.read_text())
    status = qa.get("status", "")
except (json.JSONDecodeError, Exception):
    status = ""

if status in ("PASS", "PASS WITH NOTES"):
    FLAG_FILE.unlink(missing_ok=True)
    ITERATION_FILE.unlink(missing_ok=True)
    sys.exit(0)  # QA passed, allow stop

# FAIL — block and provide routing info
routing = qa.get("routing", "unknown")
issues = qa.get("issues", [])
print(json.dumps({
    "decision": "block",
    "reason": f"QA FAIL. Routing: {routing}. Issues: {json.dumps(issues)}. Follow Re-spawn Rules in CLAUDE.md."
}))
sys.exit(0)
