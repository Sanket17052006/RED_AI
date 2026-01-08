"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional

class CreateAgentRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    system_prompt: str = Field(..., min_length=10, max_length=2000)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v

class AgentResponse(BaseModel):
    agent_id: str
    name: str
    system_prompt: str
    temperature: float
    memory_count: int
    execution_count: int
    fitness_score: float
    generation: int
    success_rate: float

class ExecuteTaskRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=1000)
    context: Optional[str] = Field(None, max_length=2000)

class ExecuteTaskResponse(BaseModel):
    result: str
    steps: List[Dict]
    timestamp: str
    success: bool
    agent_id: str

class EvolveAgentsRequest(BaseModel):
    base_agents: List[str] = Field(..., min_items=1, max_items=20)
    test_tasks: List[str] = Field(..., min_items=1, max_items=20)
    generations: int = Field(5, ge=1, le=50)
    population_size: int = Field(10, ge=2, le=50)
    mutation_rate: float = Field(0.1, ge=0.0, le=1.0)

class EvolveAgentsResponse(BaseModel):
    best_agent: AgentResponse
    best_fitness: float
    generation: int
    population_stats: Dict
    evolution_history: List[Dict]
    total_agents_evaluated: int

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    context: Optional[str] = Field(None, max_length=2000)

class ChatResponse(BaseModel):
    message: str
    agent_id: str