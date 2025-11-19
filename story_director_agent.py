"""
StoryDirectorAgent: Orchestrates overall narrative structure and pacing.
Generates the main storyline from a user prompt.
"""

from typing import Dict, Any
from .base_agent import Agent


class StoryDirectorAgent(Agent):
    """
    Orchestrates the overall narrative structure.
    Takes a prompt and creates the main story arc and pacing.
    """

    def __init__(self, memory_module=None):
        """Initialize the StoryDirectorAgent."""
        super().__init__("StoryDirector", memory_module)
        self.story_templates = [
            "classic_hero_journey",
            "mystery_investigation",
            "coming_of_age",
            "redemption_arc",
            "epic_adventure",
        ]
        self.pacing_strategies = ["fast", "moderate", "slow", "variable"]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate story structure from a prompt.

        Args:
            input_data: Contains 'prompt' and optional 'style' and 'length'

        Returns:
            Dictionary with story outline and structure
        """
        prompt = input_data.get("prompt", "")
        style = input_data.get("style", "adventure")
        length = input_data.get("length", "medium")

        # Log the process
        self.log_action("process", {"prompt": prompt, "style": style})
        self.update_metrics(is_process=True)

        # Store the initial prompt in memory
        if self.memory:
            self.memory.store_memory(
                "story_context",
                prompt,
                {
                    "agent": "StoryDirector",
                    "style": style,
                    "length": length,
                },
            )

        # Generate story structure (simulated - in production would use transformers)
        story_structure = self._generate_story_structure(prompt, style, length)

        return {
            "agent": "StoryDirector",
            "story_outline": story_structure["outline"],
            "acts": story_structure["acts"],
            "themes": story_structure["themes"],
            "pacing": story_structure["pacing"],
            "intermediate_output": f"Generated {style} story with {length} length",
        }

    def learn(self, feedback: Dict[str, Any]) -> None:
        """
        Learn from feedback about story quality.

        Args:
            feedback: Contains 'score' and optional 'comments'
        """
        score = feedback.get("score", 0.5)
        comments = feedback.get("comments", "")

        self.log_action("learn", {"score": score, "comments": comments})
        self.update_metrics(quality_score=score)

        if self.memory:
            self.memory.record_feedback(
                "StoryDirector", score, comments
            )

        self.learning_history.append(
            {
                "type": "story_quality_feedback",
                "score": score,
                "comments": comments,
            }
        )

    def _generate_story_structure(
        self, prompt: str, style: str, length: str
    ) -> Dict[str, Any]:
        """
        Generate story structure based on inputs.
        In production, this would use GPT or similar models.

        Args:
            prompt: User's story prompt
            style: Story style/genre
            length: Story length

        Returns:
            Dictionary with story structure
        """
        # Create a prompt-aware outline and simple themes by extracting keywords
        base_outline = f"A {style} story inspired by: {prompt}"

        # Simple keyword extraction: take the most significant words from the prompt
        words = [w.strip('.,!?') for w in prompt.split() if len(w) > 3]
        keywords = []
        for w in words:
            lw = w.lower()
            if lw not in keywords:
                keywords.append(lw)
            if len(keywords) >= 3:
                break

        # Build theme list using keywords if available, otherwise fall back to defaults
        if keywords:
            themes = [k for k in keywords]
        else:
            themes = [
                "discovery",
                "transformation",
                "connection",
            ]

        # Compose acts with small variations depending on prompt keywords and length
        acts = []
        num_acts = 3 if length == "short" else (4 if length == "medium" else 5)
        default_act_titles = [
            "Exposition",
            "Rising Action",
            "Climax",
            "Falling Action",
            "Denouement",
        ]

        for i in range(num_acts):
            title = default_act_titles[i]
            desc = f"{title}: develops {themes[i % len(themes)]} and builds on {keywords[0] if keywords else 'the core idea'}"
            acts.append({"act_number": i + 1, "title": title, "description": desc})

        pacing = {
            "tempo": "fast" if style in ("thriller", "adventure") else "moderate",
            "scene_duration": "short" if length == "short" else ("medium" if length == "medium" else "long"),
            "tension_curve": "rising" if "conflict" in prompt.lower() or "battle" in prompt.lower() else "dramatic",
        }

        outline = base_outline

        return {
            "outline": outline,
            "acts": acts,
            "themes": themes,
            "pacing": pacing,
        }
