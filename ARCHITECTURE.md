# Architettura: Sales Customer 360 & Service Conversion Portal

## Visione Strategica

Trasformare dati commerciali disordinati in opportunità ricorrenti di servizio mediante:
1. **Normalizzazione controllata** (sales + admin)
2. **Catalogo servizi** (strutturato, modificabile)
3. **Motore di conversione** (regole di proposta automatiche)
4. **Gestione permessi** (RBAC granulare)

---

## Database Schema

### Core Entities

#### `customers`
Cliente master con score di data quality.

| Campo                | Tipo      | Note                          |
|----------------------|-----------|-------------------------------|
| `id`                 | INT PK    | Primary key                   |
| `name`               | VARCHAR   | Nome cliente (modificabile)   |
| `vat_number`         | VARCHAR   | P.IVA/VAT                     |
| `industry`           | VARCHAR   | Settore                       |
| `country`            | VARCHAR   | Paese                         |
| `data_quality_score` | INT       | 0-100, calcolato              |
| `status`             | VARCHAR   | active, inactive              |

**Relazioni**:
- 1:N `customer_contacts` (persone di contatto)
- 1:N `customer_accounts` (account commerciali)
- 1:N `contracts` (contratti)
- 1:N `opportunities` (opportunità)
- 1:N `data_quality_tasks` (task di bonifica)

---

#### `customer_accounts`
Account commerciale per cliente (può avere più account per BU).

| Campo                | Tipo      | Note                                  |
|----------------------|-----------|---------------------------------------|
| `id`                 | INT PK    | Primary key                           |
| `customer_id`        | INT FK    | Cliente                               |
| `name`               | VARCHAR   | Nome account                          |
| `account_owner_id`   | INT FK    | Sales responsabile principale         |
| `co_owner_id`        | INT FK    | Co-owner opzionale                    |
| `business_unit`      | VARCHAR   | BU (Security, Cloud, ecc)             |
| `team`               | VARCHAR   | Team di vendita                       |
| `annual_value`       | INT       | Valore ARR                            |
| `renewal_date`       | DATETIME  | Data prossimo rinnovo                 |
| `metadata`           | JSON      | Dati custom                           |

---

#### `data_quality_tasks`
Coda di bonifica dati con validazione.

| Campo                    | Tipo      | Note                                  |
|--------------------------|-----------|---------------------------------------|
| `id`                     | INT PK    | Primary key                           |
| `customer_id`            | INT FK    | Cliente interessato                   |
| `task_type`              | VARCHAR   | import, manual_entry, ecc             |
| `extracted_customer`     | VARCHAR   | Nome estratto/OCR                     |
| `corrected_customer`     | VARCHAR   | Nome corretto dal sales               |
| `extracted_product`      | VARCHAR   | Prodotto estratto                     |
| `corrected_product`      | VARCHAR   | Prodotto corretto                     |
| `amount`                 | INT       | Importo vendita                       |
| `sale_date`              | DATETIME  | Data vendita                          |
| `contract_expiry_date`   | DATETIME  | Scadenza contratto                    |
| `account_owner_id`       | INT FK    | Sales owner                           |
| `status`                 | ENUM      | to_validate, validated, doubtful, discarded |
| `validated_by_id`        | INT FK    | User che ha validato                  |
| `validated_at`           | DATETIME  | Quando validato                       |
| `validation_notes`       | TEXT      | Note di validazione                   |
| `sales_notes`            | TEXT      | Note del sales                        |

**Stati**:
- `to_validate`: Nuovo, in attesa di review
- `validated`: Confermato, pronto per uso
- `doubtful`: Dubbio, richiede revisione
- `discarded`: Scartato, non rilevante

---

#### `products`
Prodotto/licenza venduta con vendor e categoria.

| Campo           | Tipo      | Note                          |
|-----------------|-----------|-------------------------------|
| `id`            | INT PK    | Primary key                   |
| `category_id`   | INT FK    | Categoria prodotto            |
| `vendor_id`     | INT FK    | Vendor (Fortinet, Microsoft)  |
| `name`          | VARCHAR   | Nome prodotto                 |
| `sku`           | VARCHAR   | SKU univoco                   |
| `license_type`  | VARCHAR   | subscription, perpetual, ecc  |
| `margin_expectation` | INT   | % margine atteso              |

---

#### `services`
Servizio ricorrente nel catalogo aziendale.

