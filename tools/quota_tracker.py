#!/usr/bin/env python3
"""
Gemini CLI Quota Tracker

Track Gemini CLI usage to provide quota warnings and prevent rate limit exhaustion. Monitor usage patterns and estimate remaining quota.
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Gemini Free Tier Limits (adjustable based on your plan)
DEFAULT_LIMITS = {
    "requests_per_minute": 60,
    "requests_per_day": 1000,
    "tokens_per_minute": 32000,
    "tokens_per_day": 1000000
}

class GeminiQuotaTracker:
    def __init__(self, limits: Optional[Dict] = None):
        self.limits = limits or DEFAULT_LIMITS
        self.usage_file = Path.home() / ".claude" / "hooks" / "gemini" / "usage.json"
        self.usage_data = self._load_usage_data()

    def _load_usage_data(self) -> Dict:
        """Load usage data from file or create a new structure."""
        if self.usage_file.exists():
            try:
                with open(self.usage_file, 'r') as f:
                    data = json.load(f)
                # Clean old data (older than 24 hours)
                self._cleanup_old_data(data)
                return data
            except (json.JSONDecodeError, KeyError):
                pass

        return {
            "requests": [],
            "daily_tokens": 0,
            "last_reset": datetime.now().isoformat()
        }

    def _cleanup_old_data(self, data: Dict):
        """Remove usage data older than 24 hours."""
        now = datetime.now()
        cutoff = now - timedelta(hours=24)

        # Filter out old requests
        data["requests"] = [
            req for req in data.get("requests", [])
            if datetime.fromisoformat(req["timestamp"]) > cutoff
        ]

        # Reset daily counter if needed
        last_reset = datetime.fromisoformat(data.get("last_reset", now.isoformat()))
        if (now - last_reset).days >= 1:
            data["daily_tokens"] = 0
            data["last_reset"] = now.isoformat()

    def _save_usage_data(self):
        """Save usage data to file."""
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage_data, f, indent=2)

    def record_request(self, estimated_tokens: int, success: bool = True):
        """Record a Gemini CLI request."""
        now = datetime.now()

        request_data = {
            "timestamp": now.isoformat(),
            "tokens": estimated_tokens,
            "success": success
        }

        self.usage_data["requests"].append(request_data)
        if success:
            self.usage_data["daily_tokens"] += estimated_tokens

        self._save_usage_data()

    def get_current_usage(self) -> Dict:
        """Get current usage statistics."""
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)

        recent_requests = [
            req for req in self.usage_data.get("requests", [])
            if datetime.fromisoformat(req["timestamp"]) > one_minute_ago
        ]

        return {
            "requests_last_minute": len(recent_requests),
            "tokens_last_minute": sum(req["tokens"] for req in recent_requests),
            "daily_tokens": self.usage_data.get("daily_tokens", 0),
            "requests_today": len(self.usage_data.get("requests", []))
        }

    def get_quota_status(self) -> Tuple[str, List[str]]:
        """Get quota status and warnings."""
        usage = self.get_current_usage()
        warnings = []

        # Check per-minute limits
        rpm_usage = usage["requests_last_minute"] / self.limits["requests_per_minute"]
        tpm_usage = usage["tokens_last_minute"] / self.limits["tokens_per_minute"]

        # Check daily limits
        daily_tokens_usage = usage["daily_tokens"] / self.limits["tokens_per_day"]
        daily_requests_usage = usage["requests_today"] / self.limits["requests_per_day"]

        status = "✅ Healthy"

        # High usage warnings (>80%)
        if rpm_usage > 0.8:
            status = "⚠️ High RPM"
            warnings.append(f"Request rate: {usage['requests_last_minute']}/{self.limits['requests_per_minute']} per minute")

        if tpm_usage > 0.8:
            if status == "✅ Healthy":
                status = "⚠️ High TPM"
            warnings.append(f"Token rate: {usage['tokens_last_minute']:,}/{self.limits['tokens_per_minute']:,} per minute")

        if daily_tokens_usage > 0.8:
            status = "🚨 Daily Token Warning"
            warnings.append(f"Daily tokens: {usage['daily_tokens']:,}/{self.limits['tokens_per_day']:,} ({daily_tokens_usage:.1%})")

        if daily_requests_usage > 0.8:
            status = "🚨 Daily Request Warning"
            warnings.append(f"Daily requests: {usage['requests_today']}/{self.limits['requests_per_day']} ({daily_requests_usage:.1%})")

        # Critical warnings (>95%)
        if rpm_usage > 0.95 or tpm_usage > 0.95:
            status = "🚨 Critical - Rate Limit Soon"
            warnings.append("IMMEDIATE: Approaching rate limits! Wait or reduce usage.")

        if daily_tokens_usage > 0.95 or daily_requests_usage > 0.95:
            status = "🚨 Critical - Daily Quota Exhausted"
            warnings.append("CRITICAL: Daily quota nearly exhausted! Large tasks may fail.")

        return status, warnings

    def estimate_task_tokens(self, file_paths: List[str], prompt_length: int = 100) -> int:
        """Estimate tokens needed for a task."""
        total_chars = prompt_length

        for file_path in file_paths:
            try:
                if os.path.isfile(file_path):
                    total_chars += os.path.getsize(file_path)
                elif os.path.isdir(file_path):
                    for root, dirs, files in os.walk(file_path):
                        # Skip common non-source directories
                        dirs[:] = [d for d in dirs if d not in [
                            '__pycache__', 'node_modules', '.git',
                            'venv', '.venv', 'dist', 'build'
                        ]]
                        for file in files:
                            if file.endswith(('.py', '.js', '.ts', '.md', '.yaml', '.yml', '.json')):
                                total_chars += os.path.getsize(os.path.join(root, file))
            except (OSError, PermissionError):
                continue

        # Rough estimation: ~4 chars per token
        return total_chars // 4

    def can_handle_task(self, estimated_tokens: int) -> Tuple[bool, List[str]]:
        """Check if Gemini can handle a task given current quota."""
        usage = self.get_current_usage()
        issues = []

        # Check per-minute capacity
        if usage["requests_last_minute"] >= self.limits["requests_per_minute"] - 1:
            issues.append("Request rate limit reached - wait 1 minute")
            can_handle = False
        elif usage["tokens_last_minute"] + estimated_tokens > self.limits["tokens_per_minute"]:
            issues.append("Token rate limit would be exceeded - wait or split task")
            can_handle = False
        elif usage["daily_tokens"] + estimated_tokens > self.limits["tokens_per_day"]:
            issues.append("Daily token quota would be exceeded - wait for reset")
            can_handle = False
        else:
            can_handle = True

        return can_handle, issues

def estimate_tokens_from_gemini_command(command: str) -> int:
    """Estimate tokens from a Gemini CLI command by analyzing @ paths."""
    import shlex

    try:
        parts = shlex.split(command)
        file_paths = []

        for part in parts:
            if part.startswith('@'):
                file_paths.append(part[1:])  # Remove @ prefix

        # Create a tracker instance for estimation
        tracker = GeminiQuotaTracker()
        return tracker.estimate_task_tokens(file_paths, len(command))
    except:
        # Default estimation
        return len(command) // 4  # Rough estimate

# Example usage and testing
if __name__ == "__main__":
    tracker = GeminiQuotaTracker()

    # Test quota status
    status, warnings = tracker.get_quota_status()
    print(f"Status: {status}")
    for warning in warnings:
        print(f"  Warning: {warning}")

    # Test token estimation
    test_paths = ["/home/alext/simple-resume/src"]
    estimated = tracker.estimate_task_tokens(test_paths)
    print(f"Estimated tokens for src/: {estimated:,}")