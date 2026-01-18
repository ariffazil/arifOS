# -*- coding: utf-8 -*-
"""
Reddit MCP Tool - Community Truth-Seeking

Constitutional Alignment: F2 (Truth), F13 (Curiosity)
Tier: 3
Cost: Free (requires Reddit API credentials)
Authority: Delta (Architect)

Purpose:
- Search Reddit communities for authentic perspectives
- Rank by subscriber count and activity (F2 proxy)
- Cross-validate with other truth sources (Tri-Witness)
"""

import os
from typing import Any, Dict, List, Optional

try:
    import praw
except ImportError:
    praw = None  # Will be handled gracefully


class RedditSearcher:
    """
    Reddit MCP client for F2/F13 governance.

    F2 (Truth): Community consensus as authenticity signal
    F13 (Curiosity): Explore alternative perspectives
    """

    def __init__(self):
        """Initialize Reddit client with credentials from environment."""
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "arifOS/v49.0.0")

        if praw and self.client_id and self.client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
                self.available = True
            except Exception as e:
                print(f"Reddit initialization failed: {e}")
                self.reddit = None
                self.available = False
        else:
            self.reddit = None
            self.available = False

    async def search_subreddits(
        self,
        query: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Search Reddit subreddits for query.

        Args:
            query: Search term
            limit: Max subreddits to return

        Returns:
            {
                "subreddits": [...],
                "floor": "F2_TRUTH",
                "authenticity_scores": [...]
            }
        """
        if not self.available:
            return {
                "error": "Reddit client not available (missing credentials or praw)",
                "floor": "F2_TRUTH_UNAVAILABLE",
                "subreddits": []
            }

        try:
            subreddits = list(self.reddit.subreddits.search(query, limit=limit))

            results = []
            for sub in subreddits:
                # F2 Authenticity proxy: subscribers + activity
                authenticity_score = self._calculate_authenticity(sub)

                results.append({
                    "name": sub.display_name,
                    "subscribers": sub.subscribers,
                    "description": sub.public_description,
                    "authenticity_score": authenticity_score,
                    "f2_truth_signal": authenticity_score >= 0.5
                })

            # Sort by authenticity (highest first)
            results.sort(key=lambda x: x["authenticity_score"], reverse=True)

            return {
                "subreddits": results,
                "floor": "F2_TRUTH",
                "total_found": len(results)
            }

        except Exception as e:
            return {
                "error": str(e),
                "floor": "F2_TRUTH_ERROR",
                "subreddits": []
            }

    async def search_posts(
        self,
        query: str,
        subreddit: str = "all",
        limit: int = 10,
        time_filter: str = "week"
    ) -> Dict[str, Any]:
        """
        Search Reddit posts for query.

        Args:
            query: Search term
            subreddit: Subreddit name (default: all)
            limit: Max posts to return
            time_filter: week/month/year/all

        Returns:
            {
                "posts": [...],
                "floor": "F13_CURIOSITY",
                "perspectives": [...]
            }
        """
        if not self.available:
            return {
                "error": "Reddit client not available",
                "floor": "F13_CURIOSITY_BLOCKED",
                "posts": []
            }

        try:
            sub = self.reddit.subreddit(subreddit)
            posts = list(sub.search(query, limit=limit, time_filter=time_filter))

            results = []
            for post in posts:
                results.append({
                    "title": post.title,
                    "score": post.score,
                    "upvote_ratio": post.upvote_ratio,
                    "num_comments": post.num_comments,
                    "url": post.url,
                    "author": str(post.author),
                    "created_utc": post.created_utc,
                    "f13_perspective": True  # Alternative viewpoint
                })

            return {
                "posts": results,
                "floor": "F13_CURIOSITY",
                "total_found": len(results)
            }

        except Exception as e:
            return {
                "error": str(e),
                "floor": "F13_CURIOSITY_ERROR",
                "posts": []
            }

    def _calculate_authenticity(self, subreddit) -> float:
        """
        F2 authenticity heuristic.

        Factors:
        - Subscriber count (larger = more vetted)
        - Public description exists (curated)

        Returns:
            Score 0.0-1.0 (higher = more authentic)
        """
        score = 0.0

        # Subscriber signal (log scale)
        if subreddit.subscribers > 100000:
            score += 0.5
        elif subreddit.subscribers > 10000:
            score += 0.3
        elif subreddit.subscribers > 1000:
            score += 0.2
        else:
            score += 0.1

        # Description signal
        if subreddit.public_description and len(subreddit.public_description) > 50:
            score += 0.3
        elif subreddit.public_description:
            score += 0.2

        return min(score, 1.0)


# Singleton instance
_reddit_instance: Optional[RedditSearcher] = None


def get_reddit() -> RedditSearcher:
    """Get singleton Reddit searcher instance."""
    global _reddit_instance
    if _reddit_instance is None:
        _reddit_instance = RedditSearcher()
    return _reddit_instance
