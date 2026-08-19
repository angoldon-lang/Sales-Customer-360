# Sales Customer 360 & Service Conversion Portal

Un portale integrato per la gestione clienti, normalizzazione dati commerciali, catalogo servizi e motore di proposte di conversione.

## Visione

Il sistema trasforma dati commerciali disordinati in opportunità ricorrenti di servizio attraverso:
1. **Data Quality Module** — bonifica manuale + validazione
2. **Service Catalog** — catalogo centralizzato di servizi
3. **Conversion Engine** — suggerimenti automatici licenze → servizi
4. **Permission Model** — RBAC granulare per sales, manager, BU, direzione, admin

## Stack Tecnico

- **Backend**: Python + FastAPI + SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: React + Tailwind CSS
- **Containerization**: Docker + Docker Compose

## Struttura del Progetto

```
Sales-Customer-360/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── routers/         # API endpoints
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── crud/            # Database operations
│   │   ├── main.py          # FastAPI app
│   │   ├── database.py      # DB connection
│   │   └── config.py        # Configuration
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API client
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── ARCHITECTURE.md
```

## Setup Rapido

### Con Docker Compose (Consigliato)

```bash
docker-compose up -d
```

- API: http://localhost:8000
- Frontend: http://localhost:3000
- Docs API: http://localhost:8000/docs
- Database: postgres://user:password@localhost:5432/sales_customer_360

### Setup Locale

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup .env
cp .env.example .env

# Database (PostgreSQL deve essere in esecuzione)
# Poi avvia il server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

## Moduli Principali

### 1. Data Quality Module (`/api/data-quality`)

Coda di bonifica dati con validazione sales/admin.

**Endpoints**:
- `GET /tasks` — lista attività data quality
- `POST /tasks` — crea nuovo task
- `PUT /tasks/{id}` — aggiorna e valida
- `GET /dashboard/stats` — statistiche bonifica

**Stati**: `to_validate`, `validated`, `doubtful`, `discarded`

### 2. Service Catalog (`/api/services`)

Catalogo centralizzato di servizi disponibili.

**Endpoints**:
- `GET /` — lista servizi
- `GET /{id}` — dettagli servizio
- `POST /` — crea servizio
- `GET /categories/list` — categorie

### 3. Opportunities (`/api/opportunities`)

Motore di proposte commerciali automatiche.

**Endpoints**:
- `GET /` — lista opportunità
- `POST /` — crea opportunità
- `PUT /{id}` — aggiorna stato

**Stati**: `new`, `evaluating`, `accepted`, `rejected`, `already_covered`, `postponed`

### 4. Customers (`/api/customers`)

Gestione clienti e account.

**Endpoints**:
- `GET /` — lista clienti
- `POST /` — crea cliente
- `GET /{id}` — dettagli cliente

## Permessi e Ruoli

| Ruolo         | Visibilità                    | Azioni                           |
|---------------|-------------------------------|----------------------------------|
| Sales         | Clienti assegnati             | Modifica dati propri clienti     |
| Sales Manager | Clienti team                  | Valida dati, riassegna clienti   |
| BU Manager    | Clienti/opp BU                | Gestisce catalogo servizi BU     |
| Direzione     | Tutti clienti                 | Vista KPI, pipeline, rinnovi     |
| Admin         | Tutto                         | Utenti, permessi, configurazioni |
| Data Steward  | Tutti o per area              | Bonifica massiva, deduplica      |

## Prossimi Step

1. ✅ Struttura database e models
2. ✅ API skeleton
3. ⏳ Frontend pagine principali
4. ⏳ Conversion Engine regole
5. ⏳ Permission middleware
6. ⏳ Autenticazione JWT
7. ⏳ Import dati (Excel/API)
8. ⏳ Dashboard KPI

## Documentazione

Vedi `ARCHITECTURE.md` per dettagli architetturali.
