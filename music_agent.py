"""
MusicAgent: Generates music metadata and soundtrack recommendations.
Uses PyTorch LSTM (stub) for music composition metadata.
"""

from typing import Dict, Any, List
from .base_agent import Agent


class MusicAgent(Agent):
    """
    Generates music metadata and soundtrack recommendations.
    Matches musical elements to story emotions and pacing.
    """

    def __init__(self, memory_module=None):
        """Initialize the MusicAgent."""
        super().__init__("Music", memory_module)
        self.music_genres = [
            "orchestral",
            "electronic",
            "ambient",
            "jazz",
            "classical",
            "folk",
            "cinematic",
            "experimental",
        ]
        self.instruments = [
            "strings",
            "piano",
            "flute",
            "drums",
            "synth",
            "choir",
            "guitar",
            "woodwinds",
        ]
        self.emotional_tones = [
            "heroic",
            "melancholic",
            "mysterious",
            "joyful",
            "tense",
            "peaceful",
            "dramatic",
            "romantic",
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate music metadata and recommendations.

        Args:
            input_data: Contains 'scenes', 'themes', 'characters'

        Returns:
            Dictionary with music metadata and recommendations
        """
        scenes = input_data.get("scenes", [])
        themes = input_data.get("themes", [])
        characters = input_data.get("characters", [])

        # Log the process
        self.log_action(
            "process",
            {"num_scenes": len(scenes), "themes": themes},
        )
        self.update_metrics(is_process=True)

        # Generate music metadata
        music_tracks = self._generate_music_metadata(scenes, themes, characters)

        # Store in memory
        if self.memory:
            for track in music_tracks:
                self.memory.store_memory(
                    "music_metadata",
                    f"{track['title']}: {track['description']}",
                    {
                        "agent": "Music",
                        "genre": track["genre"],
                        "tempo": track["tempo"],
                    },
                )

        return {
            "agent": "Music",
            "tracks": music_tracks,
            "track_count": len(music_tracks),
            "intermediate_output": f"Generated {len(music_tracks)} music tracks with metadata",
        }

    def learn(self, feedback: Dict[str, Any]) -> None:
        """
        Learn from feedback about music relevance and quality.

        Args:
            feedback: Contains 'score', 'track_feedback', and comments
        """
        score = feedback.get("score", 0.5)
        track_feedback = feedback.get("track_feedback", "")
        comments = feedback.get("comments", "")

        self.log_action(
            "learn",
            {"score": score, "track_feedback": track_feedback},
        )
        self.update_metrics(quality_score=score)

        if self.memory:
            self.memory.record_feedback(
                "Music", score, f"Music feedback: {track_feedback}. {comments}"
            )

        self.learning_history.append(
            {
                "type": "music_feedback",
                "score": score,
                "track_feedback": track_feedback,
                "comments": comments,
            }
        )

    def _generate_music_metadata(
        self, scenes: List[Dict[str, Any]], themes: List[str], characters: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate music metadata using LSTM-inspired approach (stub).
        In production, would use PyTorch LSTM for sequence generation.

        Args:
            scenes: Scene descriptions
            themes: Story themes
            characters: Character profiles

        Returns:
            List of music track metadata
        """
        tracks = []

        for i, scene in enumerate(scenes[:5]):  # Max 5 tracks
            # Create music metadata based on scene emotional tone
            emotional_tone = self.emotional_tones[i % len(self.emotional_tones)]

            track = {
                "track_id": i + 1,
                "title": f"Scene {i+1}: {scene.get('title', 'Untitled')}",
                "description": f"Musical accompaniment for {scene.get('title')}",
                "genre": self.music_genres[i % len(self.music_genres)],
                "tempo": self._calculate_tempo(
                    scene.get("pacing", "Dynamic")
                ),
                "key": self._select_key(emotional_tone),
                "instruments": self.instruments[i : i + 3],
                "emotional_tone": emotional_tone,
                "duration_seconds": 180 + (i * 30),  # Varying lengths
                "dynamics": "varied",
                "themes_incorporated": themes[: min(2, len(themes))],
                "structure": {
                    "intro": 20,
                    "verse": 60,
                    "chorus": 40,
                    "bridge": 30,
                    "outro": 30,
                },
                "lstm_sequence": self._generate_lstm_stub(i),
            }
            tracks.append(track)

        return tracks

    def _calculate_tempo(self, pacing: str) -> int:
        """
        Calculate musical tempo based on scene pacing.

        Args:
            pacing: Scene pacing description

        Returns:
            BPM (beats per minute)
        """
        pacing_map = {
            "fast": 140,
            "moderate": 100,
            "slow": 60,
            "variable": 90,
        }
        return pacing_map.get(pacing.lower(), 90)

    def _select_key(self, emotional_tone: str) -> str:
        """
        Select musical key based on emotional tone.

        Args:
            emotional_tone: Emotional tone of the scene

        Returns:
            Musical key notation
        """
        key_map = {
            "heroic": "D major",
            "melancholic": "E minor",
            "mysterious": "B minor",
            "joyful": "G major",
            "tense": "F# minor",
            "peaceful": "C major",
            "dramatic": "A minor",
            "romantic": "F major",
        }
        return key_map.get(emotional_tone, "C major")

    def _generate_lstm_stub(self, seed: int) -> List[int]:
        """
        Stub for LSTM-generated music sequence.
        In production, would use PyTorch LSTM.

        Args:
            seed: Seed value for deterministic generation

        Returns:
            List of MIDI note numbers (stub)
        """
        # Stub LSTM output - sequence of MIDI notes
        import random

        random.seed(seed)
        base_notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C major scale
        return [random.choice(base_notes) for _ in range(16)]
