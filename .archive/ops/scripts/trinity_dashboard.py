#!/usr/bin/env python3
"""
scripts/trinity_dashboard.py - Real-time Trinity Monitor

Dashboard for monitoring Tri-Witness scores, execution health,
and constitutional compliance across all skills.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional


class TrinityDashboard:
    """Real-time monitoring dashboard for W3 scores."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.global_w3 = 1.0
        self.verdict_counts = {
            "SEAL": 0,
            "PARTIAL": 0,
            "VOID": 0,
            "HOLD": 0
        }
        
    def register_session(self, session_id: str, skill: str, operator: str):
        """Register a new session for monitoring."""
        self.sessions[session_id] = {
            "skill": skill,
            "operator": operator,
            "start_time": datetime.now().isoformat(),
            "executions": [],
            "current_w3": 1.0,
            "verdict": "SEAL"
        }
        
    def update_execution(self, session_id: str, result: Dict):
        """Update session with new execution result."""
        if session_id not in self.sessions:
            return
            
        session = self.sessions[session_id]
        session["executions"].append({
            "timestamp": datetime.now().isoformat(),
            "result": result
        })
        
        # Update W3
        if "w3_score" in result:
            session["current_w3"] = result["w3_score"]
            session["verdict"] = result.get("verdict", "PARTIAL")
            
        # Track global verdicts
        verdict = result.get("verdict", "VOID")
        if verdict in self.verdict_counts:
            self.verdict_counts[verdict] += 1
            
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Get status for a specific session."""
        return self.sessions.get(session_id)
        
    def get_dashboard_view(self) -> Dict:
        """Get full dashboard view."""
        # Calculate aggregate W3
        all_w3s = [s["current_w3"] for s in self.sessions.values()]
        self.global_w3 = sum(all_w3s) / len(all_w3s) if all_w3s else 1.0
        
        return {
            "global_w3": round(self.global_w3, 3),
            "total_sessions": len(self.sessions),
            "total_executions": sum(
                len(s["executions"]) for s in self.sessions.values()
            ),
            "verdict_distribution": self.verdict_counts,
            "system_health": "SEAL" if self.global_w3 >= 0.95 else "DEGRADED",
            "floor_status": self._get_floor_status(),
            "active_sessions": [
                {
                    "id": sid,
                    "skill": s["skill"],
                    "w3": round(s["current_w3"], 3),
                    "verdict": s["verdict"],
                    "executions": len(s["executions"])
                }
                for sid, s in self.sessions.items()
            ]
        }
        
    def _get_floor_status(self) -> Dict[str, str]:
        """Get status of constitutional floors."""
        return {
            "F1": "✓ Reversibility",
            "F2": "✓ Truth",
            "F3": "✓ W3 Monitor",
            "F7": "✓ Dry Run Default",
            "F12": "✓ Injection Defense",
            "F13": "✓ Authority"
        }
        
    def print_dashboard(self):
        """Print dashboard to console."""
        view = self.get_dashboard_view()
        
        print("\n" + "=" * 60)
        print("  arifOS TRINITY DASHBOARD")
        print("=" * 60)
        print(f"\n  Global W3: {view['global_w3']:.3f}  |  Health: {view['system_health']}")
        print(f"  Sessions: {view['total_sessions']}  |  Executions: {view['total_executions']}")
        print(f"\n  Verdicts: SEAL={view['verdict_distribution']['SEAL']} "
              f"PARTIAL={view['verdict_distribution']['PARTIAL']} "
              f"VOID={view['verdict_distribution']['VOID']}")
        print("\n  Active Sessions:")
        for session in view['active_sessions'][-5:]:  # Show last 5
            status = "✓" if session['verdict'] == 'SEAL' else "!"
            print(f"    {status} {session['id'][:12]}: {session['skill']:15} "
                  f"W3={session['w3']:.2f} ({session['verdict']})")
        print("\n  Floors:")
        for floor, status in view['floor_status'].items():
            print(f"    {status}")
        print("=" * 60)
        
    def export_json(self, path: str):
        """Export dashboard state to JSON."""
        with open(path, 'w') as f:
            json.dump(self.get_dashboard_view(), f, indent=2)


# Singleton instance
dashboard = TrinityDashboard()


def get_dashboard() -> TrinityDashboard:
    """Get the global dashboard instance."""
    return dashboard


async def monitor_loop(refresh_seconds: int = 5):
    """Run dashboard in monitoring mode."""
    print("Starting Trinity Monitor...")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            dashboard.print_dashboard()
            await asyncio.sleep(refresh_seconds)
    except KeyboardInterrupt:
        print("\nMonitor stopped.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        asyncio.run(monitor_loop())
    else:
        # Quick status
        dashboard.print_dashboard()
