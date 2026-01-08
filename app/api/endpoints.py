"""
FastAPI endpoints for the Agentic AI Builder
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List, Dict

from app.api.models import (
    CreateAgentRequest, AgentResponse, ExecuteTaskRequest, ExecuteTaskResponse,
    EvolveAgentsRequest, EvolveAgentsResponse, ChatRequest, ChatResponse
)
from app.core.agent import AgenticAgent, agent_registry
from app.core.evolution import evolution_engine
from app.core.database import db
from app.core.tools import tools
import random
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/agents/create", response_model=AgentResponse)
async def create_agent(request: CreateAgentRequest):
    """Create a new AI agent"""
    try:
        agent_id = f"agent_{random.randint(10000, 99999)}"
        
        logger.info(f"Creating agent: {request.name}")
        
        agent = AgenticAgent(
            agent_id=agent_id,
            name=request.name,
            system_prompt=request.system_prompt,
            tools=tools,
            temperature=request.temperature
        )
        
        memory = db.get_agent_memory(agent_id, limit=1000)
        
        return {
            "agent_id": agent_id,
            "name": agent.name,
            "system_prompt": agent.system_prompt,
            "temperature": agent.temperature,
            "memory_count": len(memory),
            "execution_count": agent.total_tasks,
            "fitness_score": agent.fitness_score,
            "generation": agent.generation,
            "success_rate": (agent.successful_tasks/agent.total_tasks*100 if agent.total_tasks > 0 else 0)
        }
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")

@router.get("/agents", response_model=List[AgentResponse])
async def list_agents():
    """List all registered agents"""
    agents_list = []
    agents_data = db.get_all_agents()
    
    for agent_data in agents_data:
        agent_id = agent_data['agent_id']
        if agent_id not in agent_registry:
            try:
                agent = AgenticAgent(
                    agent_id=agent_id,
                    name=agent_data['name'],
                    system_prompt=agent_data['system_prompt'],
                    tools=tools,
                    temperature=agent_data['temperature']
                )
            except:
                continue
        
        agent = agent_registry.get(agent_id)
        if not agent:
            continue
            
        memory = db.get_agent_memory(agent_id, limit=1000)
        
        agents_list.append({
            "agent_id": agent.agent_id,
            "name": agent.name,
            "system_prompt": agent.system_prompt[:200] + "..." if len(agent.system_prompt) > 200 else agent.system_prompt,
            "temperature": agent.temperature,
            "memory_count": len(memory),
            "execution_count": agent.total_tasks,
            "fitness_score": round(agent.fitness_score, 3),
            "generation": agent.generation,
            "success_rate": round((agent.successful_tasks/agent.total_tasks*100 if agent.total_tasks > 0 else 0), 1)
        })
    
    return agents_list

@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get agent details"""
    if agent_id not in agent_registry:
        agent_data = db.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
        agent = AgenticAgent(
            agent_id=agent_id,
            name=agent_data['name'],
            system_prompt=agent_data['system_prompt'],
            tools=tools,
            temperature=agent_data['temperature']
        )
    
    agent = agent_registry[agent_id]
    memory = db.get_agent_memory(agent_id, limit=1000)
    
    return {
        "agent_id": agent.agent_id,
        "name": agent.name,
        "system_prompt": agent.system_prompt,
        "temperature": agent.temperature,
        "memory_count": len(memory),
        "execution_count": agent.total_tasks,
        "fitness_score": agent.fitness_score,
        "generation": agent.generation,
        "success_rate": round((agent.successful_tasks/agent.total_tasks*100 if agent.total_tasks > 0 else 0), 1)
    }

@router.post("/agents/{agent_id}/execute", response_model=ExecuteTaskResponse)
async def execute_task(agent_id: str, request: ExecuteTaskRequest):
    """Execute a task using an agent"""
    if agent_id not in agent_registry:
        agent_data = db.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
        agent = AgenticAgent(
            agent_id=agent_id,
            name=agent_data['name'],
            system_prompt=agent_data['system_prompt'],
            tools=tools,
            temperature=agent_data['temperature']
        )
    
    agent = agent_registry[agent_id]
    result = await agent.execute(request.task, request.context)
    
    return {
        "result": result.get("result", ""),
        "steps": result.get("steps", []),
        "timestamp": result.get("timestamp", ""),
        "success": result.get("success", False),
        "agent_id": agent_id
    }

@router.get("/agents/{agent_id}/memory")
async def get_agent_memory(agent_id: str):
    """Get agent's memory"""
    if not db.get_agent(agent_id):
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    
    memory = db.get_agent_memory(agent_id, limit=20)
    executions = db.get_execution_history(agent_id, limit=10)
    
    if agent_id in agent_registry:
        agent = agent_registry[agent_id]
        summary = agent.get_memory_summary()
    else:
        summary = f"Agent {agent_id} - Memory entries: {len(memory)}"
    
    return {
        "agent_id": agent_id,
        "memory": memory,
        "execution_history": executions,
        "summary": summary,
        "total_memory_entries": len(memory)
    }

