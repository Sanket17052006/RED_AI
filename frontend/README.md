# RED AI Frontend Dashboard

## Quick Start

1. **Start your backend server:**
   ```bash
   cd backend
   python run.py
   ```

2. **Access the dashboard:**
   Open your browser and navigate to:
   ```
   http://localhost:8000/dashboard
   ```

## Backend URL Configuration

### Option 1: Auto-Detection (Default - Recommended)
The frontend automatically detects the backend URL when accessed via the backend server. No configuration needed!

### Option 2: Manual Configuration
If you need to set a custom backend URL, edit `script.js`:

**Location:** `backend/frontend/script.js`

**Find this line (around line 6):**
```javascript
const BACKEND_URL = '';
```

**Change it to:**
```javascript
const BACKEND_URL = 'http://your-backend-url:8000';
```

**Example:**
```javascript
const BACKEND_URL = 'http://192.168.1.100:8000';  // For remote backend
// OR
const BACKEND_URL = 'http://localhost:8000';       // For local backend
```

### Important Note about .env Files
⚠️ **Frontend JavaScript cannot directly read from `.env` files** because it runs in the browser (client-side). 

The `.env` file is for **backend configuration only**. For the frontend:
- Use auto-detection (recommended)
- Or manually set `BACKEND_URL` in `script.js` as shown above

## Features

✅ View all AI agents with real-time statistics  
✅ Create new agents with custom prompts  
✅ Execute tasks with any agent  
✅ Evolve agents using genetic algorithms  
✅ Chat interface for quick interactions  
✅ View available tools  
✅ System-wide statistics  
✅ Auto-refresh every 4 seconds  

## Real-time Updates

The dashboard automatically polls the backend every **4 seconds** to keep data up-to-date. All changes are reflected within 3-5 seconds.

