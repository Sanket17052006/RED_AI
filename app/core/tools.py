"""
Tools for AI agents including safe calculator
"""
import ast
import operator
import re
from typing import List
import logging

logger = logging.getLogger(__name__)

# Import LangChain tools
try:
    from langchain_core.tools import Tool
    HAS_LANGCHAIN = True
except ImportError:
    logger.warning("LangChain tools not available")
    HAS_LANGCHAIN = False

# ==================== SAFE CALCULATOR ====================

class SafeCalculator:
    """Safe mathematical expression evaluator without eval()"""
    
    @staticmethod
    def _safe_eval(node):
        """Safely evaluate AST node with limited operations"""
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = SafeCalculator._safe_eval(node.left)
            right = SafeCalculator._safe_eval(node.right)
            
            op_map = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.FloorDiv: operator.floordiv,
                ast.Mod: operator.mod
            }
            
            if type(node.op) in op_map:
                return op_map[type(node.op)](left, right)
            else:
                raise ValueError(f"Unsupported operator: {type(node.op)}")
        elif isinstance(node, ast.UnaryOp):
            operand = SafeCalculator._safe_eval(node.operand)
            if isinstance(node.op, ast.USub):
                return -operand
            elif isinstance(node.op, ast.UAdd):
                return operand
            else:
                raise ValueError(f"Unsupported unary operator: {type(node.op)}")
        else:
            raise ValueError(f"Unsupported AST node: {type(node)}")
    
    @staticmethod
    def calculate(expression: str) -> float:
        """Safely evaluate a mathematical expression"""
        try:
            expr = expression.strip().replace("^", "**")
            
            if not re.match(r'^[\d\s\.\+\-\*\/\^\(\)]+$', expr):
                raise ValueError("Expression contains unsafe characters")
            
            tree = ast.parse(expr, mode='eval')
            result = SafeCalculator._safe_eval(tree.body)
            return result
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")

# ==================== AGENT TOOLS ====================

def calculate_tool(expression: str) -> str:
    """Perform mathematical calculations safely"""
    try:
        result = SafeCalculator.calculate(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

def search_knowledge_tool(query: str) -> str:
    """Search internal knowledge base"""
    knowledge = {
        "python": "Python is a high-level, interpreted programming language known for its simplicity and readability.",
        "ai": "Artificial Intelligence (AI) is the simulation of human intelligence processes by machines.",
        "api": "API (Application Programming Interface) is a set of rules for software communication.",
        "agent": "An AI agent is an autonomous entity that perceives its environment and acts to achieve goals.",
        "machine learning": "Machine learning is a subset of AI that enables systems to learn from experience.",
        "openai": "OpenAI is an AI research company that created models like GPT-4.",
        "fastapi": "FastAPI is a modern web framework for building APIs with Python.",
        "genetic algorithm": "Genetic algorithms are optimization algorithms inspired by natural selection."
    }
    
    query_lower = query.lower().strip()
    for key, value in knowledge.items():
        if key in query_lower or any(word in query_lower for word in key.split()):
            return f"{key.capitalize()}: {value}"
    
    return f"No information found about '{query}'. Try: python, ai, api, agent, etc."

def text_analysis_tool(text: str) -> str:
    """Analyze text and provide statistics"""
    if not text or text.strip() == "":
        return "Error: No text provided for analysis."
    
    words = text.split()
    chars = len(text)
    chars_no_spaces = len(text.replace(" ", ""))
    sentences = len(re.findall(r'[.!?]+', text))
    
    return f"""Text Analysis:
- Words: {len(words)}
- Characters (total): {chars}
- Characters (no spaces): {chars_no_spaces}
- Sentences: {sentences}
- Average word length: {sum(len(w) for w in words)/len(words):.1f} chars"""

def data_format_tool(input_str: str) -> str:
    """Format text data. Input format: 'text|format_type'"""
    if '|' not in input_str:
        text = input_str
        format_type = "title"
    else:
        parts = input_str.split('|', 1)
        text = parts[0].strip()
        format_type = parts[1].strip().lower() if len(parts) > 1 else "title"
    
    if not text:
        return "Error: No text provided to format."
    
    format_type = format_type.strip().lower()
    if format_type == "uppercase":
        return text.upper()
    elif format_type == "lowercase":
        return text.lower()
    elif format_type == "title":
        return text.title()
    elif format_type == "capitalize":
        return text.capitalize()
    elif format_type == "reverse":
        return text[::-1]
    else:
        return f"Error: Unknown format type '{format_type}'. Use: uppercase, lowercase, title, capitalize, or reverse."

# Create LangChain tools
if HAS_LANGCHAIN:
    tools = [
        Tool(
            name="Calculator",
            func=calculate_tool,
            description="Useful for performing mathematical calculations. Input should be a valid expression like '2 + 3 * 4' or '10^2'."
        ),
        Tool(
            name="KnowledgeSearch",
            func=search_knowledge_tool,
            description="Search for information in the knowledge base. Input should be a search query about technology or AI."
        ),
        Tool(
            name="TextAnalyzer",
            func=text_analysis_tool,
            description="Analyze text and provide statistics. Input should be text to analyze."
        ),
        Tool(
            name="DataFormatter",
            func=data_format_tool,
            description="Format text data. Input should be 'text|format_type' where format_type is: uppercase, lowercase, title, capitalize, or reverse."
        )
    ]
else:
    tools = []