| Campo                 | Tipo       | Note                                      |
|-----------------------|------------|-------------------------------------------|
| `id`                  | INT PK     | Primary key                               |
| `name`                | VARCHAR    | Nome servizio (es: Managed Firewall)      |
| `category_id`         | INT FK     | Categoria (Security, Cloud, ecc)          |
| `business_unit`       | VARCHAR    | BU owner (Security, Cloud)                |
| `owner_id`            | INT FK     | Responsabile servizio                     |
| `service_type`        | VARCHAR    | managed, consulting, support              |
| `billing_type`        | VARCHAR    | monthly, annual                           |
| `indicative_price`    | DECIMAL    | Prezzo indicativo                         |
| `price_range_min/max` | DECIMAL    | Range prezzo                              |
| `margin_expectation`  | INT        | % margine atteso (30%-50%)                |
| `is_recommended`      | BOOLEAN    | Spunta se proposta alta priorità          |

**Relazioni**:
- 1:N `service_levels` (Basic, Advanced, Premium)
- M:N `service_product_association` (prodotti che lo trigggerano)

---

#### `service_levels`
Livelli di servizio (SLA, prezzo).

| Campo               | Tipo      | Note                      |
|---------------------|-----------|---------------------------|
| `id`                | INT PK    | Primary key               |
| `service_id`        | INT FK    | Servizio                  |
| `name`              | VARCHAR   | Basic, Advanced, Premium  |
| `sla_response`      | VARCHAR   | Es: 4h, 8h, 24h           |
| `sla_resolution`    | VARCHAR   | Es: 8h, 24h, 48h          |
| `price`             | DECIMAL   | Prezzo questo livello     |

---

#### `opportunities`
Proposta di servizio per cliente.

| Campo              | Tipo      | Note                                      |
|--------------------|-----------|-------------------------------------------|
| `id`               | INT PK    | Primary key                               |
| `customer_id`      | INT FK    | Cliente                                   |
| `product_id`       | INT FK    | Prodotto trigger                          |
| `service_id`       | INT FK    | Servizio proposto                         |
| `account_owner_id` | INT FK    | Sales responsabile                        |
| `title`            | VARCHAR   | Titolo proposta                           |
| `trigger`          | VARCHAR   | Perché proposto (es: firewall senza managed) |
| `motivation`       | TEXT      | Motivazione commerciale                   |
| `priority`         | VARCHAR   | high, medium, low                         |
| `status`           | ENUM      | new, evaluating, accepted, rejected, ecc  |
| `estimated_value`  | DECIMAL   | Valore stimato                            |
| `estimated_margin` | INT       | Margine atteso %                          |
| `notes`            | TEXT      | Note sales                                |

**Stati opportunità**:
- `new`: Suggerito dal motore
- `evaluating`: Sales sta valutando
- `accepted`: Sales l'ha accettato
- `rejected`: Sales l'ha rifiutato
- `already_covered`: Già coperto da altro contratto
- `postponed`: Da riprendere più avanti

---

#### `contracts`
Contratto con cliente (prodotto + servizio).

| Campo             | Tipo      | Note                          |
|-------------------|-----------|-------------------------------|
| `id`              | INT PK    | Primary key                   |
| `customer_id`     | INT FK    | Cliente                       |
| `product_id`      | INT FK    | Prodotto contrattualizzato    |
| `service_id`      | INT FK    | Servizio associato (opzionale) |
| `contract_number` | VARCHAR   | Numero univoco contratto      |
| `start_date`      | DATETIME  | Data inizio                   |
| `end_date`        | DATETIME  | Data fine                     |
| `renewal_date`    | DATETIME  | Data rinnovo previsto         |
| `annual_value`    | DECIMAL   | ARR del contratto             |
| `status`          | VARCHAR   | active, expired, renewing     |

---

#### `users`
Utente del portale con ruolo e permessi.

| Campo           | Tipo      | Note                          |
|-----------------|-----------|-------------------------------|
| `id`            | INT PK    | Primary key                   |
| `username`      | VARCHAR   | Login univoco                 |
| `email`         | VARCHAR   | Email                         |
| `full_name`     | VARCHAR   | Nome completo                 |
| `role_id`       | INT FK    | Ruolo (Sales, Manager, Admin) |
| `business_unit` | VARCHAR   | BU di appartenenza            |
| `team`          | VARCHAR   | Team                          |
| `region`        | VARCHAR   | Area geografica               |
| `is_active`     | BOOLEAN   | Attivo/disattivo              |

---

#### `roles`
Ruoli RBAC.

| Ruolo         | Permessi Tipici                                |
|---------------|------------------------------------------------|
| `sales`       | Vedi clienti assegnati, modifica dati propri  |
| `sales_manager` | Vedi team, valida dati, riassegna account    |
| `bu_manager`  | Vedi BU, gestisce catalogo servizi            |
| `direzione`   | Vedi tutto, KPI, pipeline, rinnovi            |
| `admin`       | Tutto                                          |
| `data_steward` | Bonifica massiva, deduplica, merge clienti   |

