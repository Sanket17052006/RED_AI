"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
from dotenv import load_dotenv
import os

from app.api.endpoints import router as api_router
from app.core.database import db
from app.util.logger import setup_logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

app = FastAPI(
    title="RED AI - Agentic AI Builder with Genetic Evolution System",
    description="Build, deploy, and evolve autonomous AI agents using genetic algorithms",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files for frontend (before API routes to avoid conflicts)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    # Serve CSS, JS, and other static assets at root level
    @app.get("/style.css")
    async def serve_css():
        css_path = os.path.join(frontend_path, "style.css")
        if os.path.exists(css_path):
            return FileResponse(css_path, media_type="text/css")
        return {"error": "CSS not found"}
    
    @app.get("/script.js")
    async def serve_js():
        js_path = os.path.join(frontend_path, "script.js")
        if os.path.exists(js_path):
            return FileResponse(js_path, media_type="application/javascript")
        return {"error": "JS not found"}
    
    @app.get("/dashboard")
    async def serve_dashboard():
        """Serve the frontend dashboard"""
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend not found"}
    
    @app.get("/index.html")
    async def serve_index():
        """Serve the frontend index.html"""
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend not found"}

# Include API routes (no prefix to match original structure)
app.include_router(api_router)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("RED AI - Agentic AI Builder with Genetic Evolution System starting up...")
    
    # Load all agents from database
    agents = db.get_all_agents()
    from app.core.agent import agent_registry
    from app.core.tools import tools
    
    for agent_data in agents:
        try:
            from app.core.agent import AgenticAgent
            agent = AgenticAgent(
                agent_id=agent_data['agent_id'],
                name=agent_data['name'],
                system_prompt=agent_data['system_prompt'],
                tools=tools,
                temperature=agent_data['temperature']
            )
            agent_registry[agent.agent_id] = agent
            logger.info(f"Loaded agent from database: {agent.agent_id}")
        except Exception as e:
            logger.error(f"Failed to load agent {agent_data['agent_id']}: {e}")
    
    logger.info(f"System started. Loaded {len(agent_registry)} agents from database")

# Health check endpoint
@app.get("/")
async def health():
    """Health check endpoint"""
    agents = db.get_all_agents()
    from app.core.tools import tools
    return {
        "status": "RED AI - Agentic AI Builder Running",
        "system": "RED AI - Agentic AI Builder with Genetic Evolution System",
        "version": "2.0.0",
        "agents_registered": len(agents),
        "tools_available": len(tools),
        "framework": "FastAPI + LangChain + SQLite",
        "persistent_storage": True,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")