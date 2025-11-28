# Installation Guide

This guide covers the installation and setup of the Eriska IoT Security Platform. The platform consists of three main components:
1.  **Backend** (Django/Python)
2.  **Frontend** (Next.js/Node.js)
3.  **Security Agent** (Python)

---

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.8+**: Required for Backend and Agent.
*   **Node.js 18+**: Required for Frontend.
*   **Git**: For cloning the repository.
*   **Docker** (Optional): For running Redis and PostgreSQL easily.

---

## 1. Backend Setup

The backend is the core of the system, handling API requests and data storage.

### Step 1: Navigate to Backend Directory
```bash
cd backend
```

### Step 2: Create Virtual Environment
It's recommended to use a virtual environment to manage dependencies.
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Database
By default, the project uses SQLite. If you want to use PostgreSQL, update the `DATABASES` setting in `backend/settings.py`.

### Step 5: Run Migrations
```bash
python manage.py migrate
```

### Step 6: Start the Server
```bash
python manage.py runserver
```
The backend will be available at `http://localhost:8000`.

---

## 2. Frontend Setup

The frontend provides the dashboard for visualizing security data.

### Step 1: Navigate to Frontend Directory
```bash
cd front/eriska
```

### Step 2: Install Dependencies
```bash
npm install
# or
yarn install
```

### Step 3: Configure Environment
Create a `.env.local` file if you need to override the backend URL (default is `http://localhost:8000`).

### Step 4: Start Development Server
```bash
npm run dev
```
The dashboard will be available at `http://localhost:3000`.

---

## 3. Security Agent Setup

The agent performs the actual network scanning and security analysis.

### Step 1: Navigate to Agent Directory
```bash
cd agent
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Agent
You can run the agent in various modes.

**AI Mode (Recommended):**
```bash
python main.py --mode ai --api-key YOUR_GEMINI_API_KEY
```

**Active Network Scan:**
```bash
python main.py --mode active
```

For more details on agent usage, see the [Agent Documentation](agent-v2.md).

---

## Troubleshooting

### Common Issues

*   **Port Conflicts**: Ensure ports 3000 (Frontend) and 8000 (Backend) are free.
*   **Missing API Key**: The AI mode requires a valid Google Gemini API key.
*   **Permission Denied**: On Linux/macOS, network scanning (ARP) might require `sudo`.

### Getting Help
If you encounter issues, please open an issue on our [GitHub Repository](https://github.com/ghasemmazandarani/eriska/issues).
