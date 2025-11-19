# StoryWeaver AI - API Examples

This file contains example requests for testing the StoryWeaver API.

## Tools to Use

- **curl** (command line)
- **Postman** (GUI)
- **VS Code REST Client** extension
- **Python requests** module
- **Browser Developer Tools** (Network tab)

---

## 1. Health Check

### Request
```http
GET http://localhost:5000/health
```

### Response
```json
{
    "status": "healthy",
    "service": "StoryWeaver AI Backend"
}
```

---

## 2. Generate Story

### Request
```http
POST http://localhost:5000/generate
Content-Type: application/json

{
    "prompt": "A young explorer discovers an ancient artifact in a forgotten temple",
    "style": "adventure",
    "length": "medium",
    "num_characters": 4
}
```

### Example Prompts

**Adventure:**
```json
{
    "prompt": "A seasoned sailor discovers a mysterious island with glowing crystals",
    "style": "adventure",
    "length": "medium",
    "num_characters": 3
}
```

**Mystery:**
```json
{
    "prompt": "A detective uncovers strange clues in an abandoned mansion",
    "style": "mystery",
    "length": "long",
    "num_characters": 5
}
```

**Fantasy:**
```json
{
    "prompt": "A young mage discovers they are the chosen one",
    "style": "fantasy",
    "length": "medium",
    "num_characters": 3
}
```

**Sci-Fi:**
```json
{
    "prompt": "Humans make first contact with an alien civilization",
    "style": "sci-fi",
    "length": "long",
    "num_characters": 4
}
```

**Romance:**
```json
{
    "prompt": "Two rival artists meet at a gallery opening",
    "style": "romance",
    "length": "medium",
    "num_characters": 2
}
```

**Thriller:**
```json
{
    "prompt": "A whistleblower uncovers a dangerous conspiracy",
    "style": "thriller",
    "length": "medium",
    "num_characters": 4
}
```

### Response
```json
{
    "status": "success",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-01-15T10:30:45.123456",
    "story": {
        "agent": "StoryDirector",
        "story_outline": "A adventure story based on: A young explorer...",
        "acts": [
            {
                "act_number": 1,
                "title": "Exposition",
                "description": "Introduction of characters and setting"
            },
            ...
        ],
        "themes": ["heroism", "discovery", "transformation", ...],
        "pacing": {
            "tempo": "moderate",
            "scene_duration": "medium",
            "tension_curve": "dramatic"
        },
        "intermediate_output": "Generated adventure story with medium length"
    },
    "characters": [
        {
            "id": 1,
            "name": "Character_1",
            "role": "protagonist",
            "archetype": "hero",
            "traits": ["brave", "curious", "cunning"],
            "backstory": "A unique character...",
            "motivations": ["Personal growth", "Achieve goal", "Overcome fear"],
            "arc": "transformation",
            "description": "A protagonist character with brave personality"
        },
        ...
    ],
    "scenes": [
        {
            "act": 1,
            "title": "Exposition",
            "description": "Introduction of characters and setting",
            "setting": "urban",
            "atmosphere": {
                "lighting": "Evocative lighting details",
                "sounds": "Immersive sounds",
                "smells": "Evocative smells details"
            },
            "characters_involved": [1, 2],
            "key_events": ["Event 1 occurs in this scene", ...],
            "sensory_details": {
                "visual": "Vivid visual imagery",
                "auditory": "Immersive sounds",
                "tactile": "Textured descriptions"
            },
            "emotional_tone": "Compelling",
            "pacing": "Dynamic"
        },
        ...
    ],
    "music": [
        {
            "track_id": 1,
            "title": "Scene 1: Exposition",
            "description": "Musical accompaniment for Exposition",
            "genre": "orchestral",
            "tempo": 100,
            "key": "D major",
            "instruments": ["strings", "piano", "flute"],
            "emotional_tone": "heroic",
            "duration_seconds": 180,
            "themes_incorporated": ["heroism", "discovery"],
            "structure": {
                "intro": 20,
                "verse": 60,
                "chorus": 40,
                "bridge": 30,
                "outro": 30
            },
            "lstm_sequence": [60, 62, 64, 65, 67, 69, 71, 72, ...]
        },
        ...
    ],
    "quality_assessment": {
        "scores": {
            "coherence": 0.85,
            "creativity": 0.78,
            "emotional_impact": 0.82,
            "character_development": 0.80,
            "pacing": 0.87,
            "originality": 0.75
        },
        "overall_score": 0.81,
        "assessment_details": {
            "total_characters": 4,
            "total_scenes": 5,
            "music_tracks": 5,
            "story_acts": 5
        }
    },
    "recommendations": [
        {
            "dimension": "creativity",
            "priority": "medium",
            "suggestion": "Enhance creativity: Experiment with fresh ideas and perspectives"
        },
        ...
    ],
    "pipeline_log": [
        {
            "timestamp": "2024-01-15T10:30:45.123456",
            "event_type": "session_start",
            "details": {"prompt": "A young explorer...", "parameters": {...}}
        },
        {
            "timestamp": "2024-01-15T10:30:46.234567",
            "event_type": "story_generation_start",
            "details": {"agent": "StoryDirector"}
        },
        ...
    ],
    "memory_summary": {
        "story_context": 1,
        "character_descriptions": 4,
        "scene_settings": 5,
        "music_metadata": 5,
        "feedback_history": 0
    },
    "learning_stats": {
        "story_coherence": {
            "mean": 0.0,
            "std": 0.0,
            "max": 0.0,
            "min": 0.0,
            "count": 0
        },
        ...
    }
}
```

