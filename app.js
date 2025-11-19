// StoryWeaver AI Frontend - Main Application Logic

const API_BASE = 'http://localhost:5000';
let currentSessionId = null;

// DOM Elements
const storyForm = document.getElementById('storyForm');
const feedbackForm = document.getElementById('feedbackForm');
const loadingIndicator = document.getElementById('loadingIndicator');
const errorMessage = document.getElementById('errorMessage');
const resultsSection = document.getElementById('resultsSection');

// Event Listeners
storyForm.addEventListener('submit', handleGenerateStory);
feedbackForm.addEventListener('submit', handleSubmitFeedback);

/**
 * Handle story generation form submission
 */
async function handleGenerateStory(e) {
    e.preventDefault();
    console.log('[StoryWeaver] handleGenerateStory called');

    // Get form data
    const prompt = document.getElementById('prompt').value;
    const style = document.getElementById('style').value;
    const length = document.getElementById('length').value;
    const numCharacters = parseInt(document.getElementById('numCharacters').value);
    console.log('[StoryWeaver] Form data:', { prompt: prompt.substring(0, 50), style, length, numCharacters });

    // Validate input
    if (!prompt.trim()) {
        showError('Please enter a story prompt');
        console.log('[StoryWeaver] No prompt entered');
        return;
    }

    // Show loading
    hideError();
    showLoading();
    resultsSection.classList.add('hidden');
    console.log('[StoryWeaver] Loading indicator shown, calling /generate');

    try {
        // Call API
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt,
                style,
                length,
                num_characters: numCharacters,
            }),
        });
        console.log('[StoryWeaver] API response status:', response.status);

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        console.log('[StoryWeaver] API response data status:', data.status);

        if (data.status === 'success') {
            currentSessionId = data.session_id;
            console.log('[StoryWeaver] Story generated successfully, session_id:', currentSessionId);
            displayResults(data);
            resultsSection.classList.remove('hidden');
        } else {
            showError(data.error || 'Failed to generate story');
        }
    } catch (error) {
        console.error('[StoryWeaver] Caught error:', error);
        showError(`Error: ${error.message}`);
        console.error('Generation error:', error);
    } finally {
        hideLoading();
    }
}

/**
 * Handle feedback submission
 */
async function handleSubmitFeedback(e) {
    e.preventDefault();

    if (!currentSessionId) {
        showError('No active session to provide feedback for');
        return;
    }

    const score = parseInt(document.querySelector('input[name="feedbackScore"]:checked').value);
    const comments = document.getElementById('feedbackComments').value;

    try {
        const response = await fetch(`${API_BASE}/feedback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                overall_score: score / 5, // Convert 1-5 to 0-1
                dimension_feedback: {},
                comments,
            }),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();

        if (data.status === 'success') {
            // Reset form
            feedbackForm.reset();
            alert('Thank you! Your feedback has been recorded and will help improve future stories.');
        } else {
            showError('Failed to submit feedback');
        }
    } catch (error) {
        showError(`Error submitting feedback: ${error.message}`);
        console.error('Feedback error:', error);
    }
}

/**
 * Display all results
 */
function displayResults(data) {
    // Update pipeline progress
    updatePipelineProgress(data.pipeline_log);

    // Display story
    if (data.story) {
        displayStory(data.story);
    }

    // Display characters
    if (data.characters && data.characters.length > 0) {
        displayCharacters(data.characters);
    }

    // Display scenes
    if (data.scenes && data.scenes.length > 0) {
        displayScenes(data.scenes);
    }

    // Display music
    if (data.music && data.music.length > 0) {
        displayMusic(data.music);
    }

    // Display quality assessment
    if (data.quality_assessment) {
        displayQualityAssessment(data.quality_assessment, data.recommendations);
    }

    // Display memory status
    if (data.memory_summary) {
        displayMemoryStatus(data.memory_summary, data.learning_stats);
    }

    // Display pipeline log
    displayPipelineLog(data.pipeline_log);
}

/**
 * Update pipeline progress indicators
 */
function updatePipelineProgress(log) {
    const stages = document.querySelectorAll('.stage');

    stages.forEach(stage => {
        const stageName = stage.dataset.stage;
        const isCompleted = log.some(entry =>
            entry.event_type.includes(stageName) && !entry.event_type.includes('error')
        );

        if (isCompleted) {
            stage.classList.add('completed');
            stage.classList.remove('active');
        }
    });

    // Mark the last as active
    if (log.length > 0) {
        stages[stages.length - 1].classList.add('completed');
    }
}

/**
 * Display story information
 */
function displayStory(story) {
    document.getElementById('storyOutline').textContent = story.story_outline || 'No outline available';

    // Display acts
    const actsDiv = document.getElementById('storyActs');
    actsDiv.innerHTML = '';

    if (story.acts && story.acts.length > 0) {
        const actsList = document.createElement('ul');
        story.acts.forEach(act => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${act.title}</strong>: ${act.description}`;
            actsList.appendChild(li);
        });
        actsDiv.appendChild(actsList);
    }

    // Display themes
    const themesDiv = document.createElement('div');
    themesDiv.style.marginTop = '15px';
    themesDiv.innerHTML = '<strong>Themes:</strong> ' + (story.themes?.join(', ') || 'N/A');
    actsDiv.appendChild(themesDiv);
}

/**
 * Generate a stylized full-body human avatar on canvas.
 * Draws head, eyes, nose, mouth, hair, torso, arms, hands and legs using deterministic seeds.
 */
