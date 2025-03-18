"""
Task model for representing tasks in the system
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json
from datetime import datetime

@dataclass
class Task:
    """Represents a task to be executed"""
    id: int
    status: str = "incomplete"
    ability: str = "text-completion"
    dependent_task_ids: List[int] = field(default_factory=list)
    output: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # These fields will store any additional attributes
    _additional_attributes: Dict[str, Any] = field(default_factory=dict)

    def __getattr__(self, name):
        """Allow access to additional attributes"""
        if name in self._additional_attributes:
            return self._additional_attributes[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary with flexible schema"""
        # Extract known fields
        task_id = data.pop("id")
        status = data.pop("status", "incomplete")
        ability = data.pop("ability", "text-completion")
        dependent_task_ids = data.pop("dependent_task_ids", [])

        # Handle datetime conversion
        created_at = data.pop("created_at", None)
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.now()

        completed_at = data.pop("completed_at", None)
        if completed_at and isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at)

        output = data.pop("output", None)
        metadata = data.pop("metadata", {})

        # Store all remaining fields as additional attributes
        task = cls(
            id=task_id,
            status=status,
            ability=ability,
            dependent_task_ids=dependent_task_ids,
            output=output,
            created_at=created_at,
            completed_at=completed_at,
            metadata=metadata
        )

        task._additional_attributes = data
        return task

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        result = {
            "id": self.id,
            "status": self.status,
            "ability": self.ability,
            "dependent_task_ids": self.dependent_task_ids,
            "output": self.output,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata
        }

        # Add all additional attributes
        result.update(self._additional_attributes)
        return result

    def __str__(self) -> str:
        """String representation of task"""
        # Try to use task or insight field for description
        description = self._additional_attributes.get("task",
                      self._additional_attributes.get("insight",
                      f"Task #{self.id}"))

        deps = f" (depends on: {self.dependent_task_ids})" if self.dependent_task_ids else ""
        return f"Task #{self.id}: {description} [{self.status}] [{self.ability}]{deps}"
    
    def mark_complete(self, output: str) -> None:
        """Mark task as complete with output"""
        self.status = "complete"
        self.output = output
        self.completed_at = datetime.now()
    
    def __str__(self) -> str:
        """String representation of task"""
        deps = f" (depends on: {self.dependent_task_ids})" if self.dependent_task_ids else ""
        return f"Task #{self.id}: {self.task} [{self.status}] [{self.ability}]{deps}"
    
    def to_json(self) -> str:
        """Convert task to JSON string"""
        return json.dumps(self.to_dict(), default=str)