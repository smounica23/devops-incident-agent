# DevOps Incident Response Agent

An end-to-end agentic AI system that automatically investigates production incidents, identifies root causes, generates fixes, and creates PRs — with human approval via Microsoft Teams.

## Demo

[Add demo video link here]

## Architecture

[Add architecture diagram here]

## How It Works

1. PagerDuty/CloudWatch webhook hits FastAPI
2. Alert dispatched to Celery priority queue (P1/P2/P3)
3. LangGraph runs 15-node investigation pipeline
4. Agent queries ELK logs, identifies root cause via Claude API
5. Agent generates fix, creates GitHub branch + PR
6. Teams notification sent for human approval
7. On approval — PR merged, Confluence page created, Teams notified

## Tech Stack

- **Orchestration:** LangGraph (15-node StateGraph)
- **LLM:** Claude API (claude-sonnet-4-5)
- **Task Queue:** Celery + Redis (P1/P2/P3 priority queues)
- **Logs:** Elasticsearch + Kibana + Logstash
- **Code:** PyGithub (branch, commit, PR creation)
- **Documentation:** Atlassian REST API (Confluence)
- **Notifications:** Microsoft Teams webhook
- **Observability:** LangSmith
- **API:** FastAPI
- **Database:** PostgreSQL
- **Infra:** Docker Compose

## Setup

### Prerequisites
- Docker Desktop
- Python 3.11+
- GitHub account
- Atlassian account (Confluence)
- Anthropic API key

### Installation

```bash
git clone https://github.com/smounica23/devops-incident-agent
cd devops-incident-agent
cp .env.example .env
# Fill in your API keys in .env
docker compose up --build -d
python simulator/log_simulator.py
```

### Send a test alert

```bash
curl -X POST http://localhost:8000/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "alertName": "PaymentServiceDown",
    "severity": "critical",
    "affected_service": "payment-service",
    "environment": "production",
    "error_message": "NullPointerException in PaymentValidator.java:47"
  }'
```

### Approve the fix

```bash
curl -X POST http://localhost:8000/api/v1/incidents/{incident_id}/approve
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/alerts | Receive production alert |
| GET | /api/v1/incidents/{id} | Get incident status |
| POST | /api/v1/incidents/{id}/approve | Approve fix |
| POST | /api/v1/incidents/{id}/reject | Reject fix |

## LangGraph Pipeline

alert_intake → log_investigation → metrics_investigation →
trace_investigation → deployment_investigation → pr_commit_analysis →
root_cause_reasoning → fix_planner → code_fix → branch_and_pr →
human_approval → merge → confluence_documentation → teams_notification


## Key Features

## Incident Scenarios

| Scenario | Error | Root Cause | Fix |
|----------|-------|------------|-----|
| NullPointerException | 500 errors on /payments | Null checks removed in PR #142 | Restore null checks in PaymentValidator.java:47 |
| DB Connection Pool | Connection pool exhausted | No connection pooling config | Restore pool_size=10 |
| Request Timeout | 504 on all endpoints | No timeout configured | Add timeout configuration |

## Concurrency

Supports up to 5 concurrent incidents with priority routing:
- P1 → 3 dedicated workers (15 min HITL timeout)
- P2 → 2 dedicated workers (30 min HITL timeout)  
- P3 → 1 worker (2 hr HITL timeout)

## Production vs Portfolio

| Component | Portfolio | Production |
|-----------|-----------|------------|
| ELK | Docker Compose | AWS OpenSearch |
| GitHub | PyGithub | GitHub Enterprise MCP |
| Secrets | .env file | AWS Secrets Manager |
| Workers | Docker containers | Kubernetes pods |
| Database | PostgreSQL Docker | AWS RDS |

## Screenshots

### LangSmith Trace
![LangSmith Trace](docs/langsmith-trace.png)

### GitHub PR
![GitHub PR](docs/github-pr.png)

### Teams Notification
![Teams Notification](docs/teams-notification.png)

### Kibana Dashboard
![Kibana Dashboard](docs/kibana-dashboard.png)

- **Priority queues** — P1/P2/P3 incidents processed separately
- **Real ELK queries** — actual log analysis, not mocks
- **Claude-powered root cause** — 0.95 confidence scoring
- **Auto PR creation** — real GitHub branch + commit + PR
- **Human-in-the-loop** — Teams approval before merge
- **Full observability** — LangSmith traces every node