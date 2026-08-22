# Customer Intelligence Monitor

An intelligent system for monitoring news and public information about business clients, generating automated or semi-automated email reports by cluster.

## Features

- **Easy Client Import**: Upload CSV/Excel files with minimal data (company_name, optional vat_number, optional cluster)
- **Automatic Data Enrichment**: System enriches client data automatically by searching for website, sector, country, etc.
- **News Monitoring**: Searches for relevant public news about monitored companies
- **AI Classification**: Classifies news articles by category and scores (relevance, urgency, commercial value, risk)
- **Cluster-Based Reports**: Organize companies into clusters for targeted reporting
- **Email Delivery**: Generates and sends HTML/text email reports to configured recipients
- **Flexible Configuration**: Set reporting frequency, minimum relevance threshold, and topics per cluster

## Architecture

```
Customer Intelligence Monitor/
├── backend/
│   ├── app/
│   │   ├── models/              # SQLAlchemy models (Company, Cluster, News, Report)
│   │   ├── routers/             # API endpoints
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # CRUD and business logic
│   │   ├── core/                # Core modules (importer, enricher, news_search, classifier, report_gen, email)
│   │   ├── main.py              # FastAPI app
│   │   ├── database.py          # SQLite config
│   │   └── config.py            # Settings
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/                     # React frontend (placeholder)
├── docker-compose.yml
└── README.md
```

## Stack

- **Backend**: Python + FastAPI + SQLAlchemy
- **Database**: SQLite (MVP), upgradeable to PostgreSQL
- **Frontend**: React (future)
- **Import**: Pandas + OpenPyXL for CSV/Excel
- **AI**: Claude/OpenAI (pluggable, mock available for dev)
- **Email**: SMTP (mock available for dev)
- **News Search**: Bing/SerpAPI (pluggable, mock available for dev)

## Quick Start

### Local Setup

```bash
# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup .env
cp .env.example .env

# Run migrations (creates SQLite database)
python -c "from app.database import init_db; init_db()"

# Start server
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

**API Documentation**: http://localhost:8000/docs

### With Docker Compose

```bash
docker-compose up -d
```

## API Endpoints

### Companies

- `POST /api/companies/` - Create company
- `GET /api/companies/` - List companies
- `GET /api/companies/{id}` - Get company
- `PUT /api/companies/{id}` - Update company
- `DELETE /api/companies/{id}` - Delete company

### Clusters

- `POST /api/clusters/` - Create cluster
- `GET /api/clusters/` - List clusters
- `GET /api/clusters/{id}` - Get cluster
- `PUT /api/clusters/{id}` - Update cluster
- `DELETE /api/clusters/{id}` - Delete cluster
- `POST /api/clusters/{id}/companies/{company_id}` - Add company to cluster
- `DELETE /api/clusters/{id}/companies/{company_id}` - Remove company from cluster
- `POST /api/clusters/{id}/recipients` - Add email recipient
- `DELETE /api/clusters/{id}/recipients/{recipient_id}` - Remove recipient

### News

- `POST /api/news/` - Create news item
- `GET /api/news/{id}` - Get news item
- `GET /api/news/company/{company_id}` - Get news for company
- `GET /api/news/status/{status}` - Get news by status
- `PUT /api/news/{id}` - Update news item
- `POST /api/news/{id}/approve` - Approve news
- `POST /api/news/{id}/reject` - Reject news
- `DELETE /api/news/{id}` - Delete news

### Reports

- `POST /api/reports/` - Create report
- `GET /api/reports/{id}` - Get report
- `GET /api/reports/cluster/{cluster_id}` - Get cluster reports
- `PUT /api/reports/{id}` - Update report
- `DELETE /api/reports/{id}` - Delete report
- `POST /api/reports/cluster/{cluster_id}/generate` - Generate report for cluster
- `POST /api/reports/{id}/send` - Send report to recipients

### Import

- `POST /api/import/companies/csv` - Import from CSV file
- `POST /api/import/companies/excel` - Import from Excel file

## Data Models

### Company

```
{
  "id": 1,
  "company_name": "Example Corp",
  "vat_number": "IT12345678",
  "website": "https://example.com",
  "sector": "Technology",
  "country": "IT",
  "status": "active" | "paused" | "needs_review" | "archived",
  "created_at": "2024-08-22T10:00:00",
  "updated_at": "2024-08-22T10:00:00"
}
```

### Cluster

```
{
  "id": 1,
  "cluster_name": "Sales Nord",
  "description": "Northern sales cluster",
  "frequency": "weekly" | "daily" | "monthly",
  "min_relevance_score": 5,  # 1-10
  "report_type": "complete" | "synthetic" | "alert",
  "topics": "investimenti, partnership, digital",
  "recipients": [
    {
      "id": 1,
      "email": "salesnord@company.it",
      "name": "Northern Sales",
      "active": true
    }
  ]
}
```

### News Item

```
{
  "id": 1,
  "company_id": 1,
  "title": "Company announces new partnership",
  "source": "Financial Times",
  "url": "https://example.com/news",
  "published_date": "2024-08-22T10:00:00",
  "summary": "Company has partnered with...",
  "category": "partnership" | "acquisition" | "investment" | ...,
  "relevance_score": 8,      # 1-10
  "urgency_score": 5,        # 1-10
  "commercial_score": 7,     # 1-10
  "risk_score": 3,           # 1-10
  "confidence_score": 9,     # 1-10
  "status": "new" | "approved" | "rejected" | "duplicate" | "needs_review" | "sent"
}
```

### Report

```
{
  "id": 1,
  "cluster_id": 1,
  "subject": "Customer Intelligence Report - Sales Nord - 2024-08-22",
  "body_html": "<html>...",
  "body_text": "Text version...",
  "status": "draft" | "ready" | "sent" | "failed",
  "period_start": "2024-08-15",
  "period_end": "2024-08-22",
  "sent_at": "2024-08-22T15:00:00",
  "created_at": "2024-08-22T10:00:00"
}
```

## Workflow

1. **Import Companies**: Upload CSV/Excel with company_name, vat_number (optional), cluster (optional)
2. **Enrich Data**: System automatically searches for website, sector, country
3. **Configure Clusters**: Create clusters, set recipients, frequency, relevance threshold, topics
4. **Monitor News**: System searches for news about companies
5. **Classify News**: AI classifies news by category and scores
6. **Review & Approve**: Admin/user reviews news and approves for reporting
7. **Generate Reports**: Create cluster reports from approved news
8. **Send Reports**: Send HTML/text emails to cluster recipients

## News Categories

- `investment` - Investment announcements
- `acquisition` - M&A activity
- `merger` - Merger announcements
- `partnership` - Partnership agreements
- `new_office` - New office/expansion
- `industrial_plan` - Industrial strategy
- `financial_results` - Earnings announcements
- `crisis` - Financial or operational crisis
- `management_change` - CxO changes
- `cyber_incident` - Cybersecurity incidents
- `data_breach` - Data breach notifications
- `operational_issue` - Operational problems
- `tender` - Public tenders/bids
- `digital_project` - Digital transformation
- `other` - Other news

## Scoring (1-10)

- **relevance_score**: How relevant to the company/cluster
- **urgency_score**: How quickly needs attention
- **commercial_score**: Business opportunity value
- **risk_score**: Risk/threat level
- **confidence_score**: Confidence in company association

## Configuration

Create `.env` file in `backend/` directory:

```env
# Database
DATABASE_URL=sqlite:///./customer_intelligence.db

