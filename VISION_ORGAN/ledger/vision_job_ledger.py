"""
Vision Job Ledger — append-only local logging for all vision jobs
Local only. No VAULT999 writes. No external publishing.
"""
import json
import os
import time

LEDGER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ledger", "vision-jobs.jsonl")

def log_job(job_data):
    """Append a job record to the local ledger."""
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    
    record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "epoch": time.time(),
        **job_data
    }
    
    with open(LEDGER_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")
    
    return record

def get_jobs(limit=10):
    """Get recent jobs from ledger."""
    if not os.path.exists(LEDGER_PATH):
        return []
    
    jobs = []
    with open(LEDGER_PATH, "r") as f:
        for line in f:
            if line.strip():
                jobs.append(json.loads(line))
    
    return jobs[-limit:]
