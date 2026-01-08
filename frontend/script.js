// RED AI - Agentic AI Builder Frontend
// ==========================================
// IMPORTANT: Set your backend URL in the .env file as BACKEND_URL=http://localhost:8000
// The frontend will automatically read it from the environment
// ==========================================

// ========== CONFIGURATION ==========
// Backend URL - Leave blank to auto-detect, or set directly: const BACKEND_URL = 'http://localhost:8000';
const BACKEND_URL = 'http://localhost:8000';

// Get backend URL - auto-detect based on current location
function getBackendURL() {
    if (BACKEND_URL) {
        return BACKEND_URL;
    }
    
    // If accessing via /dashboard, use same origin
    if (window.location.pathname.includes('/dashboard') || window.location.pathname === '/') {
        return window.location.origin;
    }
    
    // Default fallback
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    
    // For other origins, use the same origin
    return window.location.origin;
}

const API_BASE = getBackendURL();

// ========== STATE MANAGEMENT ==========
let currentSection = 'agents';
let selectedAgentId = null;
let agentsList = [];
let pollingInterval = null;

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    // Log backend URL for debugging
    console.log('Backend URL:', API_BASE);
    console.log('Current location:', window.location.href);
    
    setupNavigation();
    setupForms();
    setupTemperatureSlider();
    await checkServerStatus();
    await loadInitialData();
    startPolling();
}

function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const section = item.dataset.section;
            switchSection(section);
        });
    });
}

function switchSection(section) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.section === section);
    });

    // Update content sections
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.classList.toggle('active', sec.id === `section-${section}`);
    });

    currentSection = section;

    // Load section-specific data
    switch(section) {
        case 'agents':
            loadAgents();
            break;
        case 'tools':
            loadTools();
            break;
        case 'stats':
            loadStats();
            break;
        case 'chat':
            scrollChatToBottom();
            break;
    }
}

function setupForms() {
    // Create Agent Form
    document.getElementById('createAgentForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await createAgent();
    });

    // Evolve Agents Form
    document.getElementById('evolveForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await evolveAgents();
    });

    // Execute Task Form
    document.getElementById('executeTaskForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await executeTask();
    });
}

function setupTemperatureSlider() {
    const slider = document.getElementById('temperature');
    const valueDisplay = document.getElementById('tempValue');
    slider.addEventListener('input', (e) => {
        valueDisplay.textContent = parseFloat(e.target.value).toFixed(1);
    });
}

// ========== API FUNCTIONS ==========

async function apiCall(endpoint, method = 'GET', body = null) {
    try {
        const url = `${API_BASE}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(url, options);
        
        // Check if response is actually JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('Non-JSON response received:', text.substring(0, 200));
            throw new Error(`Expected JSON but received ${contentType}. The backend might not be running or the endpoint is incorrect. URL: ${url}`);
        }
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}: ${response.statusText}` }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        console.error('API Base URL:', API_BASE);
        console.error('Endpoint:', endpoint);
        showToast(error.message, 'error');
        throw error;
    }
}

async function checkServerStatus() {
    try {
        const data = await apiCall('/');
        if (data && data.status) {
            document.getElementById('serverStatus').style.color = 'var(--success)';
            document.getElementById('serverStatus').title = 'Server Online - ' + API_BASE;
            return true;
        }
        throw new Error('Invalid response from server');
    } catch (error) {
        console.error('Server status check failed:', error);
        document.getElementById('serverStatus').style.color = 'var(--danger)';
        document.getElementById('serverStatus').title = `Server Offline - ${error.message}`;
        return false;
    }
}

async function loadAgents() {
    try {
        const agents = await apiCall('/agents');
        agentsList = agents;
        renderAgents(agents);
        document.getElementById('totalAgents').textContent = agents.length;
    } catch (error) {
        document.getElementById('agentsGrid').innerHTML = 
            '<div class="loading">Error loading agents. Please check if the backend is running.</div>';
    }
}

