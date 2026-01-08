"""
Database layer for persistent agent storage
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class AgentDatabase:
    """SQLite database for persistent agent storage"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            import os
            # Use backend directory for database
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "agents.db")
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Agents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    system_prompt TEXT NOT NULL,
                    temperature REAL NOT NULL,
                    fitness_score REAL DEFAULT 0.0,
                    generation INTEGER DEFAULT 0,
                    total_tasks INTEGER DEFAULT 0,
                    successful_tasks INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Memory table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    task TEXT NOT NULL,
                    result TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    FOREIGN KEY (agent_id) REFERENCES agents (agent_id) ON DELETE CASCADE
                )
            ''')
            
            # Execution history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS execution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    task TEXT NOT NULL,
                    result TEXT NOT NULL,
                    steps TEXT,  -- JSON encoded
                    timestamp TIMESTAMP NOT NULL,
                    success INTEGER DEFAULT 0,
                    FOREIGN KEY (agent_id) REFERENCES agents (agent_id) ON DELETE CASCADE
                )
            ''')
            
            # Evolution history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evolution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evolution_id TEXT NOT NULL,
                    generation INTEGER NOT NULL,
                    best_agent_id TEXT NOT NULL,
                    avg_fitness REAL NOT NULL,
                    max_fitness REAL NOT NULL,
                    min_fitness REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def save_agent(self, agent_data: Dict) -> bool:
        """Save agent to database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO agents 
                    (agent_id, name, system_prompt, temperature, fitness_score, 
                     generation, total_tasks, successful_tasks, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    agent_data['agent_id'],
                    agent_data['name'],
                    agent_data['system_prompt'],
                    agent_data['temperature'],
                    agent_data.get('fitness_score', 0.0),
                    agent_data.get('generation', 0),
                    agent_data.get('total_tasks', 0),
                    agent_data.get('successful_tasks', 0)
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save agent: {e}")
            return False
    
    def save_memory(self, agent_id: str, task: str, result: str):
        """Save agent memory entry"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO agent_memory (agent_id, task, result, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (agent_id, task, result[:500], datetime.now().isoformat()))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
    
    def save_execution(self, agent_id: str, execution_data: Dict):
        """Save execution history"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO execution_history 
                    (agent_id, task, result, steps, timestamp, success)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    agent_id,
                    execution_data['task'],
                    execution_data['result'][:1000],
                    json.dumps(execution_data.get('steps', [])),
                    execution_data['timestamp'],
                    1 if execution_data.get('success', False) else 0
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save execution: {e}")
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent from database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM agents WHERE agent_id = ?', (agent_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            logger.error(f"Failed to get agent: {e}")
            return None
    
    def get_all_agents(self) -> List[Dict]:
        """Get all agents from database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM agents ORDER BY created_at DESC')
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get all agents: {e}")
            return []
    
    def get_agent_memory(self, agent_id: str, limit: int = 20) -> List[Dict]:
        """Get agent's memory"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT task, result, timestamp 
                    FROM agent_memory 
                    WHERE agent_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (agent_id, limit))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get agent memory: {e}")
            return []
    
    def get_execution_history(self, agent_id: str, limit: int = 10) -> List[Dict]:
        """Get agent's execution history"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT task, result, steps, timestamp, success
                    FROM execution_history 
                    WHERE agent_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (agent_id, limit))
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    data = dict(row)
                    data['steps'] = json.loads(data['steps']) if data['steps'] else []
                    results.append(data)
                return results
        except Exception as e:
            logger.error(f"Failed to get execution history: {e}")
            return []
    
    def update_agent_stats(self, agent_id: str, fitness_score: float = None, 
                          total_tasks: int = None, successful_tasks: int = None):
        """Update agent statistics"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                updates = []
                params = []
                
                if fitness_score is not None:
                    updates.append("fitness_score = ?")
                    params.append(fitness_score)
                
                if total_tasks is not None:
                    updates.append("total_tasks = ?")
                    params.append(total_tasks)
                
                if successful_tasks is not None:
                    updates.append("successful_tasks = ?")
                    params.append(successful_tasks)
                
                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    query = f"UPDATE agents SET {', '.join(updates)} WHERE agent_id = ?"
                    params.append(agent_id)
                    cursor.execute(query, params)
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"Failed to update agent stats: {e}")
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete agent and all related data"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM agents WHERE agent_id = ?', (agent_id,))
                conn.commit()
                logger.info(f"Deleted agent: {agent_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete agent: {e}")
            return False

# Global database instance
db = AgentDatabase()