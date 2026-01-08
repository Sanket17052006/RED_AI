"""
Agentic AI Agent class with tools, memory, and execution capabilities
"""
from datetime import datetime
from typing import List, Dict, Optional, Any
import random
import re
import logging
import asyncio

from app.core.database import db
from app.core.tools import tools

# Setup logger first
logger = logging.getLogger(__name__)

# Import LangChain
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    HAS_LANGCHAIN_OPENAI = True
except ImportError as e:
    logger.warning(f"LangChain OpenAI import error: {e}")
    HAS_LANGCHAIN_OPENAI = False
    ChatOpenAI = None
    ChatPromptTemplate = None
    MessagesPlaceholder = None

# Try different import paths for AgentExecutor (LangChain versions vary)
HAS_AGENT_FRAMEWORK = False
AgentExecutor = None
create_openai_tools_agent = None

try:
    # Try newer LangChain import path
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    HAS_AGENT_FRAMEWORK = True
except ImportError:
    try:
        # Try alternative import path
        from langchain.agents.agent_executor import AgentExecutor
        from langchain.agents import create_openai_tools_agent
        HAS_AGENT_FRAMEWORK = True
    except ImportError:
        try:
            # Try langchain_core path
            from langchain_core.agents import AgentExecutor
            from langchain.agents import create_openai_tools_agent
            HAS_AGENT_FRAMEWORK = True
        except ImportError:
            logger.warning("Full LangChain agent framework not available, using simplified execution")
            HAS_AGENT_FRAMEWORK = False

# Global agent registry
agent_registry: Dict[str, 'AgenticAgent'] = {}