function renderAgents(agents) {
    const grid = document.getElementById('agentsGrid');
    
    if (agents.length === 0) {
        grid.innerHTML = '<div class="loading">No agents found. Create your first agent!</div>';
        return;
    }

    grid.innerHTML = agents.map(agent => `
        <div class="agent-card" onclick="openAgentDetails('${agent.agent_id}')">
            <div class="agent-header">
                <div>
                    <div class="agent-name">${escapeHtml(agent.name)}</div>
                    <div class="agent-id">${agent.agent_id}</div>
                </div>
                <span class="agent-badge">Gen ${agent.generation}</span>
            </div>
            <div style="margin: 1rem 0; color: var(--text-secondary); font-size: 0.9rem;">
                ${escapeHtml(agent.system_prompt.substring(0, 100))}...
            </div>
            <div class="agent-stats">
                <div class="agent-stat">
                    <span class="agent-stat-label">Fitness</span>
                    <span class="agent-stat-value">${agent.fitness_score.toFixed(3)}</span>
                </div>
                <div class="agent-stat">
                    <span class="agent-stat-label">Success Rate</span>
                    <span class="agent-stat-value">${agent.success_rate.toFixed(1)}%</span>
                </div>
                <div class="agent-stat">
                    <span class="agent-stat-label">Tasks</span>
                    <span class="agent-stat-value">${agent.execution_count}</span>
                </div>
                <div class="agent-stat">
                    <span class="agent-stat-label">Memory</span>
                    <span class="agent-stat-value">${agent.memory_count}</span>
                </div>
            </div>
            <div class="agent-actions">
                <button class="btn btn-primary" onclick="event.stopPropagation(); openTaskModal('${agent.agent_id}')">
                    <span>🚀</span> Execute Task
                </button>
            </div>
        </div>
    `).join('');
}

async function createAgent() {
    const name = document.getElementById('agentName').value;
    const systemPrompt = document.getElementById('systemPrompt').value;
    const temperature = parseFloat(document.getElementById('temperature').value);

    try {
        const agent = await apiCall('/agents/create', 'POST', {
            name,
            system_prompt: systemPrompt,
            temperature
        });

        showToast(`Agent "${agent.name}" created successfully!`, 'success');
        document.getElementById('createAgentForm').reset();
        document.getElementById('tempValue').textContent = '0.7';
        document.getElementById('temperature').value = 0.7;
        
        // Refresh agents list
        await loadAgents();
        
        // Switch to agents section
        switchSection('agents');
    } catch (error) {
        showToast(`Failed to create agent: ${error.message}`, 'error');
    }
}

async function openAgentDetails(agentId) {
    try {
        const agent = await apiCall(`/agents/${agentId}`);
        const memory = await apiCall(`/agents/${agentId}/memory`);

        selectedAgentId = agentId;

        document.getElementById('modalAgentName').textContent = agent.name;
        
        const content = `
            <div style="margin-bottom: 1.5rem;">
                <div style="margin-bottom: 1rem;">
                    <strong>Agent ID:</strong> <span style="font-family: monospace; color: var(--text-secondary);">${agent.agent_id}</span>
                </div>
                <div style="margin-bottom: 1rem;">
                    <strong>System Prompt:</strong>
                    <div style="margin-top: 0.5rem; padding: 1rem; background: var(--bg-darker); border-radius: 8px; color: var(--text-secondary);">
                        ${escapeHtml(agent.system_prompt)}
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1rem;">
                    <div><strong>Temperature:</strong> ${agent.temperature}</div>
                    <div><strong>Generation:</strong> ${agent.generation}</div>
                    <div><strong>Fitness Score:</strong> ${agent.fitness_score.toFixed(3)}</div>
                    <div><strong>Success Rate:</strong> ${agent.success_rate.toFixed(1)}%</div>
                    <div><strong>Total Tasks:</strong> ${agent.execution_count}</div>
                    <div><strong>Memory Entries:</strong> ${agent.memory_count}</div>
                </div>
                <div style="margin-top: 1.5rem;">
                    <strong>Recent Memory:</strong>
                    <div class="memory-list" style="margin-top: 1rem; max-height: 300px; overflow-y: auto;">
                        ${memory.memory.length > 0 ? memory.memory.slice(0, 10).map(entry => `
                            <div class="memory-item">
                                <div class="memory-task">Task: ${escapeHtml(entry.task.substring(0, 100))}</div>
                                <div class="memory-result">Result: ${escapeHtml(entry.result.substring(0, 150))}...</div>
                                <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem;">
                                    ${new Date(entry.timestamp).toLocaleString()}
                                </div>
                            </div>
                        `).join('') : '<div style="color: var(--text-secondary);">No memory entries yet.</div>'}
                    </div>
                </div>
            </div>
        `;

        document.getElementById('modalAgentContent').innerHTML = content;
        document.getElementById('agentModal').classList.add('active');
    } catch (error) {
        showToast(`Failed to load agent details: ${error.message}`, 'error');
    }
}

