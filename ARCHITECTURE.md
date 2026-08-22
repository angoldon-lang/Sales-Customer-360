# Customer Intelligence Monitor - Architecture

## Vision

Transform minimal client input (company name, optional VAT, optional cluster) into actionable intelligence through:
1. **Automatic Data Enrichment** — Website, sector, country detection
2. **News Aggregation** — Real-time monitoring of public company information
3. **AI Classification** — Multi-factor scoring (relevance, urgency, commercial value, risk)
4. **Cluster-Based Reporting** — Targeted email reports by organizational group
5. **Pluggable Architecture** — Swap news providers, AI classifiers, email backends

---

## Database Schema

### Core Tables

#### `companies`
Monitored companies with enriched data.

| Field | Type | Notes |
|-------|------|-------|
| `id` | INT PK | Primary key |
| `company_name` | VARCHAR(255) | Company name (indexed) |
| `vat_number` | VARCHAR(50) | VAT/P.IVA (unique, indexed) |
| `website` | VARCHAR(255) | Auto-enriched website |
| `sector` | VARCHAR(100) | Industry (auto-enriched) |
| `country` | VARCHAR(100) | Country code (auto-enriched) |
| `status` | ENUM | active, paused, needs_review, archived |
| `created_at` | DATETIME | Creation timestamp |
| `updated_at` | DATETIME | Last update timestamp |

**Relationships:**
- 1:N `news_items` — News articles about this company
- M:N `clusters` — Via `company_clusters` junction table

---

#### `clusters`
Organizational groupings for targeted reporting.

| Field | Type | Notes |
|-------|------|-------|
| `id` | INT PK | Primary key |
| `cluster_name` | VARCHAR(255) | Unique cluster name |
| `description` | VARCHAR(1000) | Optional description |
| `frequency` | ENUM | daily, weekly, monthly |
| `min_relevance_score` | INT | 1-10, threshold for auto-inclusion |
| `report_type` | ENUM | synthetic, complete, alert |
| `topics` | VARCHAR(500) | Comma-separated priority topics |
| `created_at` | DATETIME | Creation timestamp |
| `updated_at` | DATETIME | Last update timestamp |

**Relationships:**
- 1:N `cluster_recipients` — Email destinations
- M:N `companies` — Via `company_clusters` junction table
- 1:N `reports` — Generated reports

---

#### `cluster_recipients`
Email recipients for each cluster.

| Field | Type | Notes |
|-------|------|-------|
| `id` | INT PK | Primary key |
| `cluster_id` | INT FK | Parent cluster |
| `email` | VARCHAR(255) | Email address |
| `name` | VARCHAR(255) | Recipient name |
| `active` | BOOLEAN | Whether to send emails |
| `created_at` | DATETIME | Creation timestamp |

---

#### `company_clusters`
Many-to-many association (companies → clusters).

| Field | Type | Notes |
|-------|------|-------|
| `company_id` | INT FK | Company ID (PK) |
| `cluster_id` | INT FK | Cluster ID (PK) |
| `created_at` | DATETIME | Association timestamp |

**Note:** One company can belong to multiple clusters.

---

#### `news_items`
News articles and public information about companies.

| Field | Type | Notes |
|-------|------|-------|
| `id` | INT PK | Primary key |
| `company_id` | INT FK | Associated company |
| `title` | VARCHAR(500) | Article title |
| `source` | VARCHAR(255) | News source name |
| `url` | VARCHAR(500) | Unique article URL (indexed) |
| `published_date` | DATETIME | Publication date (indexed) |
| `summary` | TEXT | Short summary |
| `category` | ENUM | investment, acquisition, merger, partnership, new_office, industrial_plan, financial_results, crisis, management_change, cyber_incident, data_breach, operational_issue, tender, digital_project, other |
| `relevance_score` | INT | 1-10 |
| `urgency_score` | INT | 1-10 |
| `commercial_score` | INT | 1-10 |
| `risk_score` | INT | 1-10 |
| `confidence_score` | INT | 1-10 |
| `status` | ENUM | new, approved, rejected, duplicate, needs_review, sent |
| `created_at` | DATETIME | Discovery timestamp |
| `updated_at` | DATETIME | Last update timestamp |

**Scoring:** All scores 1-10. Scores determine inclusion in reports and alert urgency.

**Status Workflow:**
- `new` → Auto-discovered article
- `approved` → Admin reviewed and approved
- `rejected` → Not relevant
- `duplicate` → Same article from different source
- `needs_review` → Ambiguous (low confidence_score)
- `sent` → Included in sent report

---

#### `reports`
Generated email reports.

| Field | Type | Notes |
|-------|------|-------|
| `id` | INT PK | Primary key |
| `cluster_id` | INT FK | Destination cluster |
| `subject` | VARCHAR(500) | Email subject |
| `body_html` | TEXT | HTML version |
| `body_text` | TEXT | Plain text version |
| `status` | ENUM | draft, ready, sent, failed |
| `period_start` | DATETIME | Report period start |
| `period_end` | DATETIME | Report period end |
| `sent_at` | DATETIME | When report was sent |
| `created_at` | DATETIME | Report creation time |
| `updated_at` | DATETIME | Last update timestamp |

