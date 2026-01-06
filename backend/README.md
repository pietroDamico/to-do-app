# To-Do App Backend

FastAPI backend for the to-do application.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials and secret key
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

API will be available at http://localhost:8000

API documentation: http://localhost:8000/docs

## Testing

```bash
pytest --cov=app
```