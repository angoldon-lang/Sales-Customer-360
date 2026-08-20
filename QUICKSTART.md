# Quick Start Guide

## 🚀 Local Development Setup

### Prerequisites
- Docker & Docker Compose
- Git
- Python 3.11+ (for local backend development)
- Node 18+ (for frontend development)

### Start with Docker Compose

```bash
# Clone and enter directory
git clone https://github.com/angoldon-lang/Sales-Customer-360
cd Sales-Customer-360
git checkout claude/data-quality-catalog-permissions-8v3r33

# Start all services (PostgreSQL, FastAPI, React)
docker-compose up -d

# Wait for services to be healthy (~30s)
docker-compose ps

# Access:
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs (Swagger UI)
# - Frontend: http://localhost:3000
# - PostgreSQL: localhost:5432
```

### Seed Database with Sample Data

```bash
# Option 1: Run inside Docker container
docker exec sales-customer-360-api python seed.py

# Option 2: Run locally (if Python env is set up)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py
```

### Test Accounts

After seeding, use these test users:

| Username          | Role            | BU              | Password      |
|-------------------|-----------------|-----------------|---------------|
| mario_rossi       | Sales           | Security        | password123   |
| lucia_bianchi     | Sales           | Cloud           | password123   |
| anna_marini       | Sales Manager   | Security        | password123   |
| carlo_romano      | BU Manager      | Security        | password123   |
| stefano_ferrara   | Executive       | —               | password123   |
| admin             | Admin           | —               | password123   |

---

## 📱 Using the Application

### 1. Login

**API Login** (get JWT token):
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "mario_rossi", "password": "password123"}'

# Returns:
# {
#   "access_token": "eyJhbGc...",
#   "token_type": "bearer",
#   "user": {
#     "id": 1,
#     "username": "mario_rossi",
#     "role": "sales",
#     "business_unit": "Security"
#   }
# }
```

**Frontend**: Use http://localhost:3000 (login will be added in next phase)

---

### 2. Import Data

**Upload CSV file** with customer/product data:

```bash
curl -X POST http://localhost:8000/api/import/csv \
  -F "file=@sample_import.csv" \
  -H "Authorization: Bearer <YOUR_TOKEN>"

# Expected CSV format:
# customer_name, product, vendor, amount, sale_date, contract_expiry, source_document
# Acme Corp, Fortinet Firewall, Fortinet, 15000, 2023-06-15, 2026-06-15, Invoice-001
```

Or use the **Frontend** (http://localhost:3000/import):
- Download template
- Fill in data
- Upload CSV
- Confirm results

---

### 3. Validate Data Quality

**Via Frontend** (http://localhost:3000/data-quality):
1. See tasks in "To Validate" tab
2. Click task to edit
3. Correct customer/product/vendor names
4. Click "Validate" button

**Via API**:
```bash
curl -X GET http://localhost:8000/api/data-quality/tasks?status=to_validate \
  -H "Authorization: Bearer <YOUR_TOKEN>"

curl -X PUT http://localhost:8000/api/data-quality/tasks/1 \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "validated",
    "corrected_customer": "Acme Corporation",
    "corrected_product": "Fortinet FortiGate 500E",
    "validation_notes": "Confirmed with invoice"
  }'
```

---

### 4. Run Conversion Engine

Generate service proposals automatically:

```bash
# Run for all customers
curl -X POST http://localhost:8000/api/conversion/run \
  -H "Authorization: Bearer <YOUR_TOKEN>"

# Run for specific customer
curl -X POST "http://localhost:8000/api/conversion/run?customer_id=1" \
  -H "Authorization: Bearer <YOUR_TOKEN>"

# Get stats
curl -X GET http://localhost:8000/api/conversion/stats \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

---

### 5. View Opportunities

**Via API**:
```bash
# List opportunities
curl -X GET http://localhost:8000/api/opportunities?status=new \
  -H "Authorization: Bearer <YOUR_TOKEN>"

# Accept opportunity
curl -X PUT http://localhost:8000/api/opportunities/1 \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"status": "accepted", "notes": "Will present to customer next week"}'
```

---

## 🔧 Local Development (Without Docker)

### Backend

```bash
cd backend

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Edit .env with your database URL

# Run migrations (when available)
# alembic upgrade head

# Start development server
uvicorn app.main:app --reload

# Run tests
pytest

# Access API docs: http://localhost:8000/docs
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure .env
cp .env.example .env
# Edit .env if needed

# Start development server
npm start

# Access: http://localhost:3000
# HMR (Hot Module Reload) enabled by default
```

