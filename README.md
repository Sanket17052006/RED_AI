# RED AI - Agentic AI Builder with Genetic Evolution System 🤖🧬
**🚀 Beyond Chatbots: Autonomous AI Agents That Evolve & Improve Themselves**

A revolutionary AI platform that creates, deploys, and evolves autonomous AI agents using genetic algorithms. Watch as AI agents learn, adapt, and become increasingly intelligent through simulated evolution.

## 🎯 What Makes This Different?

| Traditional Chatbots | **Our Agentic AI** |
|-------------------|-------------------|
| 🔄 Simple Q&A responses | 🧠 **Autonomous reasoning & planning** |
| 📝 Static behavior | 🔬 **Genetic evolution improves over time** |
| 🤖 One-size-fits-all | 🎨 **Customizable agent personalities** |
| 💾 Forgetful sessions | 🗃️ **Persistent memory across restarts** |
| 🛠️ Manual optimization | ⚡ **Self-optimizing through evolution** |

## 🏗️ System Architecture
```mermaid
graph TB
    A[Frontend Dashboard] --> B[FastAPI Backend]
    B --> C{Agent Manager}
    C --> D[Agentic Core]
    C --> E[Genetic Engine]
    D --> F[Tools: Calculator, Search, Analysis]
    E --> G[Evolution: Selection, Crossover, Mutation]
    H[(SQLite Database)] --> C
    D --> I[OpenAI GPT-4]
    E --> J[Fitness Evaluation]
```

## 🎮 Features Dashboard

### 🏗️ **Agent Management**
- **Create Custom Agents**: Define unique personalities and behaviors
- **Real-time Performance Metrics**: Track success rates and fitness scores
- **Memory Visualization**: See what agents remember and learn

### 🔄 **Genetic Evolution Lab**
- **Evolution Controls**: Adjust mutation rates, population size, generations
- **Fitness Progression**: Watch agents improve over generations
- **Best Agent Selection**: Automatically identifies and promotes top performers

### 🛠️ **Tool Integration**
- **Smart Calculator**: Safe mathematical computations
- **Knowledge Search**: Curated AI/tech information base
- **Text Analysis**: Statistical insights from text
- **Data Formatter**: Multiple text transformation options

### 📊 **Real-time Monitoring**
- **Live Execution Logs**: Watch agents think and act
- **Evolution Progress**: Visual timeline of improvements
- **Performance Analytics**: Success rates, tool usage, response quality

## 📁 Project Structure


## 📚 API Reference

### Core Endpoints
```http
POST   /agents/create      # Create new AI agent
POST   /agents/{id}/execute # Execute task with agent
POST   /agents/evolve      # Evolve agents (genetic algorithm)
GET    /agents             # List all agents
GET    /agents/{id}/memory # Get agent's memory
GET    /system/stats       # System statistics
```


## 🧬 How Evolution Works

1. **Initialize Population**: Start with existing agents + random variations
2. **Evaluate Fitness**: Test each agent on benchmark tasks
3. **Tournament Selection**: Choose best performers as parents
4. **Crossover**: Combine traits from parent agents
5. **Mutation**: Introduce random improvements
6. **Next Generation**: Repeat for N generations
7. **Best Agent Emerges**: Most fit agent becomes the new champion

## 🎨 Dashboard Features

### Agent Creation Panel
- **Name & Personality**: Customize agent identity
- **Creativity Slider**: Adjust temperature (0.0-2.0)
- **System Prompt Editor**: Define agent behavior
- **Quick Templates**: Math Expert, Research Assistant, Creative Writer

### Evolution Control Center
- **Generation Counter**: Track evolution progress
- **Fitness Graph**: Visualize improvement over time
- **Population Monitor**: Watch agents compete and improve
- **Mutation Controls**: Fine-tune evolution parameters

### Execution Playground
- **Task Input**: Natural language task entry
- **Live Execution Steps**: Watch agent thinking process
- **Tool Usage Highlight**: See which tools are used
- **Result Display**: Formatted output with metrics

### Memory & Analytics
- **Memory Timeline**: Past tasks and results
- **Success Rate Dashboard**: Performance metrics
- **Tool Usage Statistics**: Which tools are most effective
- **Evolution History**: Complete timeline of improvements

## 🛡️ Security & Safety

### Safe Computation
- ✅ **No dangerous eval()** - Uses AST-based safe calculator
- ✅ **Input validation** - All API endpoints validated
- ✅ **Rate limiting** - Prevents API abuse
- ✅ **Error boundaries** - Graceful error handling

### Data Privacy
- 🔒 **Local SQLite database** - Your data stays on your machine
- 🔒 **No data sharing** - All processing is local
- 🔒 **Agent memory isolation** - Each agent's data is separate

## 📈 Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Agent Creation Time | < 500ms | ~300ms |
| Task Execution | < 5s | ~2-3s |
| Evolution Cycle | < 30s/gen | ~20s/gen |
| Memory Persistence | 100% | 100% |
| Success Rate (evolved) | > 85% | ~90% |

## 🌟 Real-World Applications

### 🎓 **Education & Research**
- Intelligent tutoring systems that adapt to learning styles
- Research assistants that improve their information gathering
- Code review agents that learn from past mistakes

### 💼 **Business Automation**
- Customer service agents that evolve to handle new queries
- Data analysis agents that improve their methodologies
- Process optimization through agent evolution

### 🔬 **AI Research**
- Studying emergent behaviors in AI systems
- Testing evolutionary algorithms in practice
- Benchmarking different agent architectures

## 🚧 Development Roadmap

### ✅ **Implemented**
- [x] Core agentic architecture
- [x] Genetic evolution engine
- [x] SQLite persistent storage
- [x] Tool integration suite
- [x] Basic frontend dashboard

### 📋 **Future scope**
- [ ] Web search integration
- [ ] Custom tool creation API
- [ ] Advanced visualization dashboard
- [ ] Multi-agent collaboration
- [ ] Real-time evolution streaming
- [ ] Advanced memory with embeddings
- [ ] Evolution visualization in 3D


## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API Key
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/agentic-ai-evolution.git
cd agentic-ai-evolution

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "OPENAI_API_KEY=your_key_here" > .env

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running the Frontend
```bash
# Open frontend/index.html in your browser
# or serve with a local server:
python -m http.server 8080
```

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Setup
```bash
# Set up development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Hackathon Submission

This project was built for **DECTHON 2026** and demonstrates:
- ✅ **True agentic behavior** beyond simple chatbots
- ✅ **Autonomous planning and execution**
- ✅ **Genetic evolution** for self-improvement
- ✅ **Code-based implementation** (no low-code platforms)
- ✅ **Persistent memory** across sessions
- ✅ **Real-world applicability**

## 👥 Team

1- Sanket Srivastava
2- Shoumik Shourya
3- Vikas Sharma
4- Vivek Kumar
5- Ved Prakash


## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- LangChain team for the amazing framework
- FastAPI for the incredible web framework
- DECTHON 2026 organizers for the opportunity

---
