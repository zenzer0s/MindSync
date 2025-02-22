from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import metadata, urls, users

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(metadata.router)
app.include_router(urls.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to MetaMind Bot API"}