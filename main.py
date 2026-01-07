from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel


app = FastAPI(Title ="Team Red")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"status": "RED AI backend running"}



class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: str

@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    reply = payload.message
    return {"message": reply}
