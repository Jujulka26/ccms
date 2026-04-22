from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import counselors, auth, requests, matching, model_performance

app = FastAPI(title="Client-Counselor Matching System API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(counselors.router)
app.include_router(auth.router)
app.include_router(requests.router)
app.include_router(matching.router)
app.include_router(model_performance.router)


@app.get("/")
def root():
    return {"message": "Client-Counselor Matching System API is running."}
