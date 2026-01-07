from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from datetime import datetime


# Load environment variables from a .env file if present
load_dotenv()


app = FastAPI(title="Team Red")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Instantiate the LangChain OpenAI chat model
llm = ChatOpenAI(
    model="gpt-4o-mini",  # You can change to another OpenAI chat model if needed
    temperature=0.7,
)


@app.get("/")
async def health():
    return {"status": "RED AI backend running"}


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    message: str

@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        prompt = f"""
The current date and time is: {now}

User message:
{payload.message}
"""

        result = await llm.ainvoke(prompt)
        return {"message": result.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
