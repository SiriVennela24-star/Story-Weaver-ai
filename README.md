# StoryWeaver AI - Multi-Agent Storytelling Engine

A sophisticated Python-based storytelling application powered by multiple AI agents working in concert to generate complete stories with characters, scenes, music metadata, and quality assessment.

## 🎯 Overview

StoryWeaver AI implements a **multi-agent orchestration system** where specialized agents collaborate to create immersive narratives:

- **StoryDirectorAgent**: Generates overall narrative structure and story arcs
- **CharacterAgent**: Develops detailed character profiles and personality traits
- **SceneAgent**: Creates vivid scene descriptions and atmospheric settings
- **MusicAgent**: Generates music metadata and soundtrack recommendations
- **FeedbackAgent**: Analyzes quality and provides improvement recommendations
- **MemoryModule**: Central repository for embeddings and learning history

## 🏗️ Architecture

```
StoryWeaver-AI/
├── backend/
│   ├── agents/
│   │   ├── base_agent.py           # Abstract base class
│   │   ├── story_director_agent.py
│   │   ├── character_agent.py
│   │   ├── scene_agent.py
│   │   ├── music_agent.py
│   │   ├── feedback_agent.py
│   │   └── __init__.py
│   ├── memory/
│   │   ├── memory_module.py        # Embedding & learning storage
│   │   └── __init__.py
│   ├── orchestrator/
│   │   ├── orchestrator.py         # Main pipeline coordinator
│   │   └── __init__.py
│   ├── app.py                      # Flask API backend
│   └── __init__.py
├── frontend/
│   ├── app.py                      # Flask frontend server
│   ├── templates/
│   │   └── index.html              # Main UI page
│   └── static/
│       ├── style.css               # Styling
│       └── app.js                  # Frontend logic
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup Steps

1. **Clone/Create the project** (already done)

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - Windows (Command Prompt):
     ```cmd
     venv\Scripts\activate.bat
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 📦 Dependencies

### Core Libraries
- **Flask** (2.3.3): Web framework for API and frontend
- **Flask-CORS** (4.0.0): Cross-Origin Resource Sharing support
- **PyTorch** (2.0.1): Deep learning framework (LSTM stub)
- **Transformers** (4.31.0): HuggingFace transformers for NLP
- **Sentence-Transformers** (2.2.2): Semantic embeddings
- **Scikit-learn** (1.3.1): Machine learning utilities
- **NumPy** (1.24.3): Numerical computing
- **SciPy** (1.11.2): Scientific computing

## 🏃 Running the Application

### Option 1: Run Backend and Frontend Separately

**Terminal 1 - Backend API** (Port 5000):
```bash
cd backend
python app.py
```

**Terminal 2 - Frontend** (Port 3000):
```bash
cd frontend
python app.py
```

### Option 2: Using a Task Runner (VS Code)

The project includes VS Code task configurations. Press `Ctrl+Shift+B` to see available tasks.

## 🎨 API Endpoints

### 1. Generate Story
**POST** `/generate`

Generate a complete story with all components.

**Request:**
```json
{
    "prompt": "A young adventurer discovers a magical artifact",
    "style": "adventure",
    "length": "medium",
    "num_characters": 3
}
```

**Response:**
```json
{
    "status": "success",
    "session_id": "uuid",
    "story": { ... },
    "characters": [ ... ],
    "scenes": [ ... ],
    "music": [ ... ],
    "quality_assessment": { ... },
    "recommendations": [ ... ],
    "pipeline_log": [ ... ],
    "memory_summary": { ... },
    "learning_stats": { ... }
}
```

### 2. Provide Feedback
**POST** `/feedback`

Submit feedback to improve agent learning.

**Request:**
```json
{
    "session_id": "uuid",
    "overall_score": 0.85,
    "dimension_feedback": {
        "coherence": 0.9,
        "creativity": 0.8,
        "emotional_impact": 0.85,
        "character_development": 0.8,
        "pacing": 0.85,
        "originality": 0.8
    },
    "comments": "Great story with good pacing!"
}
```

### 3. Get Metrics
**GET** `/metrics`

Retrieve agent performance metrics.

**Response:**
```json
{
    "agents": {
        "StoryDirector": { ... },
        "Character": { ... },
        "Scene": { ... },
        "Music": { ... },
        "Feedback": { ... }
    },
    "memory": { ... }
}
```

### 4. Get Memory Status
**GET** `/memory`

Check memory module status and learning statistics.

**Response:**
```json
{
    "memory_summary": {
        "story_context": 5,
        "character_descriptions": 15,
        "scene_settings": 25,
        "music_metadata": 5,
        "feedback_history": 3
    },
    "learning_stats": { ... }
}
```

### 5. Reset Orchestrator
**POST** `/reset`

Clear all memories and logs.

**Response:**
```json
{
    "status": "success",
    "message": "Orchestrator reset successfully"
}
```

### 6. Health Check
**GET** `/health`

Verify API is running.

**Response:**
```json
{
    "status": "healthy",
    "service": "StoryWeaver AI Backend"
}
```

## 🧠 Agent Implementation

