# Financial Market Data Pipeline
### Production-Grade ETL | AWS ECS + Fargate | Supabase | Apache Airflow | Docker

---

## Overview

A fully automated, cloud-deployed financial data pipeline that ingests end-of-day stock prices for a configurable watchlist of equities, transforms and validates the data through a Bronze → Silver → Gold architecture, and loads it into a cloud Postgres database — every day at 6am Eastern, without a laptop running.

This project was built to simulate the kind of pipeline a data engineer would maintain at a hedge fund or financial institution. The business requirements driving it:

**Trading Team Needs:**
- What was the closing price of each stock yesterday?
- How has each stock trended over the last 30 days?
- Which stocks moved more than 2% yesterday?
- What were the weekly highs and lows?

**Data Engineering Team Needs:**
- When did this pipeline last run successfully?
- Did we get data for every stock on our watchlist?
- If a stock is missing, which API call failed and why?

---

## Architecture

```
Alpha Vantage API
        │
        ▼
   [ EXTRACT ]
   Bronze Layer (raw JSON)
        │
        ▼
   [ TRANSFORM ]
   Silver Layer (cleaned CSV)
        │
        ▼
     [ LOAD ]
   Gold Layer → Supabase (cloud Postgres)
        
Orchestration:
  Local:  Apache Airflow (Docker Compose)
  Cloud:  AWS EventBridge Scheduler → ECS Fargate Task
```

**Cloud Infrastructure:**
| Service | Purpose |
|---|---|
| AWS ECR | Stores Docker image |
| AWS ECS Fargate | Runs container on demand (serverless) |
| AWS EventBridge Scheduler | Triggers pipeline daily at 6am ET |
| AWS CloudWatch | Captures logs from every run |
| Supabase | Cloud Postgres — Gold layer storage |

---

## Tech Stack

- **Language:** Python 3.11
- **Data:** pandas, SQLAlchemy, psycopg2
- **API:** Alpha Vantage (TIME_SERIES_DAILY)
- **Database:** PostgreSQL via Supabase (cloud-hosted on AWS)
- **Orchestration:** Apache Airflow (local), AWS EventBridge (cloud)
- **Containerization:** Docker, Docker Compose
- **Cloud:** AWS ECR, ECS Fargate, EventBridge Scheduler, CloudWatch
- **Logging:** Python logging → stdout + file

---

## Data Pipeline Layers

### Bronze (Raw)
Raw JSON responses from Alpha Vantage stored as-is. No transformation. Preserves source data exactly as received so any reprocessing can happen without hitting the API again.

### Silver (Cleaned)
Validated and typed CSV output. Transformations applied:
- Column renaming (Alpha Vantage prefixes removed)
- Date parsing and formatting
- Numeric type casting (float for prices, int for volume)
- Per-ticker error handling — one bad ticker doesn't kill the pipeline
- Rate limit detection — API error responses are caught and logged before saving

### Gold (Production)
Loaded into Supabase via SQLAlchemy upsert. Schema:

```sql
CREATE TABLE market_statistics (
    symbol       VARCHAR(50)    NOT NULL,
    market_date  DATE           NOT NULL,
    open         NUMERIC(12, 4) NOT NULL,
    high         NUMERIC(12, 4) NOT NULL,
    low          NUMERIC(12, 4) NOT NULL,
    close        NUMERIC(12, 4) NOT NULL,
    volume       INT            NOT NULL,
    PRIMARY KEY (symbol, market_date)
);
```

`NUMERIC(12, 4)` used for all price columns — never `FLOAT` — to preserve exact financial precision.

Idempotent upserts via `ON CONFLICT DO UPDATE` mean the pipeline can run multiple times without creating duplicates.

---

## Key Engineering Decisions

**Why ECS Fargate + EventBridge instead of AWS MWAA (managed Airflow)?**
AWS MWAA starts at ~$300/month — appropriate for enterprise teams with complex multi-DAG workflows, not a daily single-pipeline job. ECS Fargate runs the container only when triggered, costing cents per run. For a linear ETL that runs once daily, EventBridge + ECS is cleaner and more cost-effective.

