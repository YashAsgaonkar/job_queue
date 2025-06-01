from fastapi import FastAPI
import uvicorn
from fastapi.staticfiles import StaticFiles
from api.redis_client import redis_client
from api.process_query import router as process_query_router
from api.dashboard import router as dashboard_router
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI()

static_dir = Path(__file__).parent / "static"
app.mount(
    "/api/static",
    StaticFiles(directory=static_dir),
    name="static"
)

if redis_client.ping():
    print("Connected to Redis successfully!")

# Include the process_query router
app.include_router(process_query_router, prefix="/api", tags=["process_query"])
app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])


@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    dashboard_html_path = static_dir / "dashboard.html"
    if not dashboard_html_path.is_file():
        return "<h1>Error: dashboard.html not found!</h1>"
    with open(dashboard_html_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)