# Email (for sending reports)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@company.local

# News search provider (mock|bing|serp)
NEWS_SEARCH_PROVIDER=mock
NEWS_SEARCH_API_KEY=your-key

# AI provider (mock|claude|openai)
AI_PROVIDER=mock
AI_API_KEY=your-key
```

## Development

### Run Tests

```bash
pytest
```

### Mock Data Flow

By default, the system runs with mock providers for:
- News search (returns sample articles)
- AI classification (basic keyword matching)
- Email delivery (prints to console)

This allows full testing without external APIs.

## Future Enhancements

1. **Real News Search**: Integrate Bing Search API / SerpAPI / GDELT
2. **Claude AI Integration**: Full NLP classification via Claude API
3. **Web Dashboard**: React frontend for management
4. **Scheduler**: APScheduler for automated report generation
5. **PostgreSQL**: Upgrade to production database
6. **Authentication**: JWT-based user management
7. **RBAC**: Role-based access control
8. **Webhooks**: Integration with Slack, Microsoft Teams
9. **Advanced Filtering**: Topic-based, date range, source filtering
10. **Analytics**: Report history, metrics, trending topics

## Project Structure

### Core Modules

- **`app/core/importer.py`**: CSV/Excel parsing and validation
- **`app/core/enricher.py`**: Company data enrichment (abstract + mock)
- **`app/core/news_search.py`**: News search provider (abstract + mock)
- **`app/core/classifier.py`**: AI classification provider (abstract + mock)
- **`app/core/report_generator.py`**: HTML/text report generation
- **`app/core/email_delivery.py`**: Email sending (abstract + mock)

### Services Layer

- **`app/services/company_service.py`**: Company CRUD
- **`app/services/cluster_service.py`**: Cluster CRUD + associations
- **`app/services/news_service.py`**: News CRUD
- **`app/services/report_service.py`**: Report CRUD

### API Routers

- **`app/routers/importer.py`**: CSV/Excel import endpoints
- **`app/routers/companies.py`**: Company management
- **`app/routers/clusters.py`**: Cluster management
- **`app/routers/news.py`**: News management
- **`app/routers/reports.py`**: Report generation and delivery

## Important Rules

- Never send news without source/URL
- Don't invent missing information
- Flag ambiguous company matches for review
- Don't auto-send low confidence news
- Deduplicate by URL
- Save all history
- All reports must be reproducible
- Every news item must have source link

## Support

For issues or questions, please refer to the documentation or create an issue in the repository.
