# StoryWeaver AI - Quick Reference Card

## 🚀 Getting Started (30 seconds)

```bash
# Navigate to project
cd c:\Users\penta\Downloads\StoryWeaver-AI

# Windows: Run startup script
start.bat

# Or PowerShell
.\start.ps1

# Access UI
# Frontend: http://localhost:3000
# Backend:  http://localhost:5000
```

---

## 📁 File Locations

| Component | Location | Port |
|-----------|----------|------|
| Backend API | `backend/app.py` | 5000 |
| Frontend UI | `frontend/app.py` | 3000 |
| Agents | `backend/agents/` | - |
| Memory | `backend/memory/` | - |
| Orchestrator | `backend/orchestrator/` | - |

---

## 🤖 5 Agent Classes

| Agent | Location | Job |
|-------|----------|-----|
| StoryDirector | `story_director_agent.py` | Generate story structure |
| Character | `character_agent.py` | Create character profiles |
| Scene | `scene_agent.py` | Build vivid scenes |
| Music | `music_agent.py` | Generate music metadata |
| Feedback | `feedback_agent.py` | Assess quality |

---

## 💾 Memory Module

**Location**: `backend/memory/memory_module.py`

**Features**:
- Semantic embeddings (sentence-transformers)
- 5 memory categories
- Similarity-based recall
- Learning statistics

**Methods**:
```python
memory.store_memory(category, content, metadata)
memory.recall_similar(category, query, top_k=3)
memory.record_feedback(agent_name, score, text)
memory.update_learning_pattern(pattern_type, value)
memory.get_learning_stats()
```

---

## 🔌 API Endpoints

### Generate Story
```
POST /generate
Content: {"prompt": "...", "style": "adventure", ...}
Returns: Complete story with all agents' output
```

### Provide Feedback
```
POST /feedback
Content: {"session_id": "...", "overall_score": 0.85, ...}
Returns: Success confirmation
```

### Get Metrics
```
GET /metrics
Returns: Agent performance metrics
```

### Get Memory
```
GET /memory
Returns: Memory summary and learning stats
```

### Health Check
```
GET /health
Returns: Service status
```

### Reset
```
POST /reset
Returns: Confirmation
```

---

## 🎨 Frontend Pages

| Page | URL | Purpose |
|------|-----|---------|
| Main UI | http://localhost:3000 | Create stories |
| API Docs | http://localhost:5000 | Check API (if available) |

---

## 📊 Quality Dimensions

The system evaluates stories on 6 dimensions:

1. **Coherence** (0-1) - Narrative consistency
2. **Creativity** (0-1) - Unique elements
3. **Emotional Impact** (0-1) - Emotional resonance
4. **Character Development** (0-1) - Character depth
5. **Pacing** (0-1) - Narrative rhythm
6. **Originality** (0-1) - Novel elements

**Overall Score** = Average of all dimensions

---

## 🧠 Agent Methods

Every agent has these core methods:

```python
# Process input and generate output
output = agent.process(input_data)

# Learn from feedback
agent.learn(feedback_data)

# Get performance metrics
metrics = agent.get_metrics()
```

---

## 📝 Story Generation Flow

```
1. User Prompt
        ↓
2. [StoryDirector] → Story outline
        ↓
3. [Character] → Characters
        ↓
4. [Scene] → Scenes
        ↓
5. [Music] → Soundtrack
        ↓
6. [Feedback] → Quality Score
        ↓
7. Results to UI
```

---

## 🔧 Troubleshooting

### Port Already in Use
Edit app.py and change port:
```python
app.run(port=5001)  # or 3001 for frontend
```

### Missing Dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

### Module Not Found
Run from project root:
```bash
cd c:\Users\penta\Downloads\StoryWeaver-AI
```

### Memory Issues
Close other applications or use lighter model in memory_module.py

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Full project documentation |
| `SETUP.md` | Installation & setup guide |
| `API_EXAMPLES.md` | API usage examples |
| `PROJECT_SUMMARY.md` | Project overview |
| `QUICK_REFERENCE.md` | This file |

---

## 🎯 Example Prompts

**Adventure:**
```
"A young explorer discovers an ancient temple"
```

**Mystery:**
```
"A detective uncovers clues in an abandoned mansion"
```

**Fantasy:**
```
"A mage discovers they are the chosen one"
```

**Sci-Fi:**
```
"Humans make first contact with aliens"
```

**Romance:**
```
"Two rivals meet at a gallery opening"
```

**Thriller:**
```
"A whistleblower uncovers a dangerous conspiracy"
```

---

## 📊 Pipeline Stages

| Stage | Agent | Output |
|-------|-------|--------|
| 1 | StoryDirector | Outline, acts, themes |
| 2 | Character | Character profiles |
| 3 | Scene | Scene descriptions |
| 4 | Music | Track metadata |
| 5 | Feedback | Quality assessment |

---

## 💡 Key Features

✅ Multi-agent orchestration
✅ Semantic memory with embeddings
✅ Quality assessment
✅ Learning from feedback
✅ Real-time UI updates
✅ Pipeline logging
✅ Metrics tracking
✅ CORS-enabled API

---

## 🚀 Performance Tips

1. **First run**: Models download (~1GB), takes longer
2. **Subsequent runs**: Much faster (cached models)
3. **Shorter prompts**: Generate faster
4. **Feedback**: Helps improve future generations
5. **Memory**: Use 4GB+ RAM for best performance

---

## 📱 Frontend Features

- Story generation form
- Pipeline progress visualization
- Character cards
- Scene timeline
- Music tracks display
- Quality scores (6 dimensions)
- Improvement recommendations
- 5-star feedback rating
- Execution logs
- Memory dashboard

---

## 🔐 Security

- ✅ CORS enabled
- ✅ Input validation
- ✅ Error handling
- ✅ Logging
- ✅ Session tracking
- ✅ No secrets in code

---

## 🎓 Learning System

**Agents learn by**:
1. Processing stories
2. Receiving user feedback
3. Updating quality metrics
4. Improving future generations

**Track learning via**:
- Agent metrics (average quality)
- Learning patterns statistics
- Memory summary
- Dimension scores

---

## 📞 Support

### Quick Help
- Check SETUP.md for installation issues
- Review API_EXAMPLES.md for API usage
- See README.md for full documentation
- Check PROJECT_SUMMARY.md for overview

### Testing
```bash
# Health check
curl http://localhost:5000/health

# Generate story
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A hero rises"}'

# Get metrics
curl http://localhost:5000/metrics
```

---

## 📦 Technologies

- **Backend**: Python, Flask, PyTorch
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI/ML**: Transformers, Sentence-Transformers
- **Utilities**: NumPy, SciPy, Scikit-learn

---

## ⚡ One-Click Start

**Windows Command Prompt:**
```
start.bat
```

**Windows PowerShell:**
```
.\start.ps1
```

**Python (Any OS):**
```
python run.py
```

---

## 📈 What's Next?

1. **Start the app**: Run startup script
2. **Open frontend**: http://localhost:3000
3. **Enter prompt**: Describe your story
4. **Generate**: Click "Generate Story"
5. **Review results**: See all agent outputs
6. **Provide feedback**: Rate and comment
7. **Monitor**: Check agent metrics

---

## 🎉 You're All Set!

Everything is ready to use. Just run the startup script and start creating stories!

**Happy Storytelling! ✨📚**

---

*For detailed information, see the documentation files in the project root.*