function generateCharacterAvatar(canvas, character) {
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;

    // Deterministic RNG from character name
    const seed = _hashToSeed(character.name || '');
    const rnd = _seededRandom(seed);

    // Basic palettes
    const skinTones = ['#f5d6c6', '#e0b899', '#c78e62', '#a66b44', '#6b3f2a'];
    const hairColors = ['#2b1b0a', '#6b2b1a', '#1f2937', '#b7791f', '#d4a373', '#ffffff'];
    const clothColors = ['#3b82f6', '#ef4444', '#10b981', '#8b5cf6', '#f59e0b', '#06b6d4'];

    const skin = skinTones[seed % skinTones.length];
    const hair = hairColors[(seed >> 8) % hairColors.length];
    const cloth = clothColors[(seed >> 16) % clothColors.length];

    // Background
    ctx.fillStyle = getColorForArchetype(character.archetype);
    ctx.fillRect(0, 0, w, h);

    // Scaling factors for full body in 140x140 canvas
    const centerX = w / 2;
    const headY = h * 0.28;
    const headR = Math.floor(h * 0.14);

    // Draw torso
    const torsoTop = headY + headR + 6;
    const torsoBottom = h - 28;
    const torsoWidth = 56;
    ctx.fillStyle = cloth;
    roundRect(ctx, centerX - torsoWidth/2, torsoTop, torsoWidth, torsoBottom - torsoTop, 8);
    ctx.fill();

    // Draw arms (simple rounded rectangles)
    ctx.fillStyle = cloth;
    roundRect(ctx, centerX - torsoWidth/2 - 18, torsoTop + 6, 16, torsoBottom - torsoTop - 20, 8);
    roundRect(ctx, centerX + torsoWidth/2 + 2, torsoTop + 6, 16, torsoBottom - torsoTop - 20, 8);
    ctx.fill();

    // Draw legs
    ctx.fillStyle = '#111827';
    const legW = 16;
    const legTop = torsoBottom;
    const legH = h - legTop - 8;
    roundRect(ctx, centerX - 18, legTop, legW, legH, 6);
    roundRect(ctx, centerX + 2, legTop, legW, legH, 6);
    ctx.fill();

    // Draw head
    ctx.beginPath();
    ctx.fillStyle = skin;
    ctx.arc(centerX, headY, headR, 0, Math.PI * 2);
    ctx.fill();
    ctx.closePath();

    // Hair shape (varies by gender/seed)
    const gender = determineCharacterGender(character);
    drawHair(ctx, centerX, headY, headR, hair, gender, rnd);

    // Eyes
    const eyeY = headY - Math.floor(headR * 0.1);
    const eyeOffsetX = Math.floor(headR * 0.45);
    const eyeW = Math.max(2, Math.floor(headR * 0.18));
    ctx.fillStyle = '#111';
    roundRect(ctx, centerX - eyeOffsetX - eyeW/2, eyeY, eyeW, eyeW, 6);
    roundRect(ctx, centerX + eyeOffsetX - eyeW/2, eyeY, eyeW, eyeW, 6);
    ctx.fill();

    // Nose (simple triangle)
    ctx.fillStyle = '#b08976';
    ctx.beginPath();
    ctx.moveTo(centerX, headY - 2);
    ctx.lineTo(centerX - 4, headY + 8);
    ctx.lineTo(centerX + 4, headY + 8);
    ctx.closePath();
    ctx.fill();

    // Mouth
    ctx.strokeStyle = '#7f5539';
    ctx.lineWidth = 2;
    ctx.beginPath();
    const smile = (seed % 3) !== 0;
    if (smile) ctx.arc(centerX, headY + 14, 8, 0, Math.PI);
    else ctx.arc(centerX, headY + 18, 8, Math.PI, 0);
    ctx.stroke();

    // Hands (small circles at arm ends)
    ctx.fillStyle = skin;
    ctx.beginPath(); ctx.arc(centerX - torsoWidth/2 - 10, torsoTop + (torsoBottom - torsoTop)/2, 8, 0, Math.PI*2); ctx.fill();
    ctx.beginPath(); ctx.arc(centerX + torsoWidth/2 + 18, torsoTop + (torsoBottom - torsoTop)/2, 8, 0, Math.PI*2); ctx.fill();

    // Simple accessory: hat or scarf based on traits
    if ((character.traits || []).some(t => t.toLowerCase().includes('mystic') || t.toLowerCase().includes('wizard'))) {
        // Draw a small hat
        ctx.fillStyle = '#3b3b3b';
        ctx.beginPath();
        ctx.ellipse(centerX, headY - headR * 0.6, headR * 0.9, headR * 0.5, 0, Math.PI, 2*Math.PI);
        ctx.fill();
    }

    // Name label
    ctx.fillStyle = '#0f172a';
    ctx.font = 'bold 10px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText((character.name || '').split(' ')[0], centerX, h - 4);
}

/**
 * Render an anime-style character on canvas
 */
