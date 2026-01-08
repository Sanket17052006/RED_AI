"""
Genetic algorithm for evolving agent configurations
"""
import random
from typing import List
import logging

from app.core.agent import AgenticAgent

logger = logging.getLogger(__name__)

class AgentEvolutionEngine:
    """Genetic algorithm for evolving agent configurations"""
    
    def __init__(self, population_size: int = 10, mutation_rate: float = 0.15,
                 crossover_rate: float = 0.7, elite_size: int = 2):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        self.generation = 0
    
    async def evaluate_fitness(self, agent: AgenticAgent, test_tasks: List[str]) -> float:
        """Evaluate agent fitness by testing on tasks"""
        try:
            if not test_tasks:
                agent.fitness_score = 0.0
                agent._save_to_db()
                return 0.0
            
            total_score = 0.0
            
            for task in test_tasks:
                result = await agent.execute(task)
                output = result.get("result", "")
                
                score = 0.0
                
                if output and "Error" not in output and len(output) > 5:
                    score += 0.4
                
                output_len = len(output)
                if 15 <= output_len <= 1000:
                    score += 0.3
                elif output_len > 5:
                    score += 0.15
                
                if result.get("steps"):
                    steps = result.get("steps", [])
                    if len(steps) > 0:
                        score += 0.3
                
                total_score += score
            
            fitness = total_score / len(test_tasks)
            agent.fitness_score = fitness
            agent._save_to_db()
            
            return fitness
            
        except Exception as e:
            logger.error(f"Error evaluating fitness: {e}")
            agent.fitness_score = 0.0
            agent._save_to_db()
            return 0.0
    
    def select_parents(self, population: List[AgenticAgent]) -> tuple:
        """Tournament selection"""
        if len(population) < 2:
            return population[0], population[0] if population else None
        
        tournament_size = min(4, len(population))
        
        tournament1 = random.sample(population, tournament_size)
        parent1 = max(tournament1, key=lambda x: x.fitness_score)
        
        remaining = [a for a in population if a.agent_id != parent1.agent_id]
        if remaining:
            tournament2 = random.sample(remaining, min(tournament_size, len(remaining)))
            parent2 = max(tournament2, key=lambda x: x.fitness_score)
        else:
            parent2 = parent1
        
        return parent1, parent2
    
    async def evolve(self, population: List[AgenticAgent], test_tasks: List[str]) -> List[AgenticAgent]:
        """Evolve population to next generation"""
        if len(population) < 2:
            return population
        
        population.sort(key=lambda x: x.fitness_score, reverse=True)
        
        new_population = []
        elite_count = min(self.elite_size, len(population))
        for i in range(elite_count):
            elite = population[i]
            elite.generation = self.generation + 1
            elite._save_to_db()
            new_population.append(elite)
        
        while len(new_population) < self.population_size:
            parent1, parent2 = self.select_parents(population)
            
            if random.random() < self.crossover_rate and parent1.agent_id != parent2.agent_id:
                child = parent1.crossover(parent2)
            else:
                child = AgenticAgent(
                    agent_id=f"agent_{random.randint(10000, 99999)}",
                    name=f"Clone_{parent1.name}",
                    system_prompt=parent1.system_prompt,
                    tools=parent1.tools,
                    temperature=parent1.temperature
                )
            
            child.mutate(self.mutation_rate)
            child.generation = self.generation + 1
            child._save_to_db()
            new_population.append(child)
        
        self.generation += 1
        return new_population[:self.population_size]

# Global evolution engine
evolution_engine = AgentEvolutionEngine()