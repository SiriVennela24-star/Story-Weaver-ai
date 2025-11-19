"""
Frontend server for StoryWeaver AI.
Serves the web UI on a separate port from the API.
"""

from flask import Flask, render_template
import os

# Initialize Flask app for frontend
app = Flask(__name__, template_folder='templates', static_folder='static')

# Get absolute paths
template_dir = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(template_dir, 'templates')


@app.route('/')
def index():
    """Serve the main UI page."""
    return render_template('index.html')


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('index.html')


if __name__ == '__main__':
    print("Starting StoryWeaver AI Frontend...")
    print("Frontend available at: http://localhost:3000")
    print("Backend API available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=3000)
