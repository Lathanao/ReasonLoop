import time
import psutil
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class Metrics:
    """Class for tracking execution metrics in ReasonLoop."""

    # Timing metrics
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0

    # Token usage tracking
    token_usage: Dict[str, int] = field(default_factory=lambda: {
        "prompt": 0,
        "completion": 0,
        "total": 0
    })

    # System resource tracking
    memory_usage: List[float] = field(default_factory=list)
    cpu_usage: List[float] = field(default_factory=list)

    # Execution tracking
    execution_steps: int = 0

    # Extensibility
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

    def start(self):
        """Start or reset metrics tracking."""
        self.start_time = time.time()
        self.end_time = 0.0
        self.token_usage = {"prompt": 0, "completion": 0, "total": 0}
        self.memory_usage = []
        self.cpu_usage = []
        self.execution_steps = 0
        self.custom_metrics = {}
        self._capture_system_metrics()

    def stop(self):
        """Stop metrics tracking."""
        self.end_time = time.time()
        self._capture_system_metrics()

    def add_tokens(self, prompt_tokens: int = 0, completion_tokens: int = 0):
        """Track token usage."""
        self.token_usage["prompt"] += prompt_tokens
        self.token_usage["completion"] += completion_tokens
        self.token_usage["total"] = self.token_usage["prompt"] + self.token_usage["completion"]

    def increment_steps(self):
        """Increment execution step counter and capture metrics."""
        self.execution_steps += 1
        self._capture_system_metrics()

    def add_custom_metric(self, name: str, value: Any):
        """Add a custom metric."""
        self.custom_metrics[name] = value

    def _capture_system_metrics(self):
        """Capture current system resource usage."""
        try:
            # Memory in MB
            self.memory_usage.append(psutil.Process().memory_info().rss / 1024 / 1024)
            # CPU percentage
            self.cpu_usage.append(psutil.cpu_percent(interval=0.1))
        except Exception as e:
            logging.warning(f"Failed to capture system metrics: {e}")

    def get_execution_time(self) -> float:
        """Get execution time in seconds."""
        if self.end_time == 0:
            return time.time() - self.start_time
        return self.end_time - self.start_time

    def report(self) -> Dict[str, Any]:
        """Generate comprehensive metrics report."""
        return {
            "execution_time": self.get_execution_time(),
            "token_usage": self.token_usage,
            "execution_steps": self.execution_steps,
            "memory_usage": {
                "average": sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0,
                "peak": max(self.memory_usage) if self.memory_usage else 0,
                "current": self.memory_usage[-1] if self.memory_usage else 0
            },
            "cpu_usage": {
                "average": sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0,
                "peak": max(self.cpu_usage) if self.cpu_usage else 0
            },
            "custom_metrics": self.custom_metrics
        }

    def log_report(self, level: int = logging.INFO):
        """Log metrics report at specified level."""
        report_data = self.report()
        logging.log(level, f"Metrics Report: {report_data}")