---

## System Architecture

### Layers

```
┌─────────────────────────────────────────────┐
│         FastAPI Application Layer           │
├─────────────────────────────────────────────┤
│  Routers: Companies, Clusters, News, Reports│
├─────────────────────────────────────────────┤
│       Service Layer (CRUD Operations)       │
├─────────────────────────────────────────────┤
│   Core Modules (Pluggable Architecture)     │
│  ┌────────────────────────────────────────┐ │
│  │ Importer    → CSV/Excel parsing        │ │
│  │ Enricher    → Company data enrichment  │ │
│  │ NewsSearch  → News aggregation         │ │
│  │ Classifier  → AI classification        │ │
│  │ ReportGen   → Report generation        │ │
│  │ EmailSender → Email delivery           │ │
│  └────────────────────────────────────────┘ │
├─────────────────────────────────────────────┤
│       SQLAlchemy ORM + SQLite/PostgreSQL    │
└─────────────────────────────────────────────┘
```

### Core Modules (Pluggable)

Each core module has an abstract provider interface + mock implementation for testing.

#### 1. **Importer** (`app/core/importer.py`)

Parses CSV/Excel files and validates:
- Required column: `company_name`
- Optional columns: `vat_number`, `cluster`
- Normalizes whitespace
- Handles multiple clusters (comma-separated)
- Default cluster name: "Default"

**Workflow:**
1. Read file (CSV or Excel)
2. Validate required columns
3. Normalize data (strip whitespace, empty→None)
4. Handle cluster splitting
5. Return list of company dicts

#### 2. **Enricher** (`app/core/enricher.py`)

Automatically discovers company metadata:
- Website URL
- Business sector
- Country code
- Alternative company names
- Data quality status

**Abstract Interface:**
```python
class CompanyEnricherProvider(ABC):
    async def enrich(self, company_name: str, vat_number: str = None) -> Dict:
        # Returns: {website, sector, country, status}
```

**Implementations:**
- `MockCompanyEnricher` — Returns sensible defaults (dev/testing)
- Future: Bing Search API, proprietary data services

#### 3. **NewsSearcher** (`app/core/news_search.py`)

Searches for news about companies.

**Abstract Interface:**
```python
class NewsSearchProvider(ABC):
    async def search(self, query: str, website: str = "", limit: int = 10) -> List[Dict]:
        # Returns: [{title, url, source, published_date, summary}, ...]
```

**Implementations:**
- `MockNewsSearcher` — Returns sample articles (dev/testing)
- Future: Bing Search API, SerpAPI, GDELT, RSS feeds

#### 4. **Classifier** (`app/core/classifier.py`)

AI-powered news classification.

**Abstract Interface:**
```python
class NewsClassifierProvider(ABC):
    async def classify(self, title: str, summary: str, company_name: str) -> Dict:
        # Returns: {
        #   category: str,
        #   relevance_score: 1-10,
        #   urgency_score: 1-10,
        #   commercial_score: 1-10,
        #   risk_score: 1-10,
        #   confidence_score: 1-10
        # }
```

**Implementations:**
- `MockNewsClassifier` — Simple keyword matching (dev/testing)
- Future: Claude API, OpenAI GPT-4

#### 5. **ReportGenerator** (`app/core/report_generator.py`)

Generates HTML and plain-text email reports.

**Features:**
- Filters news by cluster's `min_relevance_score`
- Sorts by relevance/urgency
- Color-coded impact levels (HTML)
- Includes source links and summaries
- Generates email subject and body

#### 6. **EmailDelivery** (`app/core/email_delivery.py`)

Sends reports to cluster recipients.

**Abstract Interface:**
```python
class EmailProvider(ABC):
    async def send(self, to_emails: List[str], subject: str, body_text: str, body_html: str) -> bool:
```

**Implementations:**
- `MockEmailProvider` — Prints to console (dev/testing)
- `SMTPEmailProvider` — Real SMTP (production)
- Future: Microsoft Graph, SendGrid, AWS SES

---

## API Endpoints

### Companies
- `POST /api/companies/` — Create
- `GET /api/companies/` — List (with status filter)
- `GET /api/companies/{id}` — Retrieve
- `PUT /api/companies/{id}` — Update
- `DELETE /api/companies/{id}` — Delete

### Clusters
- `POST /api/clusters/` — Create
- `GET /api/clusters/` — List
- `GET /api/clusters/{id}` — Retrieve
- `PUT /api/clusters/{id}` — Update
- `DELETE /api/clusters/{id}` — Delete
- `POST /api/clusters/{id}/companies/{company_id}` — Add company
- `DELETE /api/clusters/{id}/companies/{company_id}` — Remove company
- `POST /api/clusters/{id}/recipients` — Add email recipient
- `DELETE /api/clusters/{id}/recipients/{recipient_id}` — Remove recipient

### News
- `POST /api/news/` — Create
- `GET /api/news/{id}` — Retrieve
- `GET /api/news/company/{company_id}` — List by company
- `GET /api/news/status/{status}` — Filter by status
- `PUT /api/news/{id}` — Update
- `POST /api/news/{id}/approve` — Approve for reporting
- `POST /api/news/{id}/reject` — Reject
- `DELETE /api/news/{id}` — Delete