---

## 3. Provide Feedback

### Request
```http
POST http://localhost:5000/feedback
Content-Type: application/json

{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "overall_score": 0.85,
    "dimension_feedback": {
        "coherence": 0.9,
        "creativity": 0.8,
        "emotional_impact": 0.85,
        "character_development": 0.8,
        "pacing": 0.85,
        "originality": 0.8
    },
    "comments": "Great story! The characters were well-developed and the pacing was excellent."
}
```

### Response
```json
{
    "status": "success",
    "message": "Feedback recorded and agents updated",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## 4. Get Agent Metrics

### Request
```http
GET http://localhost:5000/metrics
```

### Response
```json
{
    "agents": {
        "StoryDirector": {
            "total_processes": 5,
            "total_feedback": 2,
            "average_quality": 0.82
        },
        "Character": {
            "total_processes": 5,
            "total_feedback": 2,
            "average_quality": 0.80
        },
        "Scene": {
            "total_processes": 5,
            "total_feedback": 2,
            "average_quality": 0.81
        },
        "Music": {
            "total_processes": 5,
            "total_feedback": 2,
            "average_quality": 0.79
        },
        "Feedback": {
            "total_processes": 5,
            "total_feedback": 2,
            "average_quality": 0.81
        }
    },
    "memory": {
        "memory_summary": {
            "story_context": 5,
            "character_descriptions": 20,
            "scene_settings": 25,
            "music_metadata": 5,
            "feedback_history": 2
        },
        "learning_stats": {
            "story_coherence": {
                "mean": 0.82,
                "std": 0.03,
                "max": 0.87,
                "min": 0.78,
                "count": 5
            },
            ...
        }
    }
}
```

---

## 5. Get Memory Status

### Request
```http
GET http://localhost:5000/memory
```

### Response
```json
{
    "memory_summary": {
        "story_context": 5,
        "character_descriptions": 20,
        "scene_settings": 25,
        "music_metadata": 5,
        "feedback_history": 2
    },
    "learning_stats": {
        "story_coherence": {
            "mean": 0.82,
            "std": 0.03,
            "max": 0.87,
            "min": 0.78,
            "count": 5
        },
        "character_consistency": {
            "mean": 0.80,
            "std": 0.04,
            "max": 0.85,
            "min": 0.75,
            "count": 5
        },
        ...
    }
}
```

---

## 6. Reset Orchestrator

### Request
```http
POST http://localhost:5000/reset
```

### Response
```json
{
    "status": "success",
    "message": "Orchestrator reset successfully"
}
```

---

## Python Examples

### Generate Story
```python
import requests
import json

url = "http://localhost:5000/generate"
payload = {
    "prompt": "A mysterious door appears in the forest",
    "style": "fantasy",
    "length": "medium",
    "num_characters": 3
}

response = requests.post(url, json=payload)
data = response.json()

if data['status'] == 'success':
    session_id = data['session_id']
    print(f"Story generated! Session: {session_id}")
    print(f"Quality Score: {data['quality_assessment']['overall_score']:.2%}")
else:
    print(f"Error: {data['error']}")
```

### Submit Feedback
```python
import requests

url = "http://localhost:5000/feedback"
payload = {
    "session_id": "your-session-id",
    "overall_score": 0.85,
    "dimension_feedback": {
        "coherence": 0.9,
        "creativity": 0.8,
        "emotional_impact": 0.85,
        "character_development": 0.8,
        "pacing": 0.85,
        "originality": 0.8
    },
    "comments": "Excellent story!"
}

response = requests.post(url, json=payload)
print(response.json())
```

### Get Metrics
```python
import requests

url = "http://localhost:5000/metrics"
response = requests.get(url)
metrics = response.json()

for agent, data in metrics['agents'].items():
    print(f"{agent}: {data['average_quality']:.2%} average quality")
```

---

## cURL Examples

### Generate Story
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A detective solves a mysterious case",
    "style": "mystery",
    "length": "medium",
    "num_characters": 3
  }'
```

### Submit Feedback
```bash
curl -X POST http://localhost:5000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "overall_score": 0.85,
    "dimension_feedback": {
      "coherence": 0.9,
      "creativity": 0.8
    },
    "comments": "Great story!"
  }'
```

### Get Metrics
```bash
curl http://localhost:5000/metrics
```

---

## Performance Tips

1. **First request takes longer** - Models are loaded on first use
2. **Keep prompts concise** - Shorter prompts generate faster
3. **Feedback improves future generations** - Provide quality feedback
4. **Check metrics periodically** - Monitor agent performance

---

**Happy API Testing! 🚀**
