from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="To-Do App API",
    description="A simple to-do list application with user authentication",
    version="1.0.0"
)

# CORS configuration - to be configured properly in task #3
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "To-Do App API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}