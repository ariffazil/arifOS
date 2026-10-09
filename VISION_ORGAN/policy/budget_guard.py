"""
Budget Guard — enforces spending limits for vision jobs
"""
import json
import time
import os

# Default budgets (USD)
DEFAULT_GENERATION_BUDGET = 0.005  # ~$0.0035/image
DEFAULT_ANALYSIS_BUDGET_CREDITS = 1500  # Qwen Token Plan credits

class BudgetGuard:
    def __init__(self, max_generation_cost=None, max_analysis_credits=None):
        self.max_generation_cost = max_generation_cost or DEFAULT_GENERATION_BUDGET
        self.max_analysis_credits = max_analysis_credits or DEFAULT_ANALYSIS_BUDGET_CREDITS
    
    def check_generation_budget(self, estimated_cost=None):
        """Check if generation is within budget."""
        if estimated_cost is None:
            estimated_cost = 0.0035  # MiniMax default
        
        if estimated_cost > self.max_generation_cost:
            return {
                "approved": False,
                "reason": f"Estimated cost ${estimated_cost:.4f} exceeds budget ${self.max_generation_cost:.4f}",
                "max_allowed": self.max_generation_cost,
                "estimated": estimated_cost
            }
        
        return {
            "approved": True,
            "estimated_cost": estimated_cost,
            "budget_remaining": self.max_generation_cost - estimated_cost
        }
    
    def check_analysis_budget(self, estimated_tokens=500):
        """Check if analysis is within Qwen credit budget."""
        # Rough estimate: 1026 image tokens = ~1500 total tokens for 512x512
        # 1 credit ≈ 1 token (simplified)
        if estimated_tokens > self.max_analysis_credits:
            return {
                "approved": False,
                "reason": f"Estimated {estimated_tokens} tokens exceeds credit budget {self.max_analysis_credits}",
                "max_allowed": self.max_analysis_credits,
                "estimated": estimated_tokens
            }
        
        return {
            "approved": True,
            "estimated_tokens": estimated_tokens,
            "credits_remaining": self.max_analysis_credits - estimated_tokens
        }
    
    def record_spend(self, provider, cost_usd=None, credits_used=None):
        """Record actual spend for tracking."""
        spend_record = {
            "timestamp": time.time(),
            "provider": provider,
            "cost_usd": cost_usd,
            "credits_used": credits_used,
        }
        return spend_record