function closeAgentModal() {
    document.getElementById('agentModal').classList.remove('active');
    selectedAgentId = null;
}

async function deleteCurrentAgent() {
    if (!selectedAgentId) return;

    if (!confirm('Are you sure you want to delete this agent? This action cannot be undone.')) {
        return;
    }

    try {
        await apiCall(`/agents/${selectedAgentId}`, 'DELETE');
        showToast('Agent deleted successfully', 'success');
        closeAgentModal();
        await loadAgents();
    } catch (error) {
        showToast(`Failed to delete agent: ${error.message}`, 'error');
    }
}

function openTaskModal(agentId) {
    document.getElementById('executeAgentId').value = agentId;
    document.getElementById('executeTask').value = '';
    document.getElementById('executeContext').value = '';
    document.getElementById('taskResult').innerHTML = '';
    document.getElementById('taskModal').classList.add('active');
}

function closeTaskModal() {
    document.getElementById('taskModal').classList.remove('active');
}

async function executeTask() {
    const agentId = document.getElementById('executeAgentId').value;
    const task = document.getElementById('executeTask').value;
    const context = document.getElementById('executeContext').value;

    const resultDiv = document.getElementById('taskResult');
    resultDiv.innerHTML = '<div class="loading">Executing task...</div>';

    try {
        const result = await apiCall(`/agents/${agentId}/execute`, 'POST', {
            task,
            context: context || undefined
        });

        const stepsHtml = result.steps && result.steps.length > 0 ? `
            <div class="task-steps" style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                <strong style="display: block; margin-bottom: 0.75rem;">Execution Steps (${result.steps.length}):</strong>
                ${result.steps.map((step, idx) => `
                    <div class="step-item" style="margin-bottom: 1rem; padding: 0.75rem; background: rgba(255, 255, 255, 0.03); border-radius: 6px; border-left: 3px solid var(--primary);">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="background: var(--primary); color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: bold;">Step ${idx + 1}</span>
                            <strong>${escapeHtml(step.tool || 'Unknown Tool')}</strong>
                        </div>
                        ${step.input ? `
                            <div style="margin-top: 0.5rem;">
                                <strong style="color: var(--text-secondary); font-size: 0.85rem;">Input:</strong>
                                <div style="margin-top: 0.25rem; padding: 0.5rem; background: var(--bg-darker); border-radius: 4px; font-size: 0.85rem; white-space: pre-wrap; word-wrap: break-word;">
                                    ${formatResult(step.input)}
                                </div>
                            </div>
                        ` : ''}
                        ${step.output ? `
                            <div style="margin-top: 0.5rem;">
                                <strong style="color: var(--text-secondary); font-size: 0.85rem;">Output:</strong>
                                <div style="margin-top: 0.25rem; padding: 0.5rem; background: var(--bg-darker); border-radius: 4px; font-size: 0.85rem; white-space: pre-wrap; word-wrap: break-word; max-height: 200px; overflow-y: auto;">
                                    ${formatResult(step.output)}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        ` : '';

        // Format the result nicely
        const formattedResult = formatResult(result.result);
        
        resultDiv.innerHTML = `
            <div style="padding: 1rem; background: ${result.success ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)'}; border-radius: 8px; border-left: 3px solid ${result.success ? 'var(--success)' : 'var(--danger)'};">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <strong>Status:</strong> 
                    <span style="font-size: 1.2rem;">${result.success ? '✅' : '❌'}</span>
                    <span>${result.success ? 'Success' : 'Failed'}</span>
                </div>
                <div style="margin-top: 1rem;">
                    <strong>Result:</strong>
                    <div style="margin-top: 0.5rem;">${formattedResult}</div>
                </div>
                ${stepsHtml}
                <div style="margin-top: 1rem; font-size: 0.85rem; color: var(--text-secondary);">
                    <strong>Timestamp:</strong> ${new Date(result.timestamp).toLocaleString()}
                </div>
            </div>
        `;

        // Refresh agents to update stats
        await loadAgents();
    } catch (error) {
        resultDiv.innerHTML = `
            <div style="padding: 1rem; background: rgba(239, 68, 68, 0.1); border-radius: 8px; border-left: 3px solid var(--danger);">
                <strong>Error:</strong> ${escapeHtml(error.message)}
            </div>
        `;
    }
}

async function loadTools() {
    try {
        const data = await apiCall('/tools');
        renderTools(data.tools);
        document.getElementById('totalTools').textContent = data.total_tools;
    } catch (error) {
        document.getElementById('toolsGrid').innerHTML = 
            '<div class="loading">Error loading tools.</div>';
    }
}

function renderTools(tools) {
    const grid = document.getElementById('toolsGrid');
    grid.innerHTML = tools.map(tool => `
        <div class="tool-card">
            <div class="tool-name">${escapeHtml(tool.name)}</div>
            <div class="tool-description">${escapeHtml(tool.description)}</div>
        </div>
    `).join('');
}

async function loadStats() {
    try {
        const stats = await apiCall('/system/stats');
        document.getElementById('statTotalAgents').textContent = stats.total_agents;
        document.getElementById('statMemory').textContent = stats.total_memory_entries;
        document.getElementById('statExecutions').textContent = stats.total_executions;
    } catch (error) {
        showToast(`Failed to load stats: ${error.message}`, 'error');
    }
}

async function evolveAgents() {
    const checkboxes = document.querySelectorAll('#agentCheckboxes input[type="checkbox"]:checked');
    const selectedAgents = Array.from(checkboxes).map(cb => cb.value);
    
    if (selectedAgents.length === 0) {
        showToast('Please select at least one agent', 'error');
        return;
    }

    const testTasks = document.getElementById('testTasks').value.split('\n').filter(t => t.trim());
    if (testTasks.length === 0) {
        showToast('Please enter at least one test task', 'error');
        return;
    }

    const generations = parseInt(document.getElementById('generations').value);
    const populationSize = parseInt(document.getElementById('populationSize').value);
    const mutationRate = parseFloat(document.getElementById('mutationRate').value);

    const progressDiv = document.getElementById('evolutionProgress');
    const statusDiv = document.getElementById('evolutionStatus');
    progressDiv.style.display = 'block';
    statusDiv.innerHTML = '<div class="loading">Starting evolution...</div>';

    try {
        const result = await apiCall('/agents/evolve', 'POST', {
            base_agents: selectedAgents,
            test_tasks: testTasks,
            generations,
            population_size: populationSize,
            mutation_rate: mutationRate
        });

        let historyHtml = result.evolution_history.map(gen => `
            <div class="generation-info">
                <strong>Generation ${gen.generation}</strong><br>
                Avg Fitness: ${gen.avg_fitness.toFixed(3)} | 
                Max: ${gen.max_fitness.toFixed(3)} | 
                Min: ${gen.min_fitness.toFixed(3)}<br>
                Best: ${escapeHtml(gen.best_agent_name || 'N/A')}
            </div>
        `).join('');

        statusDiv.innerHTML = `
            <div style="padding: 1rem; background: rgba(34, 197, 94, 0.1); border-radius: 8px; margin-bottom: 1rem;">
                <strong>Evolution Complete!</strong><br>
                Best Fitness: ${result.best_fitness.toFixed(3)}<br>
                Best Agent: ${escapeHtml(result.best_agent.name)} (${result.best_agent.agent_id})
            </div>
            <div>
                <strong>Evolution History:</strong>
                ${historyHtml}
            </div>
        `;

        showToast('Evolution completed successfully!', 'success');
        await loadAgents();
    } catch (error) {
        statusDiv.innerHTML = `
            <div style="padding: 1rem; background: rgba(239, 68, 68, 0.1); border-radius: 8px;">
                <strong>Error:</strong> ${escapeHtml(error.message)}
            </div>
        `;
        showToast(`Evolution failed: ${error.message}`, 'error');
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    addChatMessage('user', message);
    input.value = '';

    try {
        const response = await apiCall('/chat', 'POST', {
            message,
            context: null
        });

        addChatMessage('assistant', response.message);
    } catch (error) {
        addChatMessage('assistant', `Error: ${error.message}`);
    }
}

function addChatMessage(role, content) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    // Format content - check if it's JSON and format it nicely
    const formattedContent = formatResult(content);
    
    messageDiv.innerHTML = `
        <div class="message-header">${role === 'user' ? 'You' : 'AI Assistant'}</div>
        <div class="message-content">${formattedContent}</div>
    `;
    messagesDiv.appendChild(messageDiv);
    scrollChatToBottom();
}

function scrollChatToBottom() {
    const messagesDiv = document.getElementById('chatMessages');
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function clearChat() {
    document.getElementById('chatMessages').innerHTML = '';
}

// ========== POLLING & REAL-TIME UPDATES ==========

function startPolling() {
    // Poll every 4 seconds for real-time updates
    pollingInterval = setInterval(async () => {
        if (currentSection === 'agents') {
            await loadAgents();
        } else if (currentSection === 'stats') {
            await loadStats();
        }
        await checkServerStatus();
    }, 4000);
}

function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}

async function loadInitialData() {
    await checkServerStatus();
    await loadAgents();
    await loadTools();
    await loadStats();
    
    // Load agent checkboxes for evolution
    await updateEvolutionCheckboxes();
}

async function updateEvolutionCheckboxes() {
    const checkboxesDiv = document.getElementById('agentCheckboxes');
    const agents = await apiCall('/agents').catch(() => []);
    
    checkboxesDiv.innerHTML = agents.map(agent => `
        <div class="checkbox-item">
            <input type="checkbox" id="agent_${agent.agent_id}" value="${agent.agent_id}">
            <label for="agent_${agent.agent_id}">${escapeHtml(agent.name)}</label>
        </div>
    `).join('');
}

// ========== UTILITY FUNCTIONS ==========

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatResult(result) {
    // If result is null or undefined, return empty string
    if (result === null || result === undefined) {
        return '<span style="color: var(--text-secondary); font-style: italic;">No result</span>';
    }
    
    // If result is already a string
    if (typeof result === 'string') {
        // Check if it looks like JSON (starts with { or [)
        const trimmed = result.trim();
        if ((trimmed.startsWith('{') && trimmed.endsWith('}')) || 
            (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
            // Try to parse as JSON
            try {
                const parsed = JSON.parse(result);
                // If it parsed successfully, format it nicely
                return formatJsonForDisplay(parsed);
            } catch (e) {
                // Not valid JSON, return as plain text
                return '<div style="white-space: pre-wrap; word-wrap: break-word;">' + escapeHtml(result) + '</div>';
            }
        } else {
            // Plain text, return as-is with proper formatting
            return '<div style="white-space: pre-wrap; word-wrap: break-word;">' + escapeHtml(result) + '</div>';
        }
    }
    
    // If result is an object or array, format it as JSON
    if (typeof result === 'object') {
        return formatJsonForDisplay(result);
    }
    
    // For other types (numbers, booleans, etc.), convert to string and escape
    return escapeHtml(String(result));
}

function formatJsonForDisplay(obj) {
    // Format JSON with proper indentation
    try {
        // Handle circular references and large objects
        const seen = new WeakSet();
        const formatted = JSON.stringify(obj, (key, value) => {
            if (typeof value === 'object' && value !== null) {
                if (seen.has(value)) {
                    return '[Circular]';
                }
                seen.add(value);
            }
            // Limit very long strings
            if (typeof value === 'string' && value.length > 1000) {
                return value.substring(0, 1000) + '... [truncated]';
            }
            return value;
        }, 2);
        
        // Escape HTML but preserve formatting
        return '<pre style="background: var(--bg-darker); padding: 1rem; border-radius: 6px; overflow-x: auto; font-family: \'Courier New\', monospace; font-size: 0.9rem; line-height: 1.5; max-height: 400px; overflow-y: auto;">' + 
               escapeHtml(formatted) + 
               '</pre>';
    } catch (e) {
        // If stringify fails, try to get a string representation
        if (obj && typeof obj.toString === 'function') {
            return escapeHtml(obj.toString());
        }
        return escapeHtml(String(obj));
    }
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Handle Enter key in chat
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }
});

// Close modals on outside click
window.addEventListener('click', (e) => {
    const agentModal = document.getElementById('agentModal');
    const taskModal = document.getElementById('taskModal');
    
    if (e.target === agentModal) {
        closeAgentModal();
    }
    if (e.target === taskModal) {
        closeTaskModal();
    }
});
