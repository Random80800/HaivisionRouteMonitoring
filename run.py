from app import create_app
from app.database.db import init_db
from app.services.poller import start_background_poller

app = create_app()

if __name__ == "__main__":
    init_db()
    start_background_poller()
    app.run(host="0.0.0.0", port=5050, debug=True)