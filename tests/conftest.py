import os
import tempfile
import pytest
from app import app as flask_app
import database.db as db_module


@pytest.fixture
def app():
    # Create a temporary SQLite database for isolated test execution
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    original_db_path = db_module.DATABASE_PATH
    db_module.DATABASE_PATH = db_path

    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-12345",
    })

    # Initialize tables
    db_module.init_db(db_path)

    yield flask_app

    # Teardown database and restore global path
    db_module.DATABASE_PATH = original_db_path
    os.close(db_fd)
    if os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except OSError:
            pass


@pytest.fixture
def client(app):
    """Flask test client fixture."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Provides a direct connection to the test database within app context."""
    with app.app_context():
        yield db_module.get_db()
