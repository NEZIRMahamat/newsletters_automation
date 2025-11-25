from flask import Flask
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Context processor to inject current date
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}

    # Register routes
    from routes.newsletter import newsletter_bp
    app.register_blueprint(newsletter_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