@router.post("/agents/evolve", response_model=EvolveAgentsResponse)
async def evolve_agents(request: EvolveAgentsRequest):
    """Evolve agents using genetic algorithm"""
    try:
        logger.info(f"Starting evolution with {len(request.base_agents)} base agents")
        
        valid_agents = []
        for agent_id in request.base_agents:
            if agent_id in agent_registry:
                valid_agents.append(agent_registry[agent_id])
            else:
                agent_data = db.get_agent(agent_id)
                if agent_data:
                    agent = AgenticAgent(
                        agent_id=agent_id,
                        name=agent_data['name'],
                        system_prompt=agent_data['system_prompt'],
                        tools=tools,
                        temperature=agent_data['temperature']
                    )
                    valid_agents.append(agent)
        
        if not valid_agents:
            raise HTTPException(status_code=400, detail="No valid base agents found")
        
        population = valid_agents[:request.population_size]
        
        while len(population) < request.population_size:
            agent = AgenticAgent(
                agent_id=f"agent_{random.randint(10000, 99999)}",
                name=f"Random_Agent_{len(population)}",
                system_prompt="You are a helpful AI agent. Execute tasks efficiently using available tools when appropriate.",
                tools=tools,
                temperature=random.uniform(0.3, 1.0)
            )
            population.append(agent)
        
        evolution_engine.population_size = request.population_size
        evolution_engine.mutation_rate = request.mutation_rate
        evolution_engine.generation = 0
        
        evolution_history = []
        total_agents_evaluated = 0
        
        for gen in range(request.generations):
            logger.info(f"Generation {gen + 1}/{request.generations}")
            
            for agent in population:
                fitness = await evolution_engine.evaluate_fitness(agent, request.test_tasks)
                total_agents_evaluated += 1
            
            fitness_scores = [a.fitness_score for a in population]
            avg_fitness = sum(fitness_scores) / len(fitness_scores) if fitness_scores else 0
            max_fitness = max(fitness_scores) if fitness_scores else 0
            min_fitness = min(fitness_scores) if fitness_scores else 0
            
            best_agent = max(population, key=lambda x: x.fitness_score) if population else None
            
            evolution_history.append({
                "generation": gen + 1,
                "avg_fitness": round(avg_fitness, 3),
                "max_fitness": round(max_fitness, 3),
                "min_fitness": round(min_fitness, 3),
                "best_agent_id": best_agent.agent_id if best_agent else None,
                "best_agent_name": best_agent.name if best_agent else None,
                "population_size": len(population)
            })
            
            if gen < request.generations - 1 and len(population) >= 2:
                population = await evolution_engine.evolve(population, request.test_tasks)
        
        if not population:
            raise HTTPException(status_code=500, detail="Evolution failed")
        
        best_agent = max(population, key=lambda x: x.fitness_score)
        memory = db.get_agent_memory(best_agent.agent_id, limit=1000)
        
        final_fitness_scores = [a.fitness_score for a in population]
        
        logger.info(f"Evolution completed. Best agent: {best_agent.agent_id}")
        
        return {
            "best_agent": {
                "agent_id": best_agent.agent_id,
                "name": best_agent.name,
                "system_prompt": best_agent.system_prompt,
                "temperature": best_agent.temperature,
                "memory_count": len(memory),
                "execution_count": best_agent.total_tasks,
                "fitness_score": round(best_agent.fitness_score, 3),
                "generation": best_agent.generation,
                "success_rate": round((best_agent.successful_tasks/best_agent.total_tasks*100 if best_agent.total_tasks > 0 else 0), 1)
            },
            "best_fitness": round(best_agent.fitness_score, 3),
            "generation": request.generations,
            "population_stats": {
                "avg_fitness": round(sum(final_fitness_scores) / len(final_fitness_scores), 3),
                "max_fitness": round(max(final_fitness_scores), 3),
                "min_fitness": round(min(final_fitness_scores), 3),
                "population_size": len(population)
            },
            "evolution_history": evolution_history,
            "total_agents_evaluated": total_agents_evaluated
        }
    
    except Exception as e:
        logger.error(f"Evolution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Evolution failed: {str(e)}")

@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    """Simple chat endpoint using default agent"""
    try:
        temp_agent_id = f"chat_{random.randint(1000, 9999)}"
        temp_agent = AgenticAgent(
            agent_id=temp_agent_id,
            name="Chat Assistant",
            system_prompt="You are a helpful AI assistant. Provide clear, accurate answers.",
            tools=tools,
            temperature=0.7
        )
        
        result = await temp_agent.execute(payload.message, payload.context)
        return {
            "message": result.get("result", "I apologize, but I couldn't generate a response."),
            "agent_id": temp_agent_id
        }
    
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.get("/tools")
async def list_tools():
    """List available tools for agents"""
    return {
        "total_tools": len(tools),
        "tools": [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in tools
        ]
    }

@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent and all its data"""
    try:
        if agent_id in agent_registry:
            del agent_registry[agent_id]
        
        success = db.delete_agent(agent_id)
        if success:
            return {"message": f"Agent {agent_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    except Exception as e:
        logger.error(f"Failed to delete agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete agent: {str(e)}")

@router.get("/system/stats")
async def system_stats():
    """Get system statistics"""
    agents = db.get_all_agents()
    total_memory = 0
    total_executions = 0
    
    for agent in agents:
        memory = db.get_agent_memory(agent['agent_id'], limit=1000)
        total_memory += len(memory)
        total_executions += agent.get('total_tasks', 0)
    
    return {
        "total_agents": len(agents),
        "total_memory_entries": total_memory,
        "total_executions": total_executions,
        "database_file": "agents.db",
        "uptime": "Persistent - survives server restarts"
    }