function renderAnimeCharacter(canvas, character) {
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;
    
    // Soft gradient background
    const g = ctx.createLinearGradient(0, 0, 0, h);
    g.addColorStop(0, '#e9d5ff');
    g.addColorStop(1, '#f3e8ff');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);
    
    // Determine character gender/style
    const gender = determineCharacterGender(character);
    const seed = _hashToSeed(character.name || '');
    const rnd = _seededRandom(seed);
    
    // Head
    const cx = w / 2;
    const headY = h * 0.25;
    const headR = 28;
    ctx.fillStyle = '#f5d6c6';
    ctx.beginPath();
    ctx.ellipse(cx, headY, headR, headR * 1.15, 0, 0, Math.PI*2);
    ctx.fill();
    
    // Hair - anime style
    const hairColor = ['#2b1b0a', '#6b2b1a', '#b7791f'][Math.floor(rnd()*3)];
    ctx.fillStyle = hairColor;
    if (gender === 'male') {
        // Short spiky hair
        for (let i = 0; i < 5; i++) {
            ctx.beginPath();
            ctx.moveTo(cx - 20 + i*10, headY - 28);
            ctx.lineTo(cx - 18 + i*10, headY - 38);
            ctx.lineTo(cx - 15 + i*10, headY - 28);
            ctx.fill();
        }
    } else {
        // Long flowing hair
        ctx.beginPath();
        ctx.ellipse(cx, headY + 8, 32, 20, 0, Math.PI, 2*Math.PI);
        ctx.fill();
    }
    
    // Eyes - big anime eyes
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.ellipse(cx - 10, headY - 6, 7, 12, 0, 0, Math.PI*2);
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(cx + 10, headY - 6, 7, 12, 0, 0, Math.PI*2);
    ctx.fill();
    
    // Pupils
    ctx.fillStyle = '#333';
    ctx.beginPath();
    ctx.arc(cx - 10, headY - 2, 4, 0, Math.PI*2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(cx + 10, headY - 2, 4, 0, Math.PI*2);
    ctx.fill();
    
    // Sparkle in eyes
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.arc(cx - 8, headY - 4, 2, 0, Math.PI*2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(cx + 12, headY - 4, 2, 0, Math.PI*2);
    ctx.fill();
    
    // Mouth - simple smile
    ctx.strokeStyle = '#d4a373';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(cx, headY + 8, 6, 0, Math.PI);
    ctx.stroke();
    
    // Body - simple tunic/dress
    const bodyColor = ['#3b82f6', '#ef4444', '#10b981'][Math.floor(rnd()*3)];
    ctx.fillStyle = bodyColor;
    ctx.fillRect(cx - 18, headY + 28, 36, 50);
    
    // Arms
    ctx.fillStyle = '#f5d6c6';
    ctx.fillRect(cx - 24, headY + 32, 12, 40);
    ctx.fillRect(cx + 12, headY + 32, 12, 40);
    
    // Legs
    ctx.fillStyle = '#2d3748';
    ctx.fillRect(cx - 12, headY + 78, 10, 30);
    ctx.fillRect(cx + 2, headY + 78, 10, 30);
    
    // Name
    ctx.fillStyle = '#0f172a';
    ctx.font = 'bold 10px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText((character.name || '').split(' ')[0], cx, h - 6);
}

/**
 * Render a design-style (geometric) character on canvas
 */
function renderDesignCharacter(canvas, character) {
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;
    
    // Minimalist gradient background
    const g = ctx.createLinearGradient(0, 0, w, h);
    g.addColorStop(0, '#bfdbfe');
    g.addColorStop(1, '#dbeafe');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);
    
    const seed = _hashToSeed(character.name || '');
    const rnd = _seededRandom(seed);
    const gender = determineCharacterGender(character);
    
    // Geometric head (circle)
    const cx = w / 2;
    const headY = h * 0.28;
    ctx.fillStyle = '#0ea5a4';
    ctx.beginPath();
    ctx.arc(cx, headY, 24, 0, Math.PI*2);
    ctx.fill();
    
    // Geometric body (rectangle with rounded corners)
    const bodyColor = ['#6366f1', '#8b5cf6', '#ec4899'][Math.floor(rnd()*3)];
    ctx.fillStyle = bodyColor;
    roundRect(ctx, cx - 16, headY + 24, 32, 56, 8);
    ctx.fill();
    
    // Minimalist arms (lines or thin rects)
    ctx.fillStyle = '#1e293b';
    ctx.fillRect(cx - 22, headY + 28, 6, 44);
    ctx.fillRect(cx + 16, headY + 28, 6, 44);
    
    // Geometric legs
    ctx.fillStyle = '#475569';
    ctx.fillRect(cx - 10, headY + 80, 8, 28);
    ctx.fillRect(cx + 2, headY + 80, 8, 28);
    
    // Accent circles
    ctx.fillStyle = 'rgba(255,255,255,0.3)';
    ctx.beginPath();
    ctx.arc(cx - 8, headY - 4, 3, 0, Math.PI*2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(cx + 8, headY - 4, 3, 0, Math.PI*2);
    ctx.fill();
    
    // Name
    ctx.fillStyle = '#0f172a';
    ctx.font = 'bold 10px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText((character.name || '').split(' ')[0], cx, h - 6);
}

// Helper: rounded rectangle path
function roundRect(ctx, x, y, w, h, r) {
    const minr = Math.min(r, w/2, h/2);
    ctx.beginPath();
    ctx.moveTo(x + minr, y);
    ctx.arcTo(x + w, y, x + w, y + h, minr);
    ctx.arcTo(x + w, y + h, x, y + h, minr);
    ctx.arcTo(x, y + h, x, y, minr);
    ctx.arcTo(x, y, x + w, y, minr);
    ctx.closePath();
}

// Helper: draw hair (various styles)
function drawHair(ctx, cx, cy, r, color, gender, rnd) {
    ctx.fillStyle = color;
    const style = Math.floor(rnd() * 4);
    if (style === 0) {
        // Short hair
        ctx.beginPath();
        ctx.ellipse(cx, cy - r*0.25, r*1.05, r*0.6, 0, Math.PI, 2*Math.PI);
        ctx.fill();
    } else if (style === 1) {
        // Long hair sides
        ctx.beginPath();
        ctx.ellipse(cx - r*0.6, cy, r*0.45, r*0.9, 0, Math.PI*1.1, Math.PI*2.1);
        ctx.ellipse(cx + r*0.6, cy, r*0.45, r*0.9, 0, Math.PI*-0.1, Math.PI*1.5);
        ctx.fill();
    } else if (style === 2) {
        // Top swoop
        ctx.beginPath();
        ctx.moveTo(cx - r, cy - r*0.2);
        ctx.quadraticCurveTo(cx, cy - r*1.05, cx + r, cy - r*0.2);
        ctx.lineTo(cx + r, cy - r*0.05);
        ctx.quadraticCurveTo(cx, cy - r*0.8, cx - r, cy - r*0.05);
        ctx.fill();
    } else {
        // Hat-like cap
        ctx.beginPath();
        ctx.ellipse(cx, cy - r*0.6, r*1.1, r*0.5, 0, Math.PI, 2*Math.PI);
        ctx.fill();
    }
}

/**
 * Determine character gender (male/female) based on name and traits
 */
function determineCharacterGender(character) {
    const traits = (character.traits || []).map(t => t.toLowerCase());
    const name = (character.name || '').toLowerCase();
    
    // Check for explicit gender traits
    if (traits.some(t => t.includes('masculine') || t.includes('strong') || t.includes('warrior'))) {
        return 'male';
    }
    if (traits.some(t => t.includes('feminine') || t.includes('grace') || t.includes('enchantress'))) {
        return 'female';
    }
    
    // Common name patterns (simplified heuristic)
    const maleEndings = ['us', 'on', 'or', 'er'];
    const femaleEndings = ['a', 'e', 'ia', 'y'];
    
    for (let ending of maleEndings) {
        if (name.endsWith(ending)) return 'male';
    }
    for (let ending of femaleEndings) {
        if (name.endsWith(ending)) return 'female';
    }
    
    // Default: random based on name hash (deterministic but varied)
    const seed = _hashToSeed(character.name);
    return seed % 2 === 0 ? 'male' : 'female';
}

/**
 * Get background color for archetype
 */
function getColorForArchetype(archetype) {
    const colors = {
        hero: '#fef3c7',
        mentor: '#ddd6fe',
        shadow: '#fca5a5',
        lover: '#fbcfe8',
        creator: '#a3e635',
        innocent: '#bfdbfe',
        sage: '#f3e8ff',
    };
    return colors[(archetype || 'innocent').toLowerCase()] || '#f0f4f8';
}

/**
 * Display characters
 */
function displayCharacters(characters) {
    const panel = document.getElementById('charactersPanel');
    panel.innerHTML = '';

    if (characters.length === 0) {
        panel.innerHTML = '<p>No characters available</p>';
        return;
    }

    const grid = document.createElement('div');
    grid.className = 'characters-grid';

    characters.forEach(char => {
        const card = document.createElement('div');
        card.className = 'character-card';
        card.style.display = 'flex';
        card.style.gap = '16px';
        
        // Character info (left side)
        const infoDiv = document.createElement('div');
        infoDiv.style.flex = '1';
        infoDiv.innerHTML = `
            <div class="character-name">${char.name}</div>
            <div class="character-role">${char.role.toUpperCase()}</div>
            <div class="character-traits">
                ${char.traits?.map(t => `<span class="character-trait">${t}</span>`).join('') || ''}
            </div>
            <div style="font-size: 0.9rem; color: #718096; margin-bottom: 8px;">
                <strong>Archetype:</strong> ${char.archetype}
            </div>
            <div style="font-size: 0.9rem; color: #718096; margin-bottom: 8px;">
                <strong>Arc:</strong> ${char.arc}
            </div>
            <div style="font-size: 0.9rem; color: #4a5568;">
                ${char.description}
            </div>
        `;
        
        // Character avatar (right side) - wrapper for portrait + controls
        const avatarWrapper = document.createElement('div');
        avatarWrapper.style.flexShrink = '0';
        avatarWrapper.style.display = 'flex';
        avatarWrapper.style.flexDirection = 'column';
        avatarWrapper.style.gap = '8px';
        
        // Avatar portrait canvas/image container
        const avatarDiv = document.createElement('div');
        avatarDiv.style.width = '140px';
        avatarDiv.style.height = '180px';
        avatarDiv.style.display = 'flex';
        avatarDiv.style.alignItems = 'center';
        avatarDiv.style.justifyContent = 'center';
        avatarDiv.style.background = getColorForArchetype(char.archetype);
        avatarDiv.style.borderRadius = '8px';
        avatarDiv.style.border = '1px solid #e2e8f0';
        avatarDiv.style.overflow = 'hidden';
        
        // Avatar controls (style selector, regenerate, download)
        const controlsDiv = document.createElement('div');
        controlsDiv.style.display = 'flex';
        controlsDiv.style.gap = '6px';
        controlsDiv.style.flexWrap = 'wrap';

        const styleSelect = document.createElement('select');
        ['cartoon','design','anime','photorealistic'].forEach(opt => {
            const o = document.createElement('option'); o.value = opt; o.textContent = opt.charAt(0).toUpperCase()+opt.slice(1); styleSelect.appendChild(o);
        });
        styleSelect.value = 'cartoon';

        const btnRegenerate = document.createElement('button');
        btnRegenerate.textContent = 'Regen';
        btnRegenerate.className = 'btn-regenerate';
        btnRegenerate.style.fontSize = '0.75rem';
        btnRegenerate.style.padding = '3px 6px';

        const btnDownload = document.createElement('button');
        btnDownload.textContent = 'Down';
        btnDownload.className = 'btn-download';
        btnDownload.style.fontSize = '0.75rem';
        btnDownload.style.padding = '3px 6px';

        controlsDiv.appendChild(styleSelect);
        controlsDiv.appendChild(btnRegenerate);
        controlsDiv.appendChild(btnDownload);

        // Store style on avatar div
        avatarDiv._char_style = styleSelect.value;
        styleSelect.addEventListener('change', (ev) => {
            avatarDiv._char_style = styleSelect.value;
        });

        avatarWrapper.appendChild(avatarDiv);
        avatarWrapper.appendChild(controlsDiv);

        // Helper to render cartoon character on canvas
        function renderCharacterPreview() {
            const style = avatarDiv._char_style || 'cartoon';
            avatarDiv.innerHTML = '';
            
            if (style === 'cartoon') {
                const canvas = document.createElement('canvas');
                canvas.width = 140;
                canvas.height = 180;
                canvas.style.borderRadius = '8px';
                canvas.style.width = '100%';
                canvas.style.height = '100%';
                avatarDiv.appendChild(canvas);
                generateCharacterAvatar(canvas, char);
            } else if (style === 'anime') {
                const canvas = document.createElement('canvas');
                canvas.width = 140;
                canvas.height = 180;
                canvas.style.borderRadius = '8px';
                canvas.style.width = '100%';
                canvas.style.height = '100%';
                avatarDiv.appendChild(canvas);
                renderAnimeCharacter(canvas, char);
            } else if (style === 'design') {
                const canvas = document.createElement('canvas');
                canvas.width = 140;
                canvas.height = 180;
                canvas.style.borderRadius = '8px';
                canvas.style.width = '100%';
                canvas.style.height = '100%';
                avatarDiv.appendChild(canvas);
                renderDesignCharacter(canvas, char);
            } else {
                // photorealistic - fetch from backend
                const img = document.createElement('img');
                img.width = 140;
                img.height = 180;
                img.style.borderRadius = '8px';
                img.style.objectFit = 'cover';
                img.alt = `Avatar of ${char.name}`;
                avatarDiv.appendChild(img);
                
                (async () => {
                    try {
                        const resp = await fetch(`${API_BASE}/render_avatar`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ character: char, width: 420, height: 560, mode: 'photorealistic' })
                        });
                        if (!resp.ok) throw new Error('Avatar generation failed');
                        const blob = await resp.blob();
                        const url = URL.createObjectURL(blob);
                        img.src = url;
                        img.onload = () => { avatarDiv.style.background = 'transparent'; };
                    } catch (e) {
                        console.warn('Photorealistic avatar failed, falling back to cartoon', e);
                        avatarDiv._char_style = 'cartoon';
                        renderCharacterPreview();
                    }
                })();
            }
        }

        // Initial render
        renderCharacterPreview();

        // Re-render when style changes
        styleSelect.addEventListener('change', () => {
            avatarDiv._char_style = styleSelect.value;
            renderCharacterPreview();
        });

        // Regenerate button behavior
        btnRegenerate.addEventListener('click', (ev) => {
            renderCharacterPreview();
        });

        // Download button behavior
        btnDownload.addEventListener('click', (ev) => {
            const curImg = avatarDiv.querySelector('img');
            if (curImg && curImg._blob) {
                const a = document.createElement('a');
                const url = URL.createObjectURL(curImg._blob);
                a.href = url; a.download = `${char.name.replace(/\s+/g,'_')}_avatar.png`;
                document.body.appendChild(a); a.click(); a.remove();
                URL.revokeObjectURL(url);
                return;
            }
            const canvas = avatarDiv.querySelector('canvas');
            if (canvas) {
                const url = canvas.toDataURL('image/png');
                const a = document.createElement('a'); a.href = url; a.download = `${char.name.replace(/\s+/g,'_')}_avatar.png`;
                document.body.appendChild(a); a.click(); a.remove();
                return;
            }
            alert('No avatar available to download');
        });
        
        card.appendChild(infoDiv);
        card.appendChild(avatarWrapper);
        grid.appendChild(card);
    });

    panel.appendChild(grid);
}