---

## 📊 Sample Seed Data

The seed script creates:

**Users** (6 test accounts with different roles)
- Sales reps with assigned customers
- Sales manager
- BU managers
- Executive
- Admin

**Products** (8 products from major vendors)
- Fortinet FortiGate 500E
- Palo Alto PA-5220
- Microsoft 365 E5
- Veeam Backup
- SolarWinds Orion
- VMware vSphere
- Nutanix Cloud
- Redgate SQL Tools

**Services** (6 managed services)
- Managed Firewall
- Managed Modern Workplace
- Backup Managed Service
- Monitoring as a Service
- Infrastructure Managed Service
- DBA as a Service

**Customers** (5 test customers)
- Acme Corporation (IT company)
- Tech Solutions Ltd (UK tech)
- Global Industries (Manufacturing)
- Prime Consulting (Italy)
- Digital Ventures (Startup)

**Contracts** (5 active contracts)
- Various products linked to customers
- Auto-renewal enabled
- Mixed end dates

**Conversion Rules** (4 active rules)
- Fortinet Firewall → Managed Firewall
- Microsoft 365 → Managed Workplace
- Veeam Backup → Backup Service
- SolarWinds → Monitoring Service

---

## 🔐 API Authentication

All endpoints except `/auth/login` and `/auth/register` require JWT token:

```bash
# Include in header:
Authorization: Bearer <YOUR_ACCESS_TOKEN>
```

Token expires in 30 minutes (configurable in `.env`).

---

## 📝 API Endpoints Reference

### Authentication
- `POST /api/auth/login` — Get access token
- `POST /api/auth/register` — Create new user
- `GET /api/auth/me` — Current user info

### Data Quality
- `GET /api/data-quality/tasks` — List tasks
- `GET /api/data-quality/tasks/{id}` — Task details
- `PUT /api/data-quality/tasks/{id}` — Update task
- `GET /api/data-quality/dashboard/stats` — Stats

### Import
- `POST /api/import/csv` — Upload CSV
- `POST /api/import/bulk-assign-customer` — Assign customer
- `GET /api/import/suggest-customers` — Fuzzy matching
- `GET /api/import/stats` — Import stats

### Conversion Engine
- `GET /api/conversion/rules` — List rules
- `POST /api/conversion/rules` — Create rule
- `POST /api/conversion/run` — Execute engine
- `GET /api/conversion/stats` — Stats
- `GET /api/conversion/logs` — History

### Customers
- `GET /api/customers` — List
- `GET /api/customers/{id}` — Details
- `POST /api/customers` — Create

### Services
- `GET /api/services` — List
- `GET /api/services/{id}` — Details
- `POST /api/services` — Create
- `GET /api/services/categories/list` — Categories

### Opportunities
- `GET /api/opportunities` — List
- `GET /api/opportunities/{id}` — Details
- `POST /api/opportunities` — Create
- `PUT /api/opportunities/{id}` — Update status

---

## 🐛 Troubleshooting

### Ports Already in Use

```bash
# Find process using port
lsof -i :5432   # PostgreSQL
lsof -i :8000   # FastAPI
lsof -i :3000   # React

# Kill process (Linux/Mac)
kill -9 <PID>

# Or change ports in docker-compose.yml
```

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Reset database
docker-compose down -v  # Remove volumes
docker-compose up -d
```

### React Build Errors

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### CORS Errors

Check `backend/app/config.py` CORS settings match frontend URL.

---

## 📚 Documentation

- **ARCHITECTURE.md** — Full system design, database schema, permission matrix
- **README.md** — Project overview, modules, technologies
- **API Docs** — Auto-generated at http://localhost:8000/docs (Swagger UI)

---

## 🎯 Next Steps

1. ✅ **Local Setup** — Run `docker-compose up -d` + seed data
2. **Frontend Login** — Add JWT authentication to React
3. **Testing** — Create pytest + Jest test suites
4. **CI/CD** — GitHub Actions for automated testing
5. **Database Migrations** — Setup Alembic for schema changes
6. **Deployment** — Docker images for production (Cloud Run, ECS, K8s)
7. **Notifications** — Email alerts for contract renewals
8. **Audit Log** — Track data modifications for compliance

---

## 📞 Support

For issues or questions:
1. Check API docs: http://localhost:8000/docs
2. Review ARCHITECTURE.md
3. Check container logs: `docker-compose logs -f <service>`
4. Look at seed.py for example data structure
