"""
CharacterAgent: Develops detailed character profiles and personalities.
Creates nuanced, consistent characters for the story.
"""

from typing import Dict, Any, List
from .base_agent import Agent


class CharacterAgent(Agent):
    """
    Develops detailed character profiles with personalities and arcs.
    Ensures character consistency throughout the narrative.
    """

    def __init__(self, memory_module=None):
        """Initialize the CharacterAgent."""
        super().__init__("Character", memory_module)
        self.character_archetypes = [
            "hero",
            "mentor",
            "shadow",
            "ally",
            "herald",
            "shapeshifter",
            "trickster",
            "guardian",
        ]
        self.personality_traits = [
            "brave",
            "curious",
            "cunning",
            "compassionate",
            "ambitious",
            "humble",
            "pragmatic",
            "idealistic",
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate character profiles based on story context.

        Args:
            input_data: Contains 'story_outline', 'num_characters', 'themes'

        Returns:
            Dictionary with detailed character profiles
        """
        story_outline = input_data.get("story_outline", "")
        num_characters = input_data.get("num_characters", 3)
        themes = input_data.get("themes", [])

        # Log the process
        self.log_action(
            "process",
            {
                "story_outline": story_outline,
                "num_characters": num_characters,
            },
        )
        self.update_metrics(is_process=True)

        # Generate character profiles
        characters = self._generate_characters(
            story_outline, num_characters, themes
        )

        # Store in memory
        if self.memory:
            for char in characters:
                self.memory.store_memory(
                    "character_descriptions",
                    f"{char['name']}: {char['description']}",
                    {"agent": "Character", "role": char["role"]},
                )

        return {
            "agent": "Character",
            "characters": characters,
            "character_count": len(characters),
            "intermediate_output": f"Created {len(characters)} detailed character profiles",
        }

    def learn(self, feedback: Dict[str, Any]) -> None:
        """
        Learn from feedback about character development.

        Args:
            feedback: Contains 'score', 'character_names', and comments
        """
        score = feedback.get("score", 0.5)
        character_names = feedback.get("character_names", [])
        comments = feedback.get("comments", "")

        self.log_action(
            "learn",
            {"score": score, "characters": character_names, "comments": comments},
        )
        self.update_metrics(quality_score=score)

        if self.memory:
            self.memory.record_feedback(
                "Character",
                score,
                f"Characters: {character_names}. Feedback: {comments}",
            )

        self.learning_history.append(
            {
                "type": "character_feedback",
                "score": score,
                "characters": character_names,
                "comments": comments,
            }
        )

    def _generate_characters(
        self, story_outline: str, num_characters: int, themes: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate character profiles.

        Args:
            story_outline: The story outline context
            num_characters: Number of characters to create
            themes: Story themes to incorporate

        Returns:
            List of character profiles
        """
        characters = []
        roles = ["protagonist", "antagonist", "mentor", "ally", "rival"]

        # Derive simple name seeds from the story outline / themes
        seed_words = []
        for t in themes:
            if isinstance(t, str) and len(t) > 2:
                seed_words.append(t)
        # fallback: take words from outline
        if not seed_words:
            seed_words = [w for w in story_outline.split() if len(w) > 4][:3]

        def _make_name(base: str, idx: int) -> str:
            # Build a readable name using parts of base and index
            part = ''.join([c for c in base.title() if c.isalpha()])[:6]
            return f"{part}{idx+1}"

        for i in range(min(num_characters, len(roles))):
            theme_part = seed_words[i % len(seed_words)] if seed_words else "Story"
            name = _make_name(theme_part, i)
            traits_slice = [
                self.personality_traits[(i + j) % len(self.personality_traits)]
                for j in range(3)
            ]

            character = {
                "id": i + 1,
                "name": name,
                "role": roles[i],
                "archetype": self.character_archetypes[i % len(self.character_archetypes)],
                "traits": traits_slice,
                "backstory": f"Born from {theme_part}, {name} has ties to {themes[i % len(themes)] if themes else 'the core theme'}.",
                "motivations": [
                    "Personal growth",
                    f"Resolve {themes[i % len(themes)] if themes else 'the conflict'}",
                ],
                "arc": "transformation",
                "description": f"{name} is a {roles[i]} who is {', '.join(traits_slice)}.",
            }
            characters.append(character)

        return characters
