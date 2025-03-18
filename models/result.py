"""
Result model for representing execution results
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
import json

@dataclass
class Result:
    """Represents the result of a task execution"""
    task_id: int
    content: str
    success: bool = True
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "task_id": self.task_id,
            "content": self.content,
            "success": self.success,
            "error": self.error,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Result':
        """Create result from dictionary"""
        # Handle datetime conversion
        timestamp = data.get("timestamp")
        if timestamp and isinstance(timestamp, str):
            data["timestamp"] = datetime.fromisoformat(timestamp)

        return cls(**data)

    def to_json(self) -> str:
        """Convert result to JSON string"""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def error_result(cls, task_id: int, error_message: str) -> 'Result':
        """Create an error result"""
        return cls(
            task_id=task_id,
            content="",
            success=False,
            error=error_message
        )