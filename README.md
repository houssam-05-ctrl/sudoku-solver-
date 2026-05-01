# Full-Stack AI Sudoku Solver

An interactive Sudoku solver built with React and a FastAPI Python backend using AC-3 constraint propagation and heuristic backtracking search.

## Setup & Run Instructions

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

_API will run on http://localhost:8000_

### 2. Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

_Frontend will typically run on http://localhost:5173_
