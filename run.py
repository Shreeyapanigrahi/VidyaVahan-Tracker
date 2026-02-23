import os
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist (useful for SQLite/Local Dev)
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode)
    app.run(debug=True)
if __name__ == "__main__":
    app.run(debug=True)


