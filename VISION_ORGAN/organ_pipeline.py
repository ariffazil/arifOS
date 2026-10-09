"""
Vision Organ v0.1 — End-to-end Pipeline Orchestrator
Shadow mode: no auto-retry, no auto-approve, no external publish.
"""
import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(__file__))

from adapters.minimax_image01 import MiniMaxImage01Adapter
from adapters.qwen_vision import QwenVisionAdapter
from compiler.compile_contract import compile_prompt
from policy.budget_guard import BudgetGuard
from ledger.vision_job_ledger import log_job


class VisionOrganPipeline:
    """Shadow-mode vision pipeline: generate → analyze → score → log."""
    
    def __init__(self, budget_usd=None, budget_credits=None):
        self.generator = MiniMaxImage01Adapter()
        self.analyzer = QwenVisionAdapter()
        self.budget = BudgetGuard(
            max_generation_cost=budget_usd,
            max_analysis_credits=budget_credits
        )
        self.max_candidates = 1
        self.max_retries = 0
    
    def run(self, contract):
        """Execute the full pipeline: generate → analyze → score → log."""
        job = {
            "request_id": contract.get("request_id", "vis_unknown"),
            "status": "started",
            "steps": {},
            "verdict": None,
        }
        
        start_time = time.time()
        
        try:
            # Step 1: Compile scene contract to prompt
            prompt = compile_prompt(contract)
            job["steps"]["compile"] = {"prompt": prompt}
            
            # Step 2: Check budget
            budget_check = self.budget.check_generation_budget()
            if not budget_check["approved"]:
                job["status"] = "rejected_budget"
                job["verdict"] = "REJECT"
                job["reason"] = budget_check["reason"]
                log_job(job)
                return job
            
            # Step 3: Generate candidate
            gen_result = self.generator.generate(
                prompt,
                aspect_ratio="1:1",
                n=min(self.max_candidates, 1)
            )
            job["steps"]["generate"] = {
                "provider": gen_result["provider"],
                "model": gen_result["model"],
                "elapsed_s": gen_result["elapsed_s"],
                "image_urls": gen_result["image_urls"],
            }
            
            # Step 4: Download image
            image_url = gen_result["image_urls"][0]
            save_path = f"/tmp/{contract['request_id']}_candidate.jpg"
            dl_result = self.generator.download_image(image_url, save_path)
            job["steps"]["download"] = {
                "path": save_path,
                "size_bytes": dl_result["size_bytes"],
            }
            
            # Step 5: Analyze with Qwen vision (quality gate)
            quality_result = self.analyzer.quality_gate(save_path, contract)
            job["steps"]["analyze"] = {
                "provider": quality_result["provider"],
                "model": quality_result["model"],
                "elapsed_s": quality_result["elapsed_s"],
                "checks": quality_result["checks"],
            }
            
            # Step 6: Determine verdict
            checks = quality_result["checks"]
            overall = checks.get("overall", "HUMAN_REVIEW")
            job["verdict"] = overall
            job["status"] = "completed"
            
            # Log to ledger
            log_job(job)
            
            job["total_elapsed_s"] = round(time.time() - start_time, 2)
            return job
            
        except Exception as e:
            job["status"] = "failed"
            job["error"] = str(e)
            job["verdict"] = "ERROR"
            log_job(job)
            return job


if __name__ == "__main__":
    # Example usage
    contract = {
        "request_id": "vis_demo_001",
        "scene_contract": {
            "subject": "blue ceramic cup",
            "required_objects": ["blue ceramic cup", "white table"],
            "setting": "white studio background",
            "camera": "centered composition, square frame",
            "negative_constraints": ["text", "watermark", "people", "extra objects"]
        }
    }
    
    pipeline = VisionOrganPipeline(budget_usd=0.005)
    result = pipeline.run(contract)
    
    print("\n" + "="*60)
    print("VISION ORGAN v0.1 — PIPELINE RESULT")
    print("="*60)
    print(json.dumps(result, indent=2, default=str))