// --- Simple WebAudio synthesizer for demo playback ---
let _sw_audio_ctx = null;
let _sw_playing = null; // { sourceNodes: [], stopTime: number }

function _ensureAudioContext() {
    if (!_sw_audio_ctx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        _sw_audio_ctx = new AudioContext();
    }
    return _sw_audio_ctx;
}

function _hashToSeed(str) {
    let h = 2166136261 >>> 0;
    for (let i = 0; i < str.length; i++) {
        h = Math.imul(h ^ str.charCodeAt(i), 16777619);
    }
    return (h >>> 0) & 0xffffffff;
}

function _seededRandom(seed) {
    // returns function that gives 0..1
    return function() {
        seed = (seed + 0x6D2B79F5) | 0;
        let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967295;
    };
}

function _buildScaleFrequencies(key) {
    // Map a simple set of keys to base frequency (A4 = 440)
    const noteToSemitone = { C: -9, D: -7, E: -5, F: -4, G: -2, A: 0, B: 2 };
    const base = noteToSemitone[(key || 'C').toUpperCase().charAt(0)] || 0;
    const a4 = 440;
    const freqs = [];
    // major scale intervals
    const intervals = [0, 2, 4, 5, 7, 9, 11, 12];
    intervals.forEach(i => {
        const semitone = base + i;
        freqs.push(a4 * Math.pow(2, semitone / 12));
    });
    return freqs;
}

function stopCurrentPlayback() {
    // Cleanup audio element playback or synth nodes
    if (!_sw_playing) return;
    if (_sw_playing.audioElement) {
        try { _sw_playing.audioElement.pause(); } catch (e) {}
        try { URL.revokeObjectURL(_sw_playing.blobUrl); } catch (e) {}
    }
    if (_sw_playing.sourceNodes) {
        _sw_playing.sourceNodes.forEach(n => {
            try { n.stop(); } catch (e) {}
            try { n.disconnect(); } catch (e) {}
        });
    }
    teardownPlaybackUI();
    // stop any active scene visualizer
    try { stopSceneVisualizer(); } catch (e) {}
    _sw_playing = null;
}

// Scene visualizer state
let _current_scene_visualizer = null;