### Base Agent Class

All agents inherit from `Agent` and implement two core methods:

```python
class Agent(ABC):
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and generate output"""
        pass
    
    @abstractmethod
    def learn(self, feedback: Dict[str, Any]) -> None:
        """Learn from feedback to improve"""
        pass
```

### Agent Pipeline Sequence

1. **StoryDirector** → Generates narrative structure
2. **Character** → Develops character profiles
3. **Scene** → Creates scene descriptions
4. **Music** → Generates music metadata
5. **Feedback** → Assesses quality

## 💾 Memory Module

The `MemoryModule` provides:

- **Semantic Embeddings**: Uses sentence-transformers for semantic similarity
- **Memory Categories**:
  - `story_context`: Initial prompts and story outlines
  - `character_descriptions`: Character profiles
  - `scene_settings`: Scene descriptions
  - `music_metadata`: Music track information
  - `feedback_history`: User feedback and ratings

- **Learning Patterns**: Tracks metrics like:
  - `story_coherence`
  - `character_consistency`
  - `scene_vividness`
  - `music_relevance`
  - `user_satisfaction`

## 🎯 Quality Assessment Dimensions

The Feedback Agent evaluates stories on:

1. **Coherence**: Narrative consistency
2. **Creativity**: Creative uniqueness
3. **Emotional Impact**: Emotional resonance
4. **Character Development**: Character depth
5. **Pacing**: Narrative rhythm
6. **Originality**: Novel elements

## 🖥️ Web UI Features

The frontend provides:

- **Story Generation Form**:
  - Prompt input
  - Style selection (Adventure, Mystery, Fantasy, Sci-Fi, Romance, Thriller)
  - Length selection (Short, Medium, Long)
  - Character count selection

- **Pipeline Visualization**:
  - Real-time progress tracking
  - Agent stage indicators

- **Results Display**:
  - Story outline and acts
  - Character cards with traits
  - Scene timeline with descriptions
  - Music track cards
  - Quality assessment with scores
  - Improvement recommendations

- **Feedback System**:
  - 5-star rating
  - Comment submission
  - Learning integration

- **System Visibility**:
  - Pipeline execution logs
  - Memory status
  - Learning statistics

## 📊 Example Workflow

### 1. User Input
User enters: "A young explorer discovers a hidden city in the jungle"

### 2. Pipeline Execution

```
User Prompt
    ↓
[StoryDirector] → Story outline, acts, themes
    ↓
[Character] → 3 detailed characters with traits
    ↓
[Scene] → 5 vivid scene descriptions
    ↓
[Music] → 5 music tracks with metadata
    ↓
[Feedback] → Quality assessment (0.82/1.0)
    ↓
Complete Story Package + Logs
```

### 3. User Feedback
User rates story as 5 stars with comment about character depth

### 4. Agent Learning
Agents update their learning patterns for future improvements

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file:
```
FLASK_ENV=development
API_PORT=5000
FRONTEND_PORT=3000
```

### Model Configuration
Sentence-Transformer model can be changed in `memory_module.py`:
```python
self.model = SentenceTransformer("all-MiniLM-L6-v2")  # Default
# Alternative models:
# "all-mpnet-base-v2" - Better quality
# "paraphrase-MiniLM-L6-v2" - Better for paraphrasing
```

## 🧪 Testing

### Manual API Testing with cURL

**Generate Story:**
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A hero discovers a secret", "style": "adventure"}'
```

**Submit Feedback:**
```bash
curl -X POST http://localhost:5000/feedback \
  -H "Content-Type: application/json" \
  -d '{"session_id": "uuid", "overall_score": 0.85, "comments": "Great!"}'
```

**Check Metrics:**
```bash
curl http://localhost:5000/metrics
```

## 📈 Performance Metrics

Each agent tracks:
- `total_processes`: Number of processing calls
- `total_feedback`: Number of feedback submissions
- `average_quality`: Running average quality score

## 🚀 Future Enhancements

- [ ] GPT-3/4 integration for natural language generation
- [ ] Real PyTorch LSTM implementation for music generation
- [ ] Database backend for persistent memory
- [ ] Advanced sentiment analysis with transformers
- [ ] User authentication and session management
- [ ] Story versioning and comparison
- [ ] Export to multiple formats (PDF, EPUB, etc.)
- [ ] Collaborative storytelling features
- [ ] Advanced visualization of agent interactions

## 🐛 Troubleshooting

### Port Already in Use
If ports 5000 or 3000 are in use:
```bash
# Change in backend/app.py (port parameter in app.run())
# Change in frontend/app.py (port parameter in app.run())
```

### Module Import Errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt --upgrade
```

### CORS Issues
Already configured with Flask-CORS, but verify `allow_origin` in backend if needed.

### Memory Issues
For large stories, consider limiting embeddings:
```python
# In MemoryModule
max_embeddings = 1000
if len(self.embeddings[category]) > max_embeddings:
    # Implement pruning logic
```

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## 📞 Support

For issues, questions, or suggestions, please open an issue in the repository.

---

**Created with ❤️ by StoryWeaver AI Team**
