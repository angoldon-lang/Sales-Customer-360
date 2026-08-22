import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, init_db, engine, Base


@pytest.fixture(scope="module")
def setup_test_db():
    """Setup test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(setup_test_db):
    """Create test client."""
    return TestClient(app)


def test_health_check(client):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data
    assert data["name"] == "Customer Intelligence Monitor"


def test_create_company(client):
    """Test company creation."""
    company_data = {
        "company_name": "Test Corp",
        "vat_number": "IT12345678",
        "website": "https://test.com",
        "sector": "Technology",
        "country": "IT",
    }
    response = client.post("/api/companies/", json=company_data)
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "Test Corp"
    assert data["vat_number"] == "IT12345678"
    assert data["id"] is not None


def test_list_companies(client):
    """Test company listing."""
    # Create a company first
    company_data = {
        "company_name": "Test Corp 2",
        "vat_number": "IT87654321",
    }
    client.post("/api/companies/", json=company_data)

    # List companies
    response = client.get("/api/companies/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_create_cluster(client):
    """Test cluster creation."""
    cluster_data = {
        "cluster_name": "Sales Nord",
        "frequency": "weekly",
        "min_relevance_score": 5,
    }
    response = client.post("/api/clusters/", json=cluster_data)
    assert response.status_code == 200
    data = response.json()
    assert data["cluster_name"] == "Sales Nord"
    assert data["id"] is not None


def test_add_recipient_to_cluster(client):
    """Test adding email recipient to cluster."""
    # Create cluster
    cluster_data = {
        "cluster_name": "Test Cluster",
        "frequency": "daily",
    }
    cluster_response = client.post("/api/clusters/", json=cluster_data)
    cluster_id = cluster_response.json()["id"]

    # Add recipient
    recipient_data = {
        "email": "test@example.com",
        "name": "Test User",
        "active": True,
    }
    response = client.post(f"/api/clusters/{cluster_id}/recipients", json=recipient_data)
    assert response.status_code == 200
    assert response.json()["status"] == "added"


def test_associate_company_with_cluster(client):
    """Test associating company with cluster."""
    # Create company
    company_data = {"company_name": "Test Corp 3"}
    company_response = client.post("/api/companies/", json=company_data)
    company_id = company_response.json()["id"]

    # Create cluster
    cluster_data = {"cluster_name": "Test Cluster 2"}
    cluster_response = client.post("/api/clusters/", json=cluster_data)
    cluster_id = cluster_response.json()["id"]

    # Associate
    response = client.post(f"/api/clusters/{cluster_id}/companies/{company_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "added"


def test_create_news_item(client):
    """Test creating a news item."""
    # Create company first
    company_data = {"company_name": "Test Corp 4"}
    company_response = client.post("/api/companies/", json=company_data)
    company_id = company_response.json()["id"]

    # Create news
    news_data = {
        "company_id": company_id,
        "title": "Breaking News",
        "source": "Reuters",
        "url": "https://example.com/news1",
        "summary": "This is test news",
        "category": "partnership",
        "relevance_score": 8,
        "urgency_score": 6,
        "commercial_score": 7,
        "risk_score": 2,
        "confidence_score": 9,
    }
    response = client.post("/api/news/", json=news_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Breaking News"
    assert data["status"] == "new"


def test_approve_news(client):
    """Test approving a news item."""
    # Create company and news
    company_data = {"company_name": "Test Corp 5"}
    company_response = client.post("/api/companies/", json=company_data)
    company_id = company_response.json()["id"]

    news_data = {
        "company_id": company_id,
        "title": "News to Approve",
        "source": "Reuters",
        "url": "https://example.com/news2",
    }
    news_response = client.post("/api/news/", json=news_data)
    news_id = news_response.json()["id"]

    # Approve
    response = client.post(f"/api/news/{news_id}/approve")
    assert response.status_code == 200
    assert response.json()["status"] == "approved"


def test_generate_report(client):
    """Test report generation for a cluster."""
    # Create company, cluster, associate them
    company_data = {"company_name": "Test Corp 6"}
    company_response = client.post("/api/companies/", json=company_data)
    company_id = company_response.json()["id"]

    cluster_data = {"cluster_name": "Report Test Cluster"}
    cluster_response = client.post("/api/clusters/", json=cluster_data)
    cluster_id = cluster_response.json()["id"]

    # Associate company with cluster
    client.post(f"/api/clusters/{cluster_id}/companies/{company_id}")

    # Create and approve news
    news_data = {
        "company_id": company_id,
        "title": "Report Test News",
        "source": "Reuters",
        "url": "https://example.com/news3",
    }
    news_response = client.post("/api/news/", json=news_data)
    news_id = news_response.json()["id"]
    client.post(f"/api/news/{news_id}/approve")

    # Generate report
    response = client.post(f"/api/reports/cluster/{cluster_id}/generate?days=7")
    assert response.status_code == 200
    data = response.json()
    assert "report_id" in data
    assert data["status"] == "draft"
    assert data["subject"] is not None