---

## API Endpoints

### Data Quality Module

```
GET    /api/data-quality/tasks              — Lista task
POST   /api/data-quality/tasks              — Crea task
GET    /api/data-quality/tasks/{id}         — Dettagli
PUT    /api/data-quality/tasks/{id}         — Aggiorna/valida
GET    /api/data-quality/dashboard/stats    — Statistiche
```

### Service Catalog

```
GET    /api/services                        — Lista servizi
POST   /api/services                        — Crea servizio
GET    /api/services/{id}                   — Dettagli
GET    /api/services/categories/list        — Categorie
```

### Opportunities

```
GET    /api/opportunities                   — Lista
POST   /api/opportunities                   — Crea proposta
GET    /api/opportunities/{id}              — Dettagli
PUT    /api/opportunities/{id}              — Aggiorna stato
```

### Customers

```
GET    /api/customers                       — Lista
POST   /api/customers                       — Crea cliente
GET    /api/customers/{id}                  — Dettagli
```

---

## Flusso: Normalizzazione Dati

```
┌─────────────────────┐
│  Import Documenti   │
│ (Excel, fatture)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Estrazione Auto     │
│ (OCR, parsing)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Data Quality Task  │
│ (stato: to_validate)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Validazione Sales   │
│ (corregge dati)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Stato: validated    │
│ (pronto per uso)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Scheda Cliente      │
│ Aggiornata + KPI    │
└─────────────────────┘
```

---

## Flusso: Conversion Engine

```
┌──────────────────────────────────┐
│ Contratto trovato:               │
│ Cliente X ha firewall Fortinet   │
│ negli ultimi 36 mesi             │
└──────────────────┬───────────────┘
                   │
                   ▼
┌──────────────────────────────────┐
│ Regola trigger:                  │
│ firewall + NO managed service    │
│ → proponi Managed Firewall       │
└──────────────────┬───────────────┘
                   │
                   ▼
┌──────────────────────────────────┐
│ Opportunity creato:              │
│ status: new                      │
│ priority: high                   │
│ estimated_value: € dal catalogo  │
└──────────────────┬───────────────┘
                   │
                   ▼
┌──────────────────────────────────┐
│ Sales valuta:                    │
│ ✓ accetto                        │
│ ✗ non rilevante                  │
│ ⏸ da riprendere più avanti       │
└──────────────────────────────────┘
```

---

## Matrice Permessi

| Risorsa              | Sales | Manager | BU Mgr | Direzione | Admin | Steward |
|----------------------|-------|---------|--------|-----------|-------|---------|
| Clienti propri       | RW    | R       | R      | R         | RW    | R       |
| Clienti team         | —     | RW      | R      | R         | RW    | R       |
| Clienti BU           | —     | —       | RW     | R         | RW    | R       |
| Tutti clienti        | —     | —       | —      | R         | RW    | RW      |
| Data Quality tasks   | RW*   | RW      | —      | —         | RW    | RW      |
| Catalogo servizi     | R     | —       | RW     | —         | RW    | —       |
| Opportunità          | RW*   | RW      | —      | R         | RW    | —       |
| Permessi             | —     | —       | —      | —         | RW    | —       |

**RW***: Solo su propri clienti/account

---

## Tecnologie

- **Linguaggio Backend**: Python 3.11+
- **Framework API**: FastAPI (async, automatic docs)
- **ORM**: SQLAlchemy 2.0+
- **Database**: PostgreSQL 15+
- **Autenticazione**: JWT (python-jose)
- **Frontend**: React 18 + React Router
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Table Component**: TanStack Table (React Table)
- **Containerization**: Docker + Docker Compose

---

## Prossime Implementazioni

1. **Conversion Engine**: Regole configurabili per suggeri automatici
2. **Permission Middleware**: Filtraggio query per visibilità RBAC
3. **JWT Authentication**: Login e token refresh
4. **Data Import**: Excel, CSV, API parsing
5. **Dashboard KPI**: Grafici pipeline, margini, rinnovi
6. **Email Notifications**: Avvisi renewal, nuove opportunità
7. **Audit Log**: Tracciamento modifiche dati sensibili
8. **Search & Filter**: Full-text search clienti, prodotti, servizi

---

## Deployment

```bash
# Local development
docker-compose up -d

# Production (example with environment variables)
docker-compose -f docker-compose.prod.yml up -d
```

Database creato automaticamente, schema via SQLAlchemy migrations (da implementare).
