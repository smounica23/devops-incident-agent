from fastapi import FastAPI


app = FastAPI(
    title="DevOps Incident Response Agent",
    description="Agentic AI system for automated incident investigation",
    version="0.1.0"
)


@app.get("/health")
async def get_health():
    return {
        "status" : "OK",
        "service" : "devops-incident-agent"
        }

@app.get("/")
async def root():
    return {
        "message": "DevOps Incident Response Agent is running"
    }