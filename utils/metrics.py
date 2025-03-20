import time
import psutil
import logging
from functools import wraps
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
import threading
import json
from datetime import datetime
import os

# Configure logging
logger = logging.getLogger("metrics")

@dataclass
class TokenMetrics:
    """Track token usage for LLM operations"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def update(self, prompt_tokens: int = 0, completion_tokens: int = 0):
        """Update token counts"""
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.total_tokens = self.prompt_tokens + self.completion_tokens

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens
        }

@dataclass
class ExecutionMetrics:
    """Track execution time and performance metrics"""
    start_time: float = 0
    end_time: float = 0
    duration_ms: float = 0

    def start(self):
        """Mark the start of execution"""
        self.start_time = time.time()
        return self

    def end(self):
        """Mark the end of execution and calculate duration"""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        return self

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms
        }

@dataclass
class SystemMetrics:
    """Track system resource usage"""
    cpu_percent: float = 0
    memory_percent: float = 0
    memory_used_mb: float = 0

    def capture(self):
        """Capture current system metrics"""
        self.cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        self.memory_percent = memory.percent
        self.memory_used_mb = memory.used / (1024 * 1024)  # Convert to MB
        return self

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_used_mb": self.memory_used_mb
        }

@dataclass
class TaskMetrics:
    """Track metrics for a specific task"""
    task_id: str
    task_type: str
    execution: ExecutionMetrics = field(default_factory=ExecutionMetrics)
    tokens: TokenMetrics = field(default_factory=TokenMetrics)
    system: SystemMetrics = field(default_factory=SystemMetrics)
    subtasks: List['TaskMetrics'] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "execution": self.execution.to_dict(),
            "tokens": self.tokens.to_dict(),
            "system": self.system.to_dict(),
            "subtasks": [st.to_dict() for st in self.subtasks],
            "status": self.status,
            "error": self.error
        }

@dataclass
class SessionMetrics:
    """Track metrics for an entire session"""
    session_id: str
    start_time: float = field(default_factory=time.time)
    tasks: List[TaskMetrics] = field(default_factory=list)
    total_tokens: TokenMetrics = field(default_factory=TokenMetrics)

    def add_task(self, task: TaskMetrics):
        """Add a task to the session and update totals"""
        self.tasks.append(task)
        self.total_tokens.update(
            prompt_tokens=task.tokens.prompt_tokens,
            completion_tokens=task.tokens.completion_tokens
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "end_time": time.time(),
            "duration_s": time.time() - self.start_time,
            "tasks": [task.to_dict() for task in self.tasks],
            "total_tokens": self.total_tokens.to_dict()
        }

class MetricsManager:
    """Singleton manager for tracking metrics across the application"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MetricsManager, cls).__new__(cls)
                cls._instance._sessions = {}
                cls._instance._current_session_id = None
                cls._instance._metrics_dir = "metrics"

                # Create metrics directory if it doesn't exist
                if not os.path.exists(cls._instance._metrics_dir):
                    os.makedirs(cls._instance._metrics_dir)

        return cls._instance

    def start_session(self, session_id: Optional[str] = None) -> str:
        """Start a new metrics session"""
        if session_id is None:
            session_id = f"session_{int(time.time())}"

        self._current_session_id = session_id
        self._sessions[session_id] = SessionMetrics(session_id=session_id)
        logger.info(f"Started metrics session: {session_id}")
        return session_id

    def get_current_session(self) -> Optional[SessionMetrics]:
        """Get the current active session"""
        if self._current_session_id is None:
            return None
        return self._sessions.get(self._current_session_id)

    def track_task(self, task_id: str, task_type: str) -> TaskMetrics:
        """Create and track a new task in the current session"""
        session = self.get_current_session()
        if session is None:
            self.start_session()
            session = self.get_current_session()

        task = TaskMetrics(task_id=task_id, task_type=task_type)
        session.add_task(task)
        return task

    def save_session(self, session_id: Optional[str] = None):
        """Save session metrics to disk"""
        if session_id is None:
            session_id = self._current_session_id

        if session_id is None or session_id not in self._sessions:
            logger.warning(f"No session found with ID: {session_id}")
            return

        session = self._sessions[session_id]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self._metrics_dir}/{session_id}_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)

        logger.info(f"Saved session metrics to {filename}")
        return filename

def track_execution(task_id: str, task_type: str):
    """Decorator to track execution metrics for a function"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            manager = MetricsManager()
            task = manager.track_task(task_id, task_type)
            task.status = "running"
            task.system.capture()
            task.execution.start()

            try:
                result = func(*args, **kwargs)
                task.status = "completed"
                return result
            except Exception as e:
                task.status = "failed"
                task.error = str(e)
                raise
            finally:
                task.execution.end()
                task.system.capture()

        return wrapper
    return decorator

def track_llm_usage(prompt_tokens: int, completion_tokens: int, task_id: str):
    """Update token usage for a specific task"""
    manager = MetricsManager()
    session = manager.get_current_session()

    if session is None:
        logger.warning("No active session found for token tracking")
        return

    for task in session.tasks:
        if task.task_id == task_id:
            task.tokens.update(prompt_tokens, completion_tokens)
            break

def get_metrics_summary() -> Dict:
    """Get a summary of current metrics"""
    manager = MetricsManager()
    session = manager.get_current_session()

    if session is None:
        return {"error": "No active session"}

    total_execution_time = sum(task.execution.duration_ms for task in session.tasks)

    return {
        "session_id": session.session_id,
        "duration_s": time.time() - session.start_time,
        "tasks_count": len(session.tasks),
        "total_execution_ms": total_execution_time,
        "total_tokens": session.total_tokens.to_dict(),
        "system": SystemMetrics().capture().to_dict()
    }