"""
Flask API for StoryWeaver AI.
Provides RESTful endpoints for story generation and feedback.
"""

import sys
import types
import numpy as np

# Inject mock sentence-transformers if not installed
if 'sentence_transformers' not in sys.modules:
    fake_st = types.SimpleNamespace()
    class FakeModel:
        def __init__(self, model_name=None):
            self.model_name = model_name
        def encode(self, texts, convert_to_numpy=True):
            if isinstance(texts, (list, tuple)):
                texts = texts[0]
            h = abs(hash(str(texts))) % (10**8)
            rng = np.random.RandomState(h)
            return rng.rand(384)
    fake_st.SentenceTransformer = FakeModel
    sys.modules['sentence_transformers'] = fake_st

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from backend.orchestrator.orchestrator import StoryWeaverOrchestrator
from backend.audio_renderer import render_wav_bytes
from backend.avatar_renderer import render_avatar_bytes
from flask import Response

# Initialize Flask app
app = Flask(__name__)

# Configure CORS explicitly for all routes
CORS(app, 
     origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost", "http://127.0.0.1"],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize orchestrator (global instance)
orchestrator = StoryWeaverOrchestrator()


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "service": "StoryWeaver AI Backend",
        }
    )


@app.route("/generate", methods=["POST"])
def generate_story():
    """
    Main endpoint to generate a complete story with all components.

    Request JSON:
    {
        "prompt": "Your story prompt here",
        "style": "adventure" (optional),
        "length": "medium" (optional),
        "num_characters": 3 (optional)
    }

    Returns:
        Complete story generation pipeline output
    """
    try:
        data = request.get_json()

        if not data or "prompt" not in data:
            return (
                jsonify({"error": "Missing required field: 'prompt'"}),
                400,
            )

        prompt = data.get("prompt", "")
        style = data.get("style", "adventure")
        length = data.get("length", "medium")
        num_characters = data.get("num_characters", 3)

        logger.info(f"Generating story for prompt: {prompt[:50]}...")

        # Generate story
        result = orchestrator.generate_story(
            prompt=prompt,
            style=style,
            length=length,
            num_characters=num_characters,
        )

        logger.info(f"Story generation completed: {result.get('status')}")

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "error": str(e),
                }
            ),
            500,
        )


@app.route("/feedback", methods=["POST"])
def provide_feedback():
    """
    Endpoint to provide feedback on a generated story.

    Request JSON:
    {
        "session_id": "session_uuid",
        "overall_score": 0.8,
        "dimension_feedback": {
            "coherence": 0.9,
            "creativity": 0.7,
            ...
        },
        "comments": "Optional feedback text"
    }

    Returns:
        Feedback processing confirmation
    """
    try:
        data = request.get_json()

        if not data or "session_id" not in data:
            return (
                jsonify({"error": "Missing required field: 'session_id'"}),
                400,
            )

        session_id = data.get("session_id")
        overall_score = data.get("overall_score", 0.5)
        dimension_feedback = data.get("dimension_feedback", {})
        comments = data.get("comments", "")

        logger.info(
            f"Received feedback for session: {session_id}, score: {overall_score}"
        )

        result = orchestrator.provide_feedback(
            session_id=session_id,
            overall_score=overall_score,
            dimension_feedback=dimension_feedback,
            comments=comments,
        )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "error": str(e),
                }
            ),
            500,
        )


@app.route("/metrics", methods=["GET"])
def get_metrics():
    """
    Get performance metrics for all agents.

    Returns:
        Dictionary with metrics for each agent
    """
    try:
        metrics = orchestrator.get_agent_metrics()
        memory_status = orchestrator.get_memory_status()

        return (
            jsonify(
                {
                    "agents": metrics,
                    "memory": memory_status,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "error": str(e),
                }
            ),
            500,
        )


@app.route("/memory", methods=["GET"])
def get_memory_status():
    """
    Get current memory module status.

    Returns:
        Memory summary and learning statistics
    """
    try:
        status = orchestrator.get_memory_status()
        return jsonify(status), 200

    except Exception as e:
        logger.error(f"Error retrieving memory status: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "error": str(e),
                }
            ),
            500,
        )


@app.route("/reset", methods=["POST"])
def reset_orchestrator():
    """
    Reset the orchestrator state (clear all memories and logs).

    Returns:
        Confirmation of reset
    """
    try:
        orchestrator.reset()
        logger.info("Orchestrator reset")

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Orchestrator reset successfully",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error resetting orchestrator: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "error": str(e),
                }
            ),
            500,
        )


@app.route("/render_audio", methods=["POST"])
def render_audio():
    """Synthesize a WAV file for a track and return it as audio/wav.

    Expected JSON:
    { "title": "...", "tempo": 120, "key": "C", "duration_seconds": 60, "genre": "ambient" }
    """
    try:
        data = request.get_json() or {}
        duration = int(data.get("duration_seconds", 60))
        # Safety limit
        if duration <= 0 or duration > 600:
            return jsonify({"error": "duration_seconds must be between 1 and 600"}), 400

        wav_bytes = render_wav_bytes(data, duration_seconds=duration)
        return Response(wav_bytes, mimetype="audio/wav")

    except Exception as e:
        logger.error(f"Error rendering audio: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/render_avatar", methods=["POST"])
def render_avatar():
    """Render a character avatar image (PNG). Accepts JSON payload with either:
        - 'description' (string) or 'prompt'
        - or 'character' (dict) with name, role, traits, archetype
        Optional 'width' and 'height'
    Returns image/png bytes.
    """
    try:
        data = request.get_json() or {}
        img_bytes = render_avatar_bytes(data)
        return Response(img_bytes, mimetype="image/png")
    except Exception as e:
        logger.error(f"Error rendering avatar: {str(e)}")
        return (
            jsonify({
                "status": "error",
                "error": str(e),
            }),
            500,
        )


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return (
        jsonify(
            {
                "error": "Internal server error",
                "details": str(error),
            }
        ),
        500,
    )


if __name__ == "__main__":
    logger.info("Starting StoryWeaver AI Backend...")
    app.run(debug=True, host="0.0.0.0", port=5000)
