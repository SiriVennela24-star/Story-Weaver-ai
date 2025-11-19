"""
FeedbackAgent: Analyzes and aggregates feedback from all agents.
Uses sentiment analysis to evaluate story quality.
"""

from typing import Dict, Any, List
from .base_agent import Agent


class FeedbackAgent(Agent):
    """
    Aggregates and analyzes feedback from all agents.
    Performs sentiment analysis and quality assessment.
    """

    def __init__(self, memory_module=None):
        """Initialize the FeedbackAgent."""
        super().__init__("Feedback", memory_module)
        self.quality_dimensions = [
            "coherence",
            "creativity",
            "emotional_impact",
            "character_development",
            "pacing",
            "originality",
        ]
        self.sentiment_labels = ["negative", "neutral", "positive"]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the complete pipeline output.

        Args:
            input_data: Contains 'story', 'characters', 'scenes', 'music'

        Returns:
            Dictionary with quality assessment and recommendations
        """
        story_output = input_data.get("story_output", {})
        characters = input_data.get("characters", [])
        scenes = input_data.get("scenes", [])
        music = input_data.get("music", [])

        # Log the process
        self.log_action("process", {"pipeline_stage": "final_assessment"})
        self.update_metrics(is_process=True)

        # Analyze all components
        quality_report = self._analyze_quality(
            story_output, characters, scenes, music
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(quality_report)

        # Store in memory
        if self.memory:
            self.memory.store_memory(
                "feedback_history",
                f"Pipeline Quality Report: {quality_report['overall_score']}",
                {
                    "agent": "Feedback",
                    "dimensions": quality_report["scores"],
                },
            )

        return {
            "agent": "Feedback",
            "quality_assessment": quality_report,
            "recommendations": recommendations,
            "intermediate_output": f"Final quality assessment: {quality_report['overall_score']:.2%}",
        }

    def learn(self, feedback: Dict[str, Any]) -> None:
        """
        Learn from user feedback on the entire pipeline.

        Args:
            feedback: Contains 'overall_score', 'dimension_feedback', comments
        """
        overall_score = feedback.get("overall_score", 0.5)
        dimension_feedback = feedback.get("dimension_feedback", {})
        comments = feedback.get("comments", "")

        self.log_action(
            "learn",
            {"overall_score": overall_score, "dimensions": dimension_feedback},
        )
        self.update_metrics(quality_score=overall_score)

        if self.memory:
            self.memory.record_feedback(
                "Feedback",
                overall_score,
                f"Dimensions: {dimension_feedback}. Comments: {comments}",
            )
            self.memory.update_learning_pattern("user_satisfaction", overall_score)

        self.learning_history.append(
            {
                "type": "overall_feedback",
                "overall_score": overall_score,
                "dimension_feedback": dimension_feedback,
                "comments": comments,
            }
        )

    def _analyze_quality(
        self,
        story: Dict[str, Any],
        characters: List[Dict[str, Any]],
        scenes: List[Dict[str, Any]],
        music: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze quality across multiple dimensions.

        Args:
            story: Story output from StoryDirector
            characters: Characters from CharacterAgent
            scenes: Scenes from SceneAgent
            music: Music metadata from MusicAgent

        Returns:
            Quality assessment report
        """
        scores = {}

        # Analyze each dimension
        scores["coherence"] = self._assess_coherence(story, characters, scenes)
        scores["creativity"] = self._assess_creativity(characters, scenes)
        scores["emotional_impact"] = self._assess_emotional_impact(scenes, music)
        scores["character_development"] = self._assess_character_development(
            characters
        )
        scores["pacing"] = self._assess_pacing(scenes, music)
        scores["originality"] = self._assess_originality(story, characters)

        # Calculate overall score
        overall_score = sum(scores.values()) / len(scores)

        return {
            "scores": scores,
            "overall_score": overall_score,
            "assessment_details": {
                "total_characters": len(characters),
                "total_scenes": len(scenes),
                "music_tracks": len(music),
                "story_acts": len(story.get("acts", [])),
            },
        }

    def _assess_coherence(
        self, story: Dict[str, Any], characters: List[Dict[str, Any]], scenes: List[Dict[str, Any]]
    ) -> float:
        """Assess narrative coherence."""
        # Simplified assessment - checks if all components exist
        coherence_score = 0.7
        if story and characters and scenes:
            coherence_score += 0.2
        if len(characters) >= 2 and len(scenes) >= 3:
            coherence_score = min(coherence_score + 0.1, 1.0)
        return coherence_score

    def _assess_creativity(
        self, characters: List[Dict[str, Any]], scenes: List[Dict[str, Any]]
    ) -> float:
        """Assess creative elements."""
        # Check for variety in archetypes and settings
        archetypes = set(c.get("archetype", "") for c in characters)
        settings = set(s.get("setting", "") for s in scenes)
        creativity_score = min(
            (len(archetypes) + len(settings)) / 10, 1.0
        )
        return creativity_score

    def _assess_emotional_impact(
        self, scenes: List[Dict[str, Any]], music: List[Dict[str, Any]]
    ) -> float:
        """Assess emotional resonance."""
        emotional_tones = set()
        for scene in scenes:
            emotional_tones.add(scene.get("emotional_tone", ""))
        for track in music:
            emotional_tones.add(track.get("emotional_tone", ""))

        # More emotional variety = higher impact
        impact_score = min(len(emotional_tones) / 6, 1.0)
        return impact_score

    def _assess_character_development(
        self, characters: List[Dict[str, Any]]
    ) -> float:
        """Assess character depth and development."""
        if not characters:
            return 0.0

        # Check for arcs and motivations
        developed_count = sum(
            1 for c in characters
            if c.get("arc") and c.get("motivations")
        )
        return min(developed_count / len(characters), 1.0)

    def _assess_pacing(
        self, scenes: List[Dict[str, Any]], music: List[Dict[str, Any]]
    ) -> float:
        """Assess narrative pacing."""
        if not scenes:
            return 0.7

        # Check for dynamic pacing in scenes
        dynamic_count = sum(
            1 for s in scenes
            if s.get("pacing", "").lower() in ["dynamic", "variable"]
        )
        pacing_score = min(0.5 + (dynamic_count / (len(scenes) + 1)), 1.0)

        # Music tempo variation also affects pacing
        if music:
            tempos = [m.get("tempo", 0) for m in music]
            if len(set(tempos)) > 1:  # Variety in tempos
                pacing_score = min(pacing_score + 0.2, 1.0)

        return pacing_score

    def _assess_originality(
        self, story: Dict[str, Any], characters: List[Dict[str, Any]]
    ) -> float:
        """Assess originality of the narrative."""
        originality_score = 0.5

        # Check for unique elements
        if story and len(story.get("themes", [])) > 2:
            originality_score += 0.2
        if characters and len(characters) > 2:
            originality_score += 0.15
        if story.get("story_outline", ""):
            originality_score += 0.15

        return min(originality_score, 1.0)

    def _generate_recommendations(
        self, quality_report: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Generate recommendations based on quality assessment.

        Args:
            quality_report: Quality assessment from analysis

        Returns:
            List of improvement recommendations
        """
        recommendations = []
        scores = quality_report.get("scores", {})

        for dimension, score in scores.items():
            if score < 0.5:
                recommendation = {
                    "dimension": dimension,
                    "priority": "high",
                    "suggestion": f"Improve {dimension}: {self._suggest_improvement(dimension)}",
                }
                recommendations.append(recommendation)
            elif score < 0.7:
                recommendation = {
                    "dimension": dimension,
                    "priority": "medium",
                    "suggestion": f"Enhance {dimension}: {self._suggest_enhancement(dimension)}",
                }
                recommendations.append(recommendation)

        return recommendations

    def _suggest_improvement(self, dimension: str) -> str:
        """Suggest improvements for a quality dimension."""
        suggestions = {
            "coherence": "Ensure all story elements are connected and consistent",
            "creativity": "Introduce more unique and diverse elements",
            "emotional_impact": "Develop stronger emotional connections in scenes",
            "character_development": "Add more depth and motivations to characters",
            "pacing": "Vary the rhythm and intensity throughout the story",
            "originality": "Explore more unconventional plot twists and themes",
        }
        return suggestions.get(dimension, "Work on improving this aspect")

    def _suggest_enhancement(self, dimension: str) -> str:
        """Suggest enhancements for a quality dimension."""
        enhancements = {
            "coherence": "Strengthen the connections between story elements",
            "creativity": "Experiment with fresh ideas and perspectives",
            "emotional_impact": "Deepen the emotional resonance of key moments",
            "character_development": "Expand character backgrounds and motivations",
            "pacing": "Fine-tune the narrative tempo for better flow",
            "originality": "Push creative boundaries further",
        }
        return enhancements.get(dimension, "Continue to refine this aspect")