function startSceneVisualizer(card) {
    // stop previous
    stopSceneVisualizer();
    if (!card) return;
    const visual = card.querySelector('.scene-visual');
    if (!visual) return;
    // remove placeholder
    visual.innerHTML = '';
    // create canvas
    const canvas = document.createElement('canvas');
    canvas.width = visual.clientWidth || 220;
    canvas.height = visual.clientHeight || 140;
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    visual.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    // Map scene properties to visual parameters
    const scene = card._scene || {};
    const tone = (scene.emotional_tone || '').toLowerCase();
    const pacing = (scene.pacing || '').toLowerCase();
    const atmosphere = scene.atmosphere || {};

    // color palettes by tone
    const palettes = {
        happy: ['#fef08a', '#fb923c'],
        sad: ['#bfdbfe', '#1e40af'],
        tense: ['#fecaca', '#b91c1c'],
        mysterious: ['#e9d5ff', '#6d28d9'],
        neutral: ['#bae6fd', '#0ea5a4']
    };
    let colors = palettes.neutral;
    if (tone.includes('happy') || tone.includes('joy') || tone.includes('warm')) colors = palettes.happy;
    else if (tone.includes('sad') || tone.includes('melanch')) colors = palettes.sad;
    else if (tone.includes('tense') || tone.includes('threat') || tone.includes('danger')) colors = palettes.tense;
    else if (tone.includes('myster') || tone.includes('mystic') || tone.includes('mystical')) colors = palettes.mysterious;

    // pacing -> speed multiplier
    let speedMult = 1.0;
    if (pacing.includes('slow')) speedMult = 0.6;
    else if (pacing.includes('fast') || pacing.includes('rapid')) speedMult = 1.6;

    // atmosphere softness reduces amplitude
    let amplitudeMult = 1.0;
    const atmVals = Object.values(atmosphere).join(' ').toLowerCase();
    if (atmVals.includes('soft') || atmVals.includes('soft lighting') || atmVals.includes('soft_lighting')) amplitudeMult = 0.6;
    if (atmVals.includes('intense') || atmVals.includes('harsh')) amplitudeMult = 1.4;

    // number of bars influenced by tone
    let bars = 12;
    if (tone.includes('tense')) bars = 16;
    else if (tone.includes('sad')) bars = 8;
    else if (tone.includes('happy')) bars = 14;

    let raf = null;
    let start = performance.now();

    // determine selected style (cartoon/design/anime)
    const style = (card._scene_style || 'cartoon').toLowerCase();

    // Get analyser if available (for audio-driven visuals)
    const analyser = card._analyser;
    let dataArray = null;
    if (analyser) {
        dataArray = new Uint8Array(analyser.frequencyBinCount);
    }

    // Get audio amplitude for envelope-responsive visuals
    function getAudioAmplitude() {
        if (!analyser || !dataArray) return 0.5; // default mid-range
        try {
            analyser.getByteFrequencyData(dataArray);
            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) sum += dataArray[i];
            return Math.min(1.0, (sum / dataArray.length) / 255);
        } catch (e) { return 0.5; }
    }

    function drawCartoon(now) {
        const t = (now - start) / 1000 * speedMult;
        const w = canvas.width; const h = canvas.height;
        const audioAmp = getAudioAmplitude();
        
        // flat layered background: wall, floor
        ctx.fillStyle = colors[0];
        ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = colors[1];
        ctx.fillRect(0, h * 0.6, w, h * 0.4);

        // simple props influenced by scene description: a pillow, a plant, or lamp
        ctx.save();
        const seed = _hashToSeed(scene.title || scene.setting || '');
        const rnd = _seededRandom(seed);
        const objs = Math.max(1, Math.floor(1 + rnd()*2));
        for (let i=0;i<objs;i++) {
            const ow = 40 + Math.floor(rnd()*80);
            const oh = 20 + Math.floor(rnd()*50);
            const x = 20 + Math.floor(rnd() * (w - ow - 40));
            const y = h * 0.6 + 10 + Math.floor(rnd() * (h*0.35 - oh));
            ctx.fillStyle = `rgba(255,255,255,${0.08 + rnd()*0.18 + audioAmp*0.1})`;
            roundRect(ctx, x, y, ow, oh, 8);
            ctx.fill();
        }
        ctx.restore();

        // stylized character silhouettes (two people) - pulse with audio
        if ((scene.characters || []).length > 0 || /(man|woman|person|people|boy|girl)/i.test(scene.description || '')) {
            const cx = Math.floor(w*0.5);
            const cy = Math.floor(h*0.5 - 10);
            const pulse = 1.0 + audioAmp * 0.15; // audio drives slight size pulse
            // back person
            ctx.fillStyle = `rgba(15,23,42,${0.80 + audioAmp*0.15})`;
            roundRect(ctx, cx - 36*pulse, cy - 10, 24*pulse, 56*pulse, 12);
            ctx.fill();
            // front person
            ctx.fillStyle = `rgba(255,255,255,${0.90 + audioAmp*0.1})`;
            roundRect(ctx, cx + 6*pulse, cy - 6, 28*pulse, 64*pulse, 12);
            ctx.fill();
        }

        // subtle animated overlay for life
        ctx.fillStyle = `rgba(255,255,255,${0.02 + 0.02*Math.sin(t*2) + audioAmp*0.04})`;
        ctx.fillRect(0,0,w,h);

        raf = requestAnimationFrame(drawCartoon);
    }

    function drawDesign(now) {
        const t = (now - start) / 1000 * speedMult;
        const w = canvas.width; const h = canvas.height;
        const audioAmp = getAudioAmplitude();
        
        // geometric shapes and negative space
        ctx.clearRect(0,0,w,h);
        const g = ctx.createLinearGradient(0,0,w,h);
        g.addColorStop(0, lightenColor(colors[0], 0.08 + audioAmp*0.06));
        g.addColorStop(1, lightenColor(colors[1], -0.02 + audioAmp*0.04));
        ctx.fillStyle = g;
        ctx.fillRect(0,0,w,h);

        const count = 4;
        for (let i=0;i<count;i++){
            const s = 0.6 + 0.6 * Math.sin(t*0.8 + i) + audioAmp * 0.15;
            ctx.fillStyle = `rgba(255,255,255,${0.06 + 0.06*i + audioAmp*0.08})`;
            const rw = w * (0.3 + 0.15 * i) * s;
            const rh = h * (0.2 + 0.12 * i) * (1/s);
            const x = (w - rw) * (i/(count-1));
            const y = (h - rh) * (1 - i/(count));
            roundRect(ctx, x, y, rw, rh, 18);
            ctx.fill();
        }

        ctx.fillStyle = `rgba(0,0,0,${0.06 + audioAmp*0.08})`;
        roundRect(ctx, w*0.1, h*0.55, w*0.8, h*0.28, 12);
        ctx.fill();

        raf = requestAnimationFrame(drawDesign);
    }

    function drawAnime(now) {
        const t = (now - start) / 1000 * speedMult;
        const w = canvas.width; const h = canvas.height;
        const audioAmp = getAudioAmplitude();
        
        // deep vignette + soft gradient
        const g = ctx.createLinearGradient(0,0,w,h);
        g.addColorStop(0, shadeColor(colors[0], Math.floor(-8 + audioAmp*6)));
        g.addColorStop(1, shadeColor(colors[1], Math.floor(6 - audioAmp*4)));
        ctx.fillStyle = g;
        ctx.fillRect(0,0,w,h);

        // light rays - intensity driven by audio
        ctx.save(); ctx.globalAlpha = 0.08 + 0.06*Math.abs(Math.sin(t)) + audioAmp*0.1;
        ctx.fillStyle = '#fff';
        for (let i=0;i<6;i++){
            const px = w * (i/6 + 0.05*Math.sin(t + i) + audioAmp*0.05);
            ctx.fillRect(px, 0, 4, h);
        }
        ctx.restore();

        // anime-style character face silhouette - reacts to audio
        const cx = Math.floor(w*0.45);
        const cy = Math.floor(h*0.45);
        const facePulse = 1.0 + audioAmp * 0.12;
        ctx.fillStyle = `rgba(255,255,255,${0.90 + audioAmp*0.1})`;
        ctx.beginPath(); ctx.ellipse(cx, cy, 32*facePulse, 44*facePulse, 0, 0, Math.PI*2); ctx.fill(); ctx.closePath();
        ctx.fillStyle = shadeColor(colors[1], Math.floor(-12 + audioAmp*8));
        ctx.beginPath(); ctx.ellipse(cx, cy-22, 36*facePulse, 22*facePulse, 0, Math.PI, 2*Math.PI); ctx.fill(); ctx.closePath();

        // eyes - twinkle affected by audio
        const eyeOpacity = 0.8 + audioAmp*0.2;
        ctx.fillStyle = `rgba(17,17,17,${eyeOpacity})`; ctx.fillRect(cx-12, cy-6, 6, 6); ctx.fillRect(cx+6, cy-6, 6, 6);
        ctx.fillStyle = `rgba(255,255,255,${eyeOpacity*0.8})`; ctx.fillRect(cx-10, cy-4, 2,2); ctx.fillRect(cx+8, cy-4, 2,2);

        raf = requestAnimationFrame(drawAnime);
    }

    // choose drawer based on selected style
    if (style === 'design') raf = requestAnimationFrame(drawDesign);
    else if (style === 'anime') raf = requestAnimationFrame(drawAnime);
    else raf = requestAnimationFrame(drawCartoon);

    _current_scene_visualizer = { card, canvas, stop: () => { if (raf) cancelAnimationFrame(raf); try { canvas.remove(); } catch (e) {}; visual.innerHTML = '<div style="color:#cbd5e1">Preview</div>'; // reset play button style
            try {
                const pb = card.querySelector('.btn-play-scene');
                if (pb) { pb.style.background = '#60a5fa'; pb.style.boxShadow = 'none'; }
            } catch (e) {}
            _current_scene_visualizer = null; } };
}

