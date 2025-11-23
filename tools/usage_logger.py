#!/usr/bin/env python3
"""
Gemini Usage Logger

Logs Gemini CLI usage for pattern analysis and quota monitoring.
Integrates with the gemini-delegation skill to track actual usage.
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

class GeminiUsageLogger:
    def __init__(self):
        self.log_dir = Path.home() / ".claude" / "hooks" / "gemini" / "logs"
        self.usage_log = self.log_dir / "usage.jsonl"
        self.session_file = self.log_dir / "current_session.json"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_usage(self, command: str, estimated_tokens: int, actual_tokens: int = None,
                  success: bool = True, duration: float = None, error: str = None):
        """Log a Gemini CLI usage event."""
        timestamp = datetime.now().isoformat()

        log_entry = {
            "timestamp": timestamp,
            "command": command,
            "estimated_tokens": estimated_tokens,
            "actual_tokens": actual_tokens or estimated_tokens,  # Default
            "success": success,
            "duration_seconds": duration,
            "error": error,
            "session_id": self._get_session_id()
        }

        # Write to usage log
        with open(self.usage_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        # Update session stats
        self._update_session_stats(log_entry)

    def _get_session_id(self) -> str:
        """Get or create a session identifier."""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                    # Check if session is still recent (within 1 hour)
                    last_activity = datetime.fromisoformat(session_data.get("last_activity", ""))
                    if (datetime.now() - last_activity).seconds < 3600:
                        return session_data.get("session_id", "unknown")
            except:
                pass

        # Create new session
        session_id = f"session_{int(time.time())}"
        session_data = {
            "session_id": session_id,
            "start_time": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }

        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

        return session_id

    def _update_session_stats(self, log_entry):
        """Update current session statistics."""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
            else:
                session_data = {"session_id": self._get_session_id()}

            # Update stats
            session_data["last_activity"] = log_entry["timestamp"]
            session_data.setdefault("total_requests", 0)
            session_data.setdefault("total_tokens", 0)
            session_data.setdefault("successful_requests", 0)

            session_data["total_requests"] += 1
            session_data["total_tokens"] += log_entry["actual_tokens"]
            if log_entry["success"]:
                session_data["successful_requests"] += 1

            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)

        except Exception:
            pass  # Don't let logging errors break the main flow

    def get_usage_summary(self, hours: int = 24) -> dict:
        """Get usage summary for the last N hours."""
        if not self.usage_log.exists():
            return {"total_requests": 0, "total_tokens": 0, "success_rate": 0.0}

        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        total_requests = 0
        total_tokens = 0
        successful_requests = 0

        try:
            with open(self.usage_log, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        entry_time = datetime.fromisoformat(entry["timestamp"]).timestamp()

                        if entry_time >= cutoff_time:
                            total_requests += 1
                            total_tokens += entry.get("actual_tokens", 0)
                            if entry.get("success", False):
                                successful_requests += 1
                    except (json.JSONDecodeError, KeyError):
                        continue
        except FileNotFoundError:
            pass

        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0.0

        return {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "successful_requests": successful_requests,
            "success_rate": success_rate,
            "hours_analyzed": hours
        }

    def get_recent_errors(self, count: int = 5) -> list:
        """Get recent error entries."""
        if not self.usage_log.exists():
            return []

        errors = []
        try:
            with open(self.usage_log, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if not entry.get("success", True) and entry.get("error"):
                            errors.append(entry)
                    except (json.JSONDecodeError, KeyError):
                        continue
        except FileNotFoundError:
            pass

        return errors[-count:]  # Return last N errors

# CLI interface for manual usage tracking
def main():
    if len(sys.argv) < 3:
        print("Usage: python3 usage_logger.py <command> <estimated_tokens> [success] [duration] [error]")
        sys.exit(1)

    command = sys.argv[1]
    estimated_tokens = int(sys.argv[2])
    success = sys.argv[3].lower() == "true" if len(sys.argv) > 3 else True
    duration = float(sys.argv[4]) if len(sys.argv) > 4 else None
    error = sys.argv[5] if len(sys.argv) > 5 else None

    logger = GeminiUsageLogger()
    logger.log_usage(command, estimated_tokens, success=success, duration=duration, error=error)

if __name__ == "__main__":
    main()