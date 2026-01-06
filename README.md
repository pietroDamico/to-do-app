# To-Do App

This repo serves the purpose of testing agents capabilities. It will be completely managed by an agent guided by human feedback.

## Project Structure

```
to-do-app/
├── docs/
│   ├── requirements/
│   │   └── requirements-v1.md          # Requirements document (REQ-001 to REQ-007)
│   └── ll-agent-prompt.md              # Instructions for LL implementation agents
├── backend/                             # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py                     # Basic FastAPI app skeleton
│   ├── requirements.txt                # Python dependencies
│   ├── .env.example                    # Environment variables template
│   └── README.md
├── frontend/                            # React frontend
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx                     # Basic React app skeleton
│   │   └── App.css
│   ├── package.json                    # Node dependencies
│   ├── vite.config.js
│   ├── index.html
│   ├── .env.example
│   └── README.md
└── README.md                            # This file
```

## Technology Stack

- **Backend**: Python + FastAPI, PostgreSQL, SQLAlchemy, JWT authentication
- **Frontend**: React, React Router, Axios, Vite
- **Testing**: pytest (backend), Vitest + React Testing Library (frontend)

## Development Workflow

This project uses a coordinated agent-based development workflow:

1. **Requirements** → Documented in `docs/requirements/requirements-v1.md`
2. **Epics** → GitHub issues with `epic` label (#1, #2)
3. **Tasks** → GitHub issues linked to epics (#3-#10)
4. **Implementation** → LL agents implement tasks following `docs/ll-agent-prompt.md`
5. **Pull Requests** → With full traceability to tasks, epics, and requirements
6. **Review & Merge** → HL agent or human review

## Current Epics

### Epic #1: User Authentication System
- REQ-001: User Registration
- REQ-002: User Login  
- REQ-003: User Logout

**Tasks**: #3 through #10 (8 tasks total)

### Epic #2: To-Do List Management
- REQ-004: Create To-Do Item
- REQ-005: View To-Do List
- REQ-006: Mark To-Do Item as Complete
- REQ-007: Delete To-Do Item

**Tasks**: To be created

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
uvicorn app.main:app --reload
```

Visit: http://localhost:8000/docs for API documentation

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with backend API URL
npm run dev
```

Visit: http://localhost:5173

## For LL Agents

If you're an LL agent assigned to implement a task:

1. Read `docs/ll-agent-prompt.md` for complete instructions
2. Find your assigned issue: `gh issue list --assignee @me`
3. Implement following the task specification
4. Write tests (80% coverage minimum)
5. Create PR with full traceability

## Documentation

- **Requirements**: `docs/requirements/requirements-v1.md`
- **LL Agent Instructions**: `docs/ll-agent-prompt.md`
- **Backend README**: `backend/README.md`
- **Frontend README**: `frontend/README.md`

## Traceability

Every piece of work traces back to requirements:

```
Code → PR → Task (Issue) → Epic (Issue) → Requirements (REQ-xxx) → requirements-v1.md
```

Example: A login endpoint implementation will reference:
- Task #6
- Epic #1 
- REQ-002 (User Login)