### Reports
- `POST /api/reports/` — Create
- `GET /api/reports/{id}` — Retrieve
- `GET /api/reports/cluster/{cluster_id}` — List by cluster
- `PUT /api/reports/{id}` — Update
- `DELETE /api/reports/{id}` — Delete
- `POST /api/reports/cluster/{cluster_id}/generate` — Auto-generate from news
- `POST /api/reports/{id}/send` — Send to recipients

### Import
- `POST /api/import/companies/csv` — Import from CSV
- `POST /api/import/companies/excel` — Import from Excel

---

## Data Flow

### 1. Company Import

```
CSV/Excel File
    ↓
Importer (validate + normalize)
    ↓
CompanyService.create_company()
    ↓
Company + Cluster associations created
    ↓
Status: "needs_review" (if no VAT) or "active"
```

### 2. Data Enrichment

```
Company (needs enrichment)
    ↓
Enricher.enrich(company_name, vat_number)
    ↓
Mock: Return sensible defaults
Real: Call web search API
    ↓
Update company fields: website, sector, country
```

### 3. News Monitoring

```
Company in cluster
    ↓
NewsSearcher.search(company_name, website)
    ↓
Mock: Return sample articles
Real: Call Bing/SerpAPI
    ↓
NewsService.create_news() for each result
    ↓
NewsItem status: "new"
```

### 4. Classification

```
NewsItem (status: "new")
    ↓
Classifier.classify(title, summary, company_name)
    ↓
Mock: Keyword matching
Real: Claude/OpenAI API
    ↓
Set scores: relevance, urgency, commercial, risk, confidence
    ↓
Determine status:
  - confidence_score ≥ threshold → "approved"
  - confidence_score < threshold → "needs_review"
```

### 5. Report Generation

```
Cluster selected
    ↓
Get all companies in cluster
    ↓
Get approved news items for those companies (period: last N days)
    ↓
Filter by min_relevance_score
    ↓
ReportGenerator.generate_report()
    ↓
Create Report (status: "draft")
    ↓
Optionally review and send
```

### 6. Email Delivery

```
Report (status: "draft" → "ready")
    ↓
EmailDelivery.send(recipients, subject, html, text)
    ↓
Mock: Print to console
Real: SMTP or Microsoft Graph
    ↓
Update Report status: "sent"
    ↓
Record sent_at timestamp
```

---

## Configuration

### Environment Variables (.env)

```env
# Database
DATABASE_URL=sqlite:///./customer_intelligence.db
# or: postgresql://user:pass@host:5432/db

# Email SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@company.local

# News Search Provider
NEWS_SEARCH_PROVIDER=mock  # or: bing, serp
NEWS_SEARCH_API_KEY=your-key

# AI Classification Provider
AI_PROVIDER=mock  # or: claude, openai
AI_API_KEY=your-key
```

---

## Deployment Targets

### Development
- SQLite database (in-memory or file)
- Mock providers for all external APIs
- FastAPI with `--reload`
- CORS from localhost:3000

### Production
- PostgreSQL database
- Real integrations: Bing Search, Claude API, SMTP/Graph
- Uvicorn behind reverse proxy (nginx)
- Scheduled jobs (APScheduler) for daily monitoring
- Logging and monitoring
- Docker containerization

---

## Module Dependencies

```
app/
├── core/
│   ├── importer.py       → pandas
│   ├── enricher.py       → (depends on provider)
│   ├── news_search.py    → (depends on provider)
│   ├── classifier.py     → (depends on provider)
│   ├── report_generator.py → (no external deps)
│   └── email_delivery.py → smtplib / (depends on provider)
├── models/
│   └── (all depend on sqlalchemy)
├── services/
│   └── (depend on models + sqlalchemy)
├── routers/
│   └── (depend on services + fastapi)
└── database.py           → sqlalchemy
```

---

## Testing Strategy

### Unit Tests
- Import parsing (CSV normalization, validation)
- Classifier keyword matching
- Report generation (HTML/text)

### Integration Tests
- End-to-end workflows (import → enrich → news → classify → report → send)
- Database operations (CRUD)
- API endpoints

### Test Database
- In-memory SQLite (`:memory:`)
- Fixtures for companies, clusters, news items

### Test Coverage
- Importers: CSV/Excel parsing edge cases
- Services: CRUD operations
- Routers: API contract validation

---

## Future Enhancements

### Short-term
1. Real news search (Bing Search API)
2. Claude API integration for classification
3. Web dashboard (React frontend)
4. User authentication (JWT)
5. APScheduler for automated monitoring

### Medium-term
1. PostgreSQL migration
2. Role-based access control (RBAC)
3. Webhook integrations (Slack, Teams)
4. Topic filtering and saved searches
5. Duplicate detection (content hashing)

### Long-term
1. Machine learning model for better classification
2. Multi-language support
3. Advanced analytics and trending
4. API webhooks for third-party integrations
5. Mobile app
