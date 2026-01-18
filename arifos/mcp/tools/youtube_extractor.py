# -*- coding: utf-8 -*-
"""
YouTube Transcript MCP Tool - Video Knowledge Extraction

Constitutional Alignment: F2 (Truth), F13 (Curiosity)
Tier: 3
Cost: Free (no API key required for transcripts)
Authority: Delta (Architect)

Purpose:
- Extract video transcripts for knowledge mining
- Alternative knowledge format (F13 Curiosity)
- Cross-validate video claims with text sources (F2)
"""

import os
from typing import Any, Dict, List, Optional

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        NoTranscriptFound,
        TranscriptsDisabled,
        VideoUnavailable,
    )
except ImportError:
    YouTubeTranscriptApi = None


class YouTubeExtractor:
    """
    YouTube MCP client for F2/F13 governance.

    F2 (Truth): Extract verifiable video content
    F13 (Curiosity): Explore video-based knowledge
    """

    def __init__(self):
        """Initialize YouTube transcript extractor."""
        self.available = YouTubeTranscriptApi is not None
        if not self.available:
            print("YouTube Transcript API not available (install youtube-transcript-api)")

    async def extract_transcript(
        self,
        video_id: str,
        languages: List[str] = None
    ) -> Dict[str, Any]:
        """
        Extract transcript from YouTube video.

        Args:
            video_id: YouTube video ID
            languages: Preferred languages (default: ['en'])

        Returns:
            {
                "text": "full transcript",
                "segments": [...],
                "floor": "F13_CURIOSITY",
                "language": "en"
            }
        """
        if not self.available:
            return {
                "error": "YouTube Transcript API not available",
                "floor": "F13_CURIOSITY_BLOCKED",
                "text": ""
            }

        if languages is None:
            languages = ['en']

        try:
            # Get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id,
                languages=languages
            )

            # Extract full text
            full_text = " ".join([segment["text"] for segment in transcript_list])

            # Calculate F2 truth score (simple length heuristic)
            f2_score = min(len(full_text) / 1000, 1.0)  # More content = more verifiable

            return {
                "text": full_text,
                "segments": transcript_list,
                "floor": "F13_CURIOSITY",
                "language": "en",  # TODO: Detect actual language
                "f2_truth_proxy": f2_score,
                "word_count": len(full_text.split())
            }

        except TranscriptsDisabled:
            return {
                "error": "Transcripts disabled for this video",
                "floor": "F13_CURIOSITY_BLOCKED",
                "text": ""
            }
        except NoTranscriptFound:
            return {
                "error": "No transcript found in requested languages",
                "floor": "F13_CURIOSITY_BLOCKED",
                "text": ""
            }
        except VideoUnavailable:
            return {
                "error": "Video unavailable",
                "floor": "F13_CURIOSITY_BLOCKED",
                "text": ""
            }
        except Exception as e:
            return {
                "error": str(e),
                "floor": "F13_CURIOSITY_ERROR",
                "text": ""
            }

    async def search_and_extract(
        self,
        search_query: str,
        max_videos: int = 3
    ) -> Dict[str, Any]:
        """
        Search YouTube and extract transcripts (requires YouTube Data API).

        NOTE: This requires YOUTUBE_API_KEY environment variable.

        Args:
            search_query: Search term
            max_videos: Max videos to process

        Returns:
            {
                "videos": [...],
                "floor": "F13_CURIOSITY",
                "total_text": "combined transcripts"
            }
        """
        api_key = os.getenv("YOUTUBE_API_KEY")

        if not api_key:
            return {
                "error": "YouTube Data API key not configured (search disabled)",
                "floor": "F13_CURIOSITY_PARTIAL",
                "videos": [],
                "hint": "Provide video IDs directly to extract_transcript() instead"
            }

        # TODO: Implement YouTube Data API search
        # For now, return error suggesting direct video ID usage
        return {
            "error": "YouTube search not implemented yet",
            "floor": "F13_CURIOSITY_PARTIAL",
            "videos": [],
            "workaround": "Use extract_transcript(video_id) with known video IDs"
        }

    async def batch_extract(
        self,
        video_ids: List[str],
        languages: List[str] = None
    ) -> Dict[str, Any]:
        """
        Extract transcripts from multiple videos.

        Args:
            video_ids: List of YouTube video IDs
            languages: Preferred languages

        Returns:
            {
                "transcripts": [...],
                "floor": "F13_CURIOSITY",
                "total_videos": 5
            }
        """
        results = []

        for video_id in video_ids:
            transcript = await self.extract_transcript(video_id, languages)
            results.append({
                "video_id": video_id,
                "transcript": transcript.get("text", ""),
                "success": "error" not in transcript
            })

        successful = sum(1 for r in results if r["success"])

        return {
            "transcripts": results,
            "floor": "F13_CURIOSITY",
            "total_videos": len(video_ids),
            "successful_extractions": successful
        }


# Singleton instance
_youtube_instance: Optional[YouTubeExtractor] = None


def get_youtube() -> YouTubeExtractor:
    """Get singleton YouTube extractor instance."""
    global _youtube_instance
    if _youtube_instance is None:
        _youtube_instance = YouTubeExtractor()
    return _youtube_instance
