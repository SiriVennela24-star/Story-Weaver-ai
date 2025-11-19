"""
Base Agent class that defines the interface for all specialized agents.
Each agent must implement process() and learn() methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class Agent(ABC):
    """
    Abstract base class for all agents in StoryWeaver AI.
    Defines the interface for processing input and learning from feedback.
    """

    def __init__(self, name: str, memory_module=None):
        """
        Initialize an agent.

        Args:
            name: Agent name (e.g., "StoryDirector")
            memory_module: Reference to the central MemoryModule
        """
        self.name = name
        self.memory = memory_module
        self.learning_history: List[Dict[str, Any]] = []
        self.performance_metrics = {
            "total_processes": 0,
            "total_feedback": 0,
            "average_quality": 0.0,
        }

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and generate output.

        Args:
            input_data: Dictionary containing input parameters

        Returns:
            Dictionary with processed output
        """
        pass

    @abstractmethod
    def learn(self, feedback: Dict[str, Any]) -> None:
        """
        Learn from feedback to improve future performance.

        Args:
            feedback: Dictionary containing feedback (score, text, etc.)
        """
        pass

    def update_metrics(
        self, quality_score: float = None, is_process: bool = False
    ) -> None:
        """
        Update performance metrics.

        Args:
            quality_score: Quality score for this interaction (0-1)
            is_process: Whether this is a process call or feedback
        """
        if is_process:
            self.performance_metrics["total_processes"] += 1
        else:
            self.performance_metrics["total_feedback"] += 1

            if quality_score is not None:
                # Update running average
                current_avg = self.performance_metrics["average_quality"]
                total = self.performance_metrics["total_feedback"]
                self.performance_metrics["average_quality"] = (
                    current_avg * (total - 1) + quality_score
                ) / total

    def get_metrics(self) -> Dict[str, Any]:
        """
        Retrieve current performance metrics.

        Returns:
            Dictionary with current metrics
        """
        return self.performance_metrics.copy()

    def log_action(
        self, action_type: str, details: Dict[str, Any] = None
    ) -> None:
        """
        Log an agent action to learning history.

        Args:
            action_type: Type of action (process, feedback, etc.)
            details: Additional details about the action
        """
        entry = {
            "agent": self.name,
            "action": action_type,
            "details": details or {},
        }
        self.learning_history.append(entry)