**Why Supabase instead of RDS?**
Supabase provides a managed Postgres instance with a generous free tier and a familiar connection interface. It runs on AWS infrastructure, making it accessible to any team member without VPN or local setup.

**Why Bronze/Silver/Gold?**
Separating raw, cleaned, and production data means:
- Raw data is always preserved for reprocessing
- Transformation logic can be updated without re-hitting the API
- The Gold layer is always query-ready and trustworthy

**Why NUMERIC instead of FLOAT?**
Floating point arithmetic introduces precision errors unacceptable in financial data. `NUMERIC(12, 4)` guarantees exact decimal representation.

---

## Data Quality Checks

After every load, the pipeline queries the database to verify:
- Every ticker in the watchlist has data
- No ticker was silently skipped
- Row counts are logged per symbol

```python
SELECT symbol, COUNT(*) FROM market_statistics GROUP BY symbol
```

If a ticker is missing from results entirely, a warning is logged — catching failures that wouldn't appear in a simple row count.

---

## Error Handling

- **Per-ticker isolation:** If one ticker fails during extract or transform, remaining tickers continue
- **Rate limit detection:** Alpha Vantage error responses are detected before saving to Bronze
- **Fail-fast orchestration:** If extract fails, transform and load do not run
- **Structured logging:** Every step logs to both stdout (captured by CloudWatch) and a local file
- **Raise on failure:** Outer exceptions re-raise so the orchestrator knows the pipeline failed

---

## Running Locally

**Prerequisites:** Docker Desktop, Python 3.11+

```bash
# Clone the repo
git clone https://github.com/efedincaslan/etl_pipeline_financial_tickers_final
cd Finance_2.0

# Set up environment
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Fill in: apikey, connection_string, FERNET_KEY

# Run the pipeline
python dags/main.py

# Run with Airflow (local)
docker compose up airflow-init
docker compose up
# Access UI at http://localhost:8080 (user: airflow / pass: airflow)
```

---

## Deploying to AWS

```bash
# Authenticate Docker to ECR
(Get-ECRLoginCommand).Password | docker login --username AWS --password-stdin <your-ecr-url>

# Build and push
docker build -t finance-pipeline .
docker tag finance-pipeline:latest <your-ecr-url>/finance-etl-pipeline:latest
docker push <your-ecr-url>/finance-etl-pipeline:latest
```

ECS Task Definition and EventBridge schedule are already configured. New image is picked up automatically on next scheduled run.

---

## Project Structure

```
Finance_2.0/
├── dags/
│   ├── extract.py              # Bronze layer — API ingestion
│   ├── transform.py            # Silver layer — cleaning & validation
│   ├── load.py                 # Gold layer — Supabase upsert
│   ├── main.py                 # Orchestrator + data quality checks
│   ├── database.py             # Shared SQLAlchemy engine
│   ├── tickers.py              # Stock watchlist
│   └── finance_pipeline_dag.py # Airflow DAG definition
├── dockerfile                  # Container definition
├── docker-compose.yaml         # Airflow local setup
├── requirements.txt
├── .env                        # Never committed
├── .gitignore
└── .dockerignore
```

---

## What's Next

- **CI/CD:** GitHub Actions to automatically rebuild and push Docker image to ECR on every push to main
- **AWS Secrets Manager:** Replace plain-text environment variables in ECS task definition with encrypted secrets
- **S3 Bronze Layer:** Move raw JSON storage from local filesystem to S3 for true cloud-native architecture
- **Data Quality Framework:** Integrate Great Expectations for schema validation and anomaly detection
- **Alerting:** SNS email notifications on pipeline failure

---

## Author

Efe Dincaslan — incoming Data Engineer, Fidelity Investments (LEAP Program)  
Virginia Tech, Business Information Technology (Cybersecurity + Analytics)

---

*Built as a learning project to simulate production data engineering patterns before starting at Fidelity. Every architectural decision was made deliberately — not just to get it working, but to understand why.*