function stopSceneVisualizer() {
    if (_current_scene_visualizer && typeof _current_scene_visualizer.stop === 'function') {
        try { _current_scene_visualizer.stop(); } catch (e) {}
        _current_scene_visualizer = null;
    }
}

// Utility: convert #rrggbb to rgb object
function hexToRgb(hex) {
    if (!hex) return {r:0,g:0,b:0};
    const h = hex.replace('#','');
    const bigint = parseInt(h, 16);
    if (h.length === 6) {
        return { r: (bigint >> 16) & 255, g: (bigint >> 8) & 255, b: bigint & 255 };
    }
    if (h.length === 3) {
        return { r: parseInt(h[0]+h[0],16), g: parseInt(h[1]+h[1],16), b: parseInt(h[2]+h[2],16) };
    }
    return {r:0,g:0,b:0};
}

// lightenColor accepts hex and amount (0..1) to lighten (+) or darken (-)
function lightenColor(hex, amount) {
    const c = hexToRgb(hex || '#000000');
    const r = Math.min(255, Math.max(0, Math.round(c.r + 255 * amount)));
    const g = Math.min(255, Math.max(0, Math.round(c.g + 255 * amount)));
    const b = Math.min(255, Math.max(0, Math.round(c.b + 255 * amount)));
    return `rgba(${r},${g},${b},1)`;
}

// shadeColor shifts by integer amount (-100..100)
function shadeColor(hex, percent) {
    const c = hexToRgb(hex || '#000000');
    const r = Math.min(255, Math.max(0, c.r + percent));
    const g = Math.min(255, Math.max(0, c.g + percent));
    const b = Math.min(255, Math.max(0, c.b + percent));
    return `rgb(${r},${g},${b})`;
}

// --- Playback UI Panel ---
let _sw_play_panel = null;
let _sw_play_interval = null;

function attachPlaybackUI(player, track, durationSeconds) {
    // player can be an HTMLAudioElement OR a controller object with:
    // - play(): resume playback
    // - pause(): pause playback
    // - currentTime (number) or currentTime() function returning seconds
    // - duration (number)
    teardownPlaybackUI();
    // create panel
    const panel = document.createElement('div');
    panel.className = 'sw-play-panel';
    panel.style.position = 'fixed';
    panel.style.right = '20px';
    panel.style.bottom = '20px';
    panel.style.background = '#fff';
    panel.style.border = '1px solid #e2e8f0';
    panel.style.padding = '10px 12px';
    panel.style.boxShadow = '0 6px 18px rgba(0,0,0,0.08)';
    panel.style.zIndex = 9999;
    panel.innerHTML = `
        <div style="font-weight:600; margin-bottom:6px;">Playing: ${track.title}</div>
        <div style="display:flex; gap:8px; align-items:center;">
            <button id="sw-pause-resume">Pause</button>
            <button id="sw-stop">Stop</button>
            <div id="sw-time" style="margin-left:8px; font-size:0.9rem; color:#475569">0:00 / ${Math.floor(durationSeconds/60)}:${String(durationSeconds%60).padStart(2,'0')}</div>
        </div>
    `;
    document.body.appendChild(panel);
    _sw_play_panel = panel;

    let isPaused = false;
    const pauseBtn = panel.querySelector('#sw-pause-resume');
    const stopBtn = panel.querySelector('#sw-stop');
    const timeDiv = panel.querySelector('#sw-time');

    pauseBtn.addEventListener('click', () => {
        if (!player) return;
        if (isPaused) {
            try {
                if (typeof player.play === 'function') player.play();
                else if (player.audioElement && typeof player.audioElement.play === 'function') player.audioElement.play();
            } catch (e) {}
            pauseBtn.textContent = 'Pause';
            isPaused = false;
        } else {
            try {
                if (typeof player.pause === 'function') player.pause();
                else if (player.audioElement && typeof player.audioElement.pause === 'function') player.audioElement.pause();
            } catch (e) {}
            pauseBtn.textContent = 'Resume';
            isPaused = true;
        }
    });

    stopBtn.addEventListener('click', () => {
        stopCurrentPlayback();
    });

    // update time
    _sw_play_interval = setInterval(() => {
        if (!player) return;
        let cur = 0;
        try {
            if (typeof player.currentTime === 'function') cur = Math.floor(player.currentTime());
            else cur = Math.floor(player.currentTime || (player.audioElement && player.audioElement.currentTime) || 0);
        } catch (e) { cur = 0; }
        let tot = Math.floor(player.duration || (player.audioElement && player.audioElement.duration) || durationSeconds);
        const fmt = (s) => `${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`;
        timeDiv.textContent = `${fmt(cur)} / ${fmt(tot)}`;
    }, 500);
}

function teardownPlaybackUI() {
    if (_sw_play_interval) {
        clearInterval(_sw_play_interval);
        _sw_play_interval = null;
    }
    if (_sw_play_panel) {
        try { _sw_play_panel.remove(); } catch (e) {}
        _sw_play_panel = null;
    }
}

