from flask import Flask

def create_app():
    app = Flask(__name__)

    # Register routes
    from web.routes.newsletter import newsletter_bp
    app.register_blueprint(newsletter_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
