"""
StoryWeaver Orchestrator: Coordinates all agents in a pipeline.
Manages the sequence of processing and logging of intermediate outputs.
"""

import json
from typing import Dict, Any, List
from datetime import datetime
from backend.agents import (
    StoryDirectorAgent,
    CharacterAgent,
    SceneAgent,
    MusicAgent,
    FeedbackAgent,
)
from backend.memory.memory_module import MemoryModule


class StoryWeaverOrchestrator:
    """
    Main orchestrator that coordinates all agents in a storytelling pipeline.
    Manages data flow, logging, and integration with the MemoryModule.
    """

    def __init__(self):
        """Initialize the orchestrator with all agents and memory module."""
        self.memory = MemoryModule()

        # Initialize all agents
        self.story_director = StoryDirectorAgent(self.memory)
        self.character_agent = CharacterAgent(self.memory)
        self.scene_agent = SceneAgent(self.memory)
        self.music_agent = MusicAgent(self.memory)
        self.feedback_agent = FeedbackAgent(self.memory)

        self.agents = [
            self.story_director,
            self.character_agent,
            self.scene_agent,
            self.music_agent,
            self.feedback_agent,
        ]

        # Pipeline state
        self.pipeline_log: List[Dict[str, Any]] = []
        self.current_session_id = None

    def generate_story(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Execute the complete storytelling pipeline.

        Args:
            prompt: User's story prompt
            **kwargs: Additional parameters (style, length, num_characters, etc.)

        Returns:
            Dictionary with complete pipeline output and logs
        """
        session_id = self._generate_session_id()
        self.current_session_id = session_id

        # Clear pipeline log
        self.pipeline_log = []

        self._log_event("session_start", {"prompt": prompt, "parameters": kwargs})

        try:
            # Stage 1: Story Direction
            story_output = self._execute_agent(
                self.story_director,
                {
                    "prompt": prompt,
                    "style": kwargs.get("style", "adventure"),
                    "length": kwargs.get("length", "medium"),
                },
                "story_generation",
            )

            # Stage 2: Character Development
            character_output = self._execute_agent(
                self.character_agent,
                {
                    "story_outline": story_output.get("story_outline", ""),
                    "num_characters": kwargs.get("num_characters", 3),
                    "themes": story_output.get("themes", []),
                },
                "character_development",
            )

            # Stage 3: Scene Building
            scene_output = self._execute_agent(
                self.scene_agent,
                {
                    "acts": story_output.get("acts", []),
                    "characters": character_output.get("characters", []),
                    "themes": story_output.get("themes", []),
                },
                "scene_building",
            )

            # Stage 4: Music Generation
            music_output = self._execute_agent(
                self.music_agent,
                {
                    "scenes": scene_output.get("scenes", []),
                    "themes": story_output.get("themes", []),
                    "characters": character_output.get("characters", []),
                },
                "music_generation",
            )

            # Stage 5: Quality Assessment
            feedback_output = self._execute_agent(
                self.feedback_agent,
                {
                    "story_output": story_output,
                    "characters": character_output.get("characters", []),
                    "scenes": scene_output.get("scenes", []),
                    "music": music_output.get("tracks", []),
                },
                "quality_assessment",
            )

            # Compile final result
            final_result = {
                "status": "success",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "story": story_output,
                "characters": character_output.get("characters", []),
                "scenes": scene_output.get("scenes", []),
                "music": music_output.get("tracks", []),
                "quality_assessment": feedback_output.get("quality_assessment", {}),
                "recommendations": feedback_output.get("recommendations", []),
                "pipeline_log": self.pipeline_log,
                "memory_summary": self.memory.get_memory_summary(),
                "learning_stats": self.memory.get_learning_stats(),
            }

            self._log_event("session_complete", {"status": "success"})
            return final_result

        except Exception as e:
            self._log_event("session_error", {"error": str(e)})
            return {
                "status": "error",
                "session_id": session_id,
                "error": str(e),
                "pipeline_log": self.pipeline_log,
            }

    def _execute_agent(
        self,
        agent,
        input_data: Dict[str, Any],
        stage_name: str,
    ) -> Dict[str, Any]:
        """
        Execute a single agent in the pipeline.

        Args:
            agent: Agent instance to execute
            input_data: Input data for the agent
            stage_name: Name of the pipeline stage

        Returns:
            Agent output
        """
        try:
            self._log_event(f"{stage_name}_start", {"agent": agent.name})

            # Execute agent
            output = agent.process(input_data)

            # Log intermediate output
            self._log_event(
                f"{stage_name}_output",
                {
                    "agent": agent.name,
                    "status": "success",
                    "message": output.get("intermediate_output", ""),
                },
            )

            return output

        except Exception as e:
            self._log_event(
                f"{stage_name}_error",
                {"agent": agent.name, "error": str(e)},
            )
            raise

    def provide_feedback(
        self,
        session_id: str,
        overall_score: float,
        dimension_feedback: Dict[str, float] = None,
        comments: str = "",
    ) -> Dict[str, Any]:
        """
        Provide feedback on a generated story to enable learning.

        Args:
            session_id: ID of the session to provide feedback for
            overall_score: Overall quality score (0-1)
            dimension_feedback: Scores for each quality dimension
            comments: Optional comments about the story

        Returns:
            Feedback processing result
        """
        feedback_data = {
            "overall_score": overall_score,
            "dimension_feedback": dimension_feedback or {},
            "comments": comments,
        }

        self._log_event("feedback_received", feedback_data)

        # Have each agent learn from feedback
        for agent in self.agents:
            try:
                agent.learn(feedback_data)
            except Exception as e:
                self._log_event(
                    "feedback_error",
                    {"agent": agent.name, "error": str(e)},
                )

        return {
            "status": "success",
            "message": "Feedback recorded and agents updated",
            "session_id": session_id,
        }

    def get_agent_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get performance metrics for all agents.

        Returns:
            Dictionary with metrics for each agent
        """
        metrics = {}
        for agent in self.agents:
            metrics[agent.name] = agent.get_metrics()
        return metrics

    def get_memory_status(self) -> Dict[str, Any]:
        """
        Get current memory module status.

        Returns:
            Dictionary with memory summary and learning stats
        """
        return {
            "memory_summary": self.memory.get_memory_summary(),
            "learning_stats": self.memory.get_learning_stats(),
        }

    def get_pipeline_log(self, session_id: str = None) -> List[Dict[str, Any]]:
        """
        Get pipeline execution log.

        Args:
            session_id: Optional session ID to filter logs

        Returns:
            List of log entries
        """
        if session_id == self.current_session_id or not session_id:
            return self.pipeline_log
        return []

    def _log_event(self, event_type: str, details: Dict[str, Any] = None) -> None:
        """
        Log an event in the pipeline.

        Args:
            event_type: Type of event
            details: Event details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details or {},
        }
        self.pipeline_log.append(log_entry)

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        import uuid

        return str(uuid.uuid4())

    def reset(self) -> None:
        """Reset the orchestrator state."""
        self.memory.clear_memory()
        self.pipeline_log = []
        self.current_session_id = None
        for agent in self.agents:
            agent.learning_history = []
