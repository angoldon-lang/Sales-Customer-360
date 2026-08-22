import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.config import Settings


@pytest.fixture(scope="session")
def test_db():
    """Create test database."""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def db_session(test_db):
    """Create test database session."""
    connection = test_db.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_settings():
    """Test settings."""
    return Settings(
        database_url="sqlite:///:memory:",
        debug=True,
        news_search_provider="mock",
        ai_provider="mock",
    )