class AgenticAgent:
    """Represents an AI agent with tools, memory, and execution capabilities"""
    
    def __init__(self, agent_id: str, name: str, system_prompt: str, 
                 tools: List, temperature: float = 0.7, max_memory_size: int = 50):
        self.agent_id = agent_id
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools
        self.temperature = temperature
        self.max_memory_size = max_memory_size
        
        # Initialize statistics
        db_agent = db.get_agent(agent_id)
        if db_agent:
            self.fitness_score = db_agent.get('fitness_score', 0.0)
            self.generation = db_agent.get('generation', 0)
            self.total_tasks = db_agent.get('total_tasks', 0)
            self.successful_tasks = db_agent.get('successful_tasks', 0)
            logger.info(f"Loaded agent {agent_id} from database")
        else:
            self.fitness_score = 0.0
            self.generation = 0
            self.total_tasks = 0
            self.successful_tasks = 0
        
        # Create LLM instance
        if not HAS_LANGCHAIN_OPENAI or ChatOpenAI is None:
            raise ImportError("LangChain OpenAI is not available. Please install langchain-openai.")
        
        try:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=temperature,
                timeout=30,
                max_retries=3
            )
        except Exception as e:
            logger.error(f"Failed to create LLM for agent {agent_id}: {e}")
            raise
        
        # Initialize agent executor if available
        self.use_agent_executor = False
        if HAS_AGENT_FRAMEWORK and tools and ChatPromptTemplate is not None and create_openai_tools_agent is not None and AgentExecutor is not None:
            try:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    ("human", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ])
                agent = create_openai_tools_agent(self.llm, tools, prompt)
                self.executor = AgentExecutor(
                    agent=agent, 
                    tools=tools, 
                    verbose=False,
                    handle_parsing_errors=True,
                    max_iterations=5
                )
                self.use_agent_executor = True
            except Exception as e:
                logger.warning(f"Failed to create agent executor: {e}")
                self.use_agent_executor = False
        
        # Save to database
        self._save_to_db()
        agent_registry[agent_id] = self
    
    def _save_to_db(self):
        """Save agent state to database"""
        db.save_agent({
            'agent_id': self.agent_id,
            'name': self.name,
            'system_prompt': self.system_prompt,
            'temperature': self.temperature,
            'fitness_score': self.fitness_score,
            'generation': self.generation,
            'total_tasks': self.total_tasks,
            'successful_tasks': self.successful_tasks
        })
    
    async def execute(self, task: str, context: Optional[str] = None, max_retries: int = 2) -> Dict[str, Any]:
        """Execute a task using the agent with retry logic"""
        self.total_tasks += 1
        
        for attempt in range(max_retries):
            try:
                full_task = task
                if context:
                    full_task = f"Context: {context}\n\nTask: {task}"
                
                logger.info(f"Agent {self.agent_id} executing task: {task[:100]}...")
                
                if self.use_agent_executor and self.tools:
                    result = await self.executor.ainvoke({"input": full_task})
                    output = result.get("output", "No output generated")
                    steps = result.get("intermediate_steps", [])
                else:
                    # Simplified execution
                    tools_desc = "\n".join([f"- {t.name}: {t.description}" for t in self.tools]) if self.tools else ""
                    prompt = f"""{self.system_prompt}

Available tools:
{tools_desc}

Task: {full_task}

Think step by step. If you need to use a tool, mention which tool you would use and what input you would give it. Then provide the final answer.

Now proceed with the task:"""
                    
                    response = await self.llm.ainvoke(prompt)
                    output = response.content
                    steps = self._extract_tool_usage(output)
                
                success = "Error" not in output and len(output) > 10
                if success:
                    self.successful_tasks += 1
                
                execution_record = {
                    "task": task,
                    "result": output,
                    "steps": steps,
                    "timestamp": datetime.now().isoformat(),
                    "attempt": attempt + 1,
                    "success": success
                }
                
                # Save to database
                db.save_execution(self.agent_id, execution_record)
                db.save_memory(self.agent_id, task, output[:200])
                self._save_to_db()
                
                logger.info(f"Agent {self.agent_id} completed task successfully")
                return execution_record
                
            except Exception as e:
                logger.error(f"Agent {self.agent_id} execution error: {e}")
                if attempt == max_retries - 1:
                    error_record = {
                        "task": task,
                        "result": f"Error after {max_retries} attempts: {str(e)}",
                        "steps": [],
                        "timestamp": datetime.now().isoformat(),
                        "success": False
                    }
                    db.save_execution(self.agent_id, error_record)
                    return error_record
                await asyncio.sleep(1 << attempt)
    
    def _extract_tool_usage(self, output: str) -> List[Dict]:
        """Extract tool usage from agent output"""
        steps = []
        
        if not self.tools:
            return steps
        
        tool_patterns = {
            "Calculator": [r'calculate\s+([\d\s\.\+\-\*\/\^\(\)]+)', r'(\d+\s*[\+\-\*\/]\s*\d+)'],
            "KnowledgeSearch": [r'search.*for\s+"([^"]+)"', r'look up\s+([^\.]+)'],
            "TextAnalyzer": [r'analyze.*text\s*[:"]\s*([^"\n]+)'],
            "DataFormatter": [r'format.*["\']([^"\']+)["\']\s+as\s+(\w+)', r'([^|]+)\|\s*(\w+)']
        }
        
        for tool_name, patterns in tool_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, output, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if isinstance(match, tuple):
                            input_data = "|".join(match) if len(match) > 1 else match[0]
                        else:
                            input_data = match
                        
                        tool = next((t for t in self.tools if t.name == tool_name), None)
                        if tool:
                            try:
                                tool_result = tool.func(input_data.strip())
                                steps.append({
                                    "tool": tool_name,
                                    "input": input_data.strip(),
                                    "output": tool_result,
                                    "timestamp": datetime.now().isoformat()
                                })
                            except Exception as e:
                                logger.warning(f"Tool {tool_name} execution failed: {e}")
        
        return steps
    
    def get_memory_summary(self) -> str:
        """Get a summary of agent's memory"""
        memory = db.get_agent_memory(self.agent_id, limit=5)
        
        if not memory:
            return "No memory entries yet."
        
        summary = f"Agent {self.name} - Recent Memory (last 5):\n"
        for i, entry in enumerate(memory, 1):
            task_preview = entry['task'][:40] + "..." if len(entry['task']) > 40 else entry['task']
            result_preview = entry['result'][:40] + "..." if len(entry['result']) > 40 else entry['result']
            summary += f"{i}. Task: {task_preview}\n   Result: {result_preview}\n"
        
        success_rate = (self.successful_tasks/self.total_tasks*100 if self.total_tasks > 0 else 0)
        summary += f"\nSuccess rate: {success_rate:.1f}% ({self.successful_tasks}/{self.total_tasks})"
        return summary
    
    def mutate(self, mutation_rate: float = 0.1):
        """Mutate agent configuration"""
        mutations_applied = []
        
        if random.random() < mutation_rate:
            mutations = [
                " Be more concise in responses.",
                " Provide detailed, step-by-step explanations.",
                " Focus on accuracy and precision.",
                " Be creative and think outside the box.",
                " Use formal, professional language.",
            ]
            mutation = random.choice(mutations)
            self.system_prompt += mutation
            mutations_applied.append(f"Prompt: {mutation}")
            
            if HAS_LANGCHAIN_OPENAI and ChatOpenAI is not None:
                self.llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=self.temperature,
                    timeout=30
                )
        
        if random.random() < mutation_rate:
            old_temp = self.temperature
            self.temperature = max(0.1, min(1.5, self.temperature + random.uniform(-0.3, 0.3)))
            mutations_applied.append(f"Temperature: {old_temp:.2f} -> {self.temperature:.2f}")
            
            if HAS_LANGCHAIN_OPENAI and ChatOpenAI is not None:
                self.llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=self.temperature,
                    timeout=30
                )
        
        if mutations_applied:
            self._save_to_db()
        
        return mutations_applied
    
    def crossover(self, other: 'AgenticAgent') -> 'AgenticAgent':
        """Create offspring agent by combining two agents"""
        split_point_self = len(self.system_prompt) // 2
        split_point_other = len(other.system_prompt) // 2
        combined_prompt = self.system_prompt[:split_point_self] + other.system_prompt[split_point_other:]
        
        avg_temp = (self.temperature + other.temperature) / 2
        
        new_id = f"agent_{random.randint(10000, 99999)}"
        new_name = f"Evolved_{self.name.split()[-1]}_{other.name.split()[-1]}_{new_id[-4:]}"
        
        return AgenticAgent(
            agent_id=new_id,
            name=new_name,
            system_prompt=combined_prompt[:2000],
            tools=self.tools,
            temperature=avg_temp
        )