function playTrackForDuration(track, durationSeconds, sceneCard, onCompleteCallback) {
    // Attempt server-side rendering first for higher fidelity audio
    stopCurrentPlayback();
    const payload = {
        title: track.title || 'track',
        tempo: track.tempo || 120,
        key: track.key || 'C',
        genre: track.genre || 'ambient',
        duration_seconds: durationSeconds,
    };

    fetch(`${API_BASE}/render_audio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    }).then(async (res) => {
        if (!res.ok) throw new Error('Server audio render failed');
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        // create audio element for playback and UI integration
        const audio = new Audio(url);
        audio.crossOrigin = 'anonymous';
        audio.addEventListener('ended', () => {
            teardownPlaybackUI();
            if (onCompleteCallback) onCompleteCallback();
        });
        audio.play().catch(err => {
            console.error('Playback error', err);
            showError('Playback failed: ' + err.message);
        });
        attachPlaybackUI(audio, track, durationSeconds);
        
        // Connect audio to AnalyserNode for frequency-driven visualizer (if scene card provided)
        if (sceneCard) {
            try {
                const ctx = _ensureAudioContext();
                const analyser = ctx.createAnalyser();
                analyser.fftSize = 256;
                // Create MediaElementAudioSourceNode and connect to analyser
                const source = ctx.createMediaElementAudioSource(audio);
                source.connect(analyser);
                analyser.connect(ctx.destination);
                // Store analyser on scene card for visualizer to use
                sceneCard._analyser = analyser;
                sceneCard._audioContext = ctx;
            } catch (e) {
                console.warn('Could not connect analyser', e);
            }
        }
        
        _sw_playing = { audioElement: audio, blobUrl: url };
    }).catch(err => {
        console.warn('Server render failed, falling back to client synth:', err);
        // Fallback to client-side synth
        const ctx = _ensureAudioContext();
        const now = ctx.currentTime + 0.05;
        const seed = _hashToSeed(track.title + '|' + (track.genre || '') + '|' + (track.tempo || 120));
        const rnd = _seededRandom(seed);
        const scale = _buildScaleFrequencies(track.key || 'C');
        const bpm = Math.max(60, track.tempo || 120);
        const quarterSec = 60 / bpm; // duration of a beat
        const notesCount = Math.max(8, Math.floor((durationSeconds / quarterSec)));

        const sourceNodes = [];

        for (let i = 0; i < notesCount; i++) {
            const tStart = now + i * quarterSec;
            const length = quarterSec * (rnd() < 0.8 ? 1 : 0.5);
            // pick pitch
            const idx = Math.floor(rnd() * scale.length);
            const freq = scale[idx] * (rnd() < 0.2 ? 0.5 : 1);

            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.value = freq;
            gain.gain.value = 0.0001;
            osc.connect(gain);
            gain.connect(ctx.destination);

            // Envelope
            gain.gain.setValueAtTime(0.0001, tStart);
            gain.gain.exponentialRampToValueAtTime(0.08 * (0.6 + rnd() * 0.8), tStart + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.0001, tStart + length);

            osc.start(tStart);
            osc.stop(tStart + length + 0.05);

            sourceNodes.push(osc);
        }

        _sw_playing = { sourceNodes, stopTime: now + durationSeconds + 0.5 };

        // Create a lightweight controller for synth playback so the UI can control/pause/resume and show time
        const synthController = {
            play: () => ctx.resume(),
            pause: () => ctx.suspend(),
            // return current playback position in seconds
            currentTime: () => Math.max(0, ctx.currentTime - now),
            duration: durationSeconds,
            // expose audioElement for compatibility (none for synth)
            audioElement: null,
        };

        // Attach the playback UI which will call synthController.play/pause and read currentTime()
        attachPlaybackUI(synthController, track, durationSeconds);

        // Store controller on playing state so stopCurrentPlayback can access it if needed
        _sw_playing.controller = synthController;

        // Safety stop after duration
        setTimeout(() => {
            if (_sw_playing && ctx.currentTime >= _sw_playing.stopTime) stopCurrentPlayback();
        }, (durationSeconds + 1) * 1000);
    });
}

// Attach event delegation for play/stop buttons
document.addEventListener('click', (e) => {
    const el = e.target;
    if (el.classList.contains('btn-play-1m')) {
        const card = el.closest('.track-card');
        const title = card.querySelector('.track-title').textContent;
        const tempoText = card.querySelector('.track-tempo').textContent || '120';
        const tempo = parseInt(tempoText.replace(/[^0-9]/g, '')) || 120;
        const track = { title, tempo, key: 'C' };
        playTrackForDuration(track, 60);
    } else if (el.classList.contains('btn-play-2m')) {
        const card = el.closest('.track-card');
        const title = card.querySelector('.track-title').textContent;
        const tempoText = card.querySelector('.track-tempo').textContent || '120';
        const tempo = parseInt(tempoText.replace(/[^0-9]/g, '')) || 120;
        const track = { title, tempo, key: 'C' };
        playTrackForDuration(track, 120);
    } else if (el.classList.contains('btn-stop')) {
        stopCurrentPlayback();
    } else if (el.classList.contains('btn-play-scene')) {
        // Play the ambient/music for a scene card
        const card = el.closest('.scene-card');
        if (!card) return;
        const titleEl = card.querySelector('.scene-title');
        const title = titleEl ? titleEl.textContent : 'Scene';
        const duration = parseInt(card.dataset.duration) || 60;
        // build a simple ambient track descriptor
        const track = {
            title: `Scene: ${title}`,
            tempo: 60,
            key: 'C',
            genre: 'ambient',
        };
        // Show loading spinner on button
        const originalText = el.textContent;
        el.textContent = '⏳ Loading...';
        el.disabled = true;
        el.style.opacity = '0.6';
        // start audio and the scene visualizer
        playTrackForDuration(track, duration, card, () => {
            // on playback complete callback: restore button
            el.textContent = originalText;
            el.disabled = false;
            el.style.opacity = '1';
        });
        try { startSceneVisualizer(card); } catch (e) { console.warn('Visualizer start failed', e); }
    }
});

/**
 * Display scenes
 */
function displayScenes(scenes) {
    const panel = document.getElementById('scenesPanel');
    panel.innerHTML = '';

    if (scenes.length === 0) {
        panel.innerHTML = '<p>No scenes available</p>';
        return;
    }

    const timeline = document.createElement('div');
    timeline.className = 'scenes-timeline';

    scenes.forEach(scene => {
        const card = document.createElement('div');
        card.className = 'scene-card';
        // store duration for playback (seconds)
        card.dataset.duration = scene.duration_seconds || 60;

        // Left content (text)
        const left = document.createElement('div');
        left.style.flex = '1';
        left.innerHTML = `
            <div class="scene-title">Act ${scene.act}: ${scene.title}</div>
            <div class="scene-setting">Setting: ${scene.setting}</div>
            <div class="scene-description">${scene.description}</div>
            <div style="font-size: 0.9rem; color: #718096; margin-bottom: 8px;">
                <strong>Atmosphere:</strong> ${Object.entries(scene.atmosphere || {})
            .map(([k, v]) => `${k.toUpperCase()}: ${v}`)
            .join(' | ')}
            </div>
            <div style="font-size: 0.9rem; color: #718096;">
                <strong>Tone:</strong> ${scene.emotional_tone} | <strong>Pacing:</strong> ${scene.pacing}
            </div>
            <div style="margin-top:8px;">
                <button class="btn-play-scene">Play Scene</button>
            </div>
        `;

        // Right visual rectangle (video-like) - will host a canvas visualizer
        const right = document.createElement('div');
        right.className = 'scene-visual';
        right.style.width = '220px';
        right.style.height = '140px';
        right.style.flexShrink = '0';
        right.style.border = '1px solid #e2e8f0';
        right.style.borderRadius = '8px';
        right.style.background = '#0f172a';
        right.style.display = 'flex';
        right.style.alignItems = 'center';
        right.style.justifyContent = 'center';
        right.style.overflow = 'hidden';
        right.style.marginLeft = '12px';

        // placeholder content
        const rightLabel = document.createElement('div');
        rightLabel.style.color = '#cbd5e1';
        rightLabel.style.fontSize = '0.85rem';
        rightLabel.textContent = 'Preview';
        right.appendChild(rightLabel);

        card.style.display = 'flex';
        card.style.justifyContent = 'space-between';
        card.style.gap = '12px';
        card.appendChild(left);
        card.appendChild(right);
        timeline.appendChild(card);

        // Attach scene data to card for the visualizer to use
        try { card._scene = scene; } catch (e) { /* ignore */ }

        // style the Play Scene button background for visibility
        const playBtn = card.querySelector('.btn-play-scene');
        if (playBtn) {
            playBtn.style.background = '#60a5fa';
            playBtn.style.color = '#fff';
            playBtn.style.border = 'none';
            playBtn.style.padding = '6px 10px';
            playBtn.style.borderRadius = '6px';
            playBtn.style.cursor = 'pointer';
        }

        // Add a style selector for preview rendering: Cartoon, Design, Anime
        const styleWrapper = document.createElement('div');
        styleWrapper.style.marginTop = '8px';
        const styleLabel = document.createElement('label');
        styleLabel.textContent = 'Preview style:';
        styleLabel.style.fontSize = '0.8rem';
        styleLabel.style.color = '#475569';
        styleLabel.style.marginRight = '6px';
        const styleSelect = document.createElement('select');
        ['cartoon','design','anime'].forEach(opt => {
            const o = document.createElement('option'); o.value = opt; o.textContent = opt.charAt(0).toUpperCase()+opt.slice(1); styleSelect.appendChild(o);
        });
        styleSelect.value = 'cartoon';
        styleWrapper.appendChild(styleLabel);
        styleWrapper.appendChild(styleSelect);
        // place the style selector below the Play Scene button
        left.appendChild(styleWrapper);
        // store selected style on card
        card._scene_style = styleSelect.value;
        styleSelect.addEventListener('change', (ev) => { card._scene_style = styleSelect.value; });
    });

    panel.appendChild(timeline);
}

/**
 * Display music tracks
 */
function displayMusic(tracks) {
    const panel = document.getElementById('musicPanel');
    panel.innerHTML = '';

    if (tracks.length === 0) {
        panel.innerHTML = '<p>No music tracks available</p>';
        return;
    }

    const grid = document.createElement('div');
    grid.className = 'music-tracks';

    tracks.forEach(track => {
        const card = document.createElement('div');
        card.className = 'track-card';
        card.innerHTML = `
            <div class="track-title">${track.title}</div>
            <div class="track-genre">${track.genre.toUpperCase()}</div>
            <div class="track-tempo">🎵 ${track.tempo} BPM</div>
            <div class="track-instruments">
                <strong>Instruments:</strong> ${track.instruments?.join(', ') || 'N/A'}
            </div>
            <div style="margin-top: 8px;">
                <span class="track-emotion">${track.emotional_tone}</span>
            </div>
            <div style="font-size: 0.85rem; color: #718096; margin-top: 8px;">
                <strong>Duration:</strong> ${track.duration_seconds}s
            </div>
            <div class="track-controls" style="margin-top:12px; display:flex; gap:8px;">
                <button class="btn-play-1m">Play 1m</button>
                <button class="btn-play-2m">Play 2m</button>
                <button class="btn-stop">Stop</button>
            </div>
        `;
        grid.appendChild(card);
    });

    panel.appendChild(grid);
}

/**
 * Display quality assessment
 */
function displayQualityAssessment(assessment, recommendations) {
    const scoresDiv = document.getElementById('qualityScores');
    scoresDiv.innerHTML = '';

    // Display scores
    if (assessment.scores) {
        Object.entries(assessment.scores).forEach(([dimension, score]) => {
            const card = document.createElement('div');
            card.className = 'score-card';
            card.innerHTML = `
                <div class="score-label">${dimension.replace(/_/g, ' ').toUpperCase()}</div>
                <div class="score-value">${(score * 100).toFixed(0)}%</div>
            `;
            scoresDiv.appendChild(card);
        });
    }

    // Display overall score
    const overallDiv = document.createElement('div');
    overallDiv.className = 'score-card';
    overallDiv.style.gridColumn = 'span 2';
    overallDiv.innerHTML = `
        <div class="score-label">OVERALL QUALITY</div>
        <div class="score-value">${(assessment.overall_score * 100).toFixed(0)}%</div>
    `;
    scoresDiv.appendChild(overallDiv);

    // Display recommendations
    const recsDiv = document.getElementById('recommendations');
    recsDiv.innerHTML = '';

    if (recommendations && recommendations.length > 0) {
        const title = document.createElement('h4');
        title.textContent = '💡 Recommendations for Improvement';
        title.style.marginBottom = '15px';
        recsDiv.appendChild(title);

        recommendations.forEach(rec => {
            const item = document.createElement('div');
            item.className = 'recommendation-item';
            item.innerHTML = `
                <span class="recommendation-priority ${rec.priority}">${rec.priority.toUpperCase()}</span>
                ${rec.suggestion}
            `;
            recsDiv.appendChild(item);
        });
    } else {
        recsDiv.innerHTML = '<p>✨ Excellent! No improvements suggested at this time.</p>';
    }
}

/**
 * Display memory status
 */
function displayMemoryStatus(summary, stats) {
    const statusDiv = document.getElementById('memoryStatus');
    statusDiv.innerHTML = '';

    // Memory summary
    if (summary) {
        const title = document.createElement('h4');
        title.textContent = 'Memory Summary';
        title.style.marginBottom = '10px';
        statusDiv.appendChild(title);

        Object.entries(summary).forEach(([category, count]) => {
            const item = document.createElement('div');
            item.className = 'memory-category';
            item.innerHTML = `
                <span class="memory-label">${category.replace(/_/g, ' ').toUpperCase()}:</span>
                <span class="memory-value">${count}</span>
            `;
            statusDiv.appendChild(item);
        });
    }

    // Learning stats
    if (stats) {
        const statsTitle = document.createElement('h4');
        statsTitle.textContent = 'Learning Patterns';
        statsTitle.style.marginTop = '20px';
        statsTitle.style.marginBottom = '10px';
        statusDiv.appendChild(statsTitle);

        Object.entries(stats).forEach(([pattern, values]) => {
            if (values.count > 0) {
                const item = document.createElement('div');
                item.className = 'memory-category';
                item.innerHTML = `
                    <strong>${pattern.replace(/_/g, ' ').toUpperCase()}</strong><br>
                    <small>Mean: ${values.mean.toFixed(3)}, Std: ${values.std.toFixed(3)}, Max: ${values.max.toFixed(3)}</small>
                `;
                statusDiv.appendChild(item);
            }
        });
    }
}

/**
 * Display pipeline execution log
 */
function displayPipelineLog(log) {
    const logDiv = document.getElementById('pipelineLog');
    logDiv.innerHTML = '';

    if (!log || log.length === 0) {
        logDiv.innerHTML = '<p>No log entries available</p>';
        return;
    }

    log.forEach(entry => {
        const logEntry = document.createElement('div');
        logEntry.className = 'pipeline-log-entry';

        const time = new Date(entry.timestamp).toLocaleTimeString();
        const type = entry.event_type;
        const details = JSON.stringify(entry.details || {});

        logEntry.innerHTML = `
            <span class="log-timestamp">[${time}]</span> 
            <span class="log-type">${type}</span>
            <div class="log-details">${details}</div>
        `;
        logDiv.appendChild(logEntry);
    });
}

/**
 * Show loading indicator
 */
function showLoading() {
    loadingIndicator.classList.remove('hidden');
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    loadingIndicator.classList.add('hidden');
}

/**
 * Show error message
 */
function showError(message) {
    console.error('[StoryWeaver] Error:', message);
    errorMessage.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <strong>Error:</strong> ${message}
                <div style="font-size: 0.9rem; color: #888; margin-top: 6px;">
                    Check browser console (F12) for more details.
                </div>
            </div>
            <button onclick="hideError()" style="background: none; border: none; font-size: 1.2rem; cursor: pointer; padding: 0;">×</button>
        </div>
    `;
    errorMessage.classList.remove('hidden');
    errorMessage.style.marginBottom = '20px';
    // Auto-hide after 10 seconds
    setTimeout(() => {
        if (!errorMessage.classList.contains('hidden')) {
            hideError();
        }
    }, 10000);
}

/**
 * Hide error message
 */
function hideError() {
    errorMessage.classList.add('hidden');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('[StoryWeaver] Frontend loaded');
    console.log('[StoryWeaver] API_BASE:', API_BASE);
    console.log('[StoryWeaver] storyForm:', storyForm);
    console.log('[StoryWeaver] feedbackForm:', feedbackForm);
    
    if (!storyForm) {
        console.error('[StoryWeaver] ERROR: storyForm not found in DOM!');
    }
    if (!feedbackForm) {
        console.error('[StoryWeaver] ERROR: feedbackForm not found in DOM!');
    }
});
