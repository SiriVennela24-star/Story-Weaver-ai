"""
SceneAgent: Builds vivid scenes and settings for the story.
Manages setting descriptions, atmosphere, and scene sequencing.
"""

from typing import Dict, Any, List
from .base_agent import Agent


class SceneAgent(Agent):
    """
    Develops detailed scenes and settings.
    Creates vivid, immersive environments for the narrative.
    """

    def __init__(self, memory_module=None):
        """Initialize the SceneAgent."""
        super().__init__("Scene", memory_module)
        self.setting_types = [
            "urban",
            "rural",
            "fantasy",
            "sci-fi",
            "historical",
            "domestic",
            "wilderness",
            "otherworldly",
        ]
        self.atmospheric_elements = [
            "lighting",
            "sounds",
            "smells",
            "temperature",
            "textures",
            "colors",
            "weather",
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate scene descriptions based on story and characters.

        Args:
            input_data: Contains 'acts', 'characters', 'themes'

        Returns:
            Dictionary with detailed scene descriptions
        """
        acts = input_data.get("acts", [])
        characters = input_data.get("characters", [])
        themes = input_data.get("themes", [])

        # Log the process
        self.log_action(
            "process",
            {"num_acts": len(acts), "num_characters": len(characters)},
        )
        self.update_metrics(is_process=True)

        # Generate scenes for each act
        scenes = self._generate_scenes(acts, characters, themes)

        # Store in memory
        if self.memory:
            for scene in scenes:
                self.memory.store_memory(
                    "scene_settings",
                    f"Act {scene['act']}: {scene['title']} - {scene['setting']}",
                    {"agent": "Scene", "atmosphere": scene["atmosphere"]},
                )

        return {
            "agent": "Scene",
            "scenes": scenes,
            "scene_count": len(scenes),
            "intermediate_output": f"Created {len(scenes)} vivid scene descriptions",
        }

    def learn(self, feedback: Dict[str, Any]) -> None:
        """
        Learn from feedback about scene vividness and coherence.

        Args:
            feedback: Contains 'score', 'scene_feedback', and comments
        """
        score = feedback.get("score", 0.5)
        scene_feedback = feedback.get("scene_feedback", "")
        comments = feedback.get("comments", "")

        self.log_action(
            "learn",
            {"score": score, "scene_feedback": scene_feedback},
        )
        self.update_metrics(quality_score=score)

        if self.memory:
            self.memory.record_feedback(
                "Scene", score, f"Scene feedback: {scene_feedback}. {comments}"
            )

        self.learning_history.append(
            {
                "type": "scene_feedback",
                "score": score,
                "scene_feedback": scene_feedback,
                "comments": comments,
            }
        )

    def _generate_scenes(
        self, acts: List[Dict[str, Any]], characters: List[Dict[str, Any]], themes: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate detailed scene descriptions.

        Args:
            acts: Story acts from StoryDirector
            characters: Character profiles
            themes: Story themes

        Returns:
            List of scene descriptions
        """
        scenes = []

        for i, act in enumerate(acts[:5]):  # Max 5 acts
            scene = {
                "act": act.get("act_number", i + 1),
                "title": act.get("title", f"Scene {i+1}"),
                "description": act.get("description", ""),
                "setting": self.setting_types[i % len(self.setting_types)],
                "atmosphere": {
                    elem: f"Evocative {elem} details"
                    for elem in self.atmospheric_elements[:3]
                },
                "characters_involved": [
                    c["id"]
                    for c in characters[: min(2, len(characters))]
                ],
                "key_events": [
                    f"Event {j+1} occurs in this scene"
                    for j in range(3)
                ],
                "sensory_details": {
                    "visual": "Vivid visual imagery",
                    "auditory": "Immersive sounds",
                    "tactile": "Textured descriptions",
                },
                "emotional_tone": "Compelling",
                "pacing": "Dynamic",
            }
            scenes.append(scene)

        return scenes
