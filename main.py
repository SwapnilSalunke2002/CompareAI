import os
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

# Import your architectural pieces
from extractor import extract_all_video_data
from indexer import RAGIndexer
from agent import CompareAIEngine, StreamingCompareAgent # <-- Make sure to add StreamingCompareAgent to agent.py

app = FastAPI(title="CompareAI Core Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Models ---
class ComparisonRequest(BaseModel):
    video_url_a: str
    video_url_b: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatTurnRequest(BaseModel):
    query: str
    history: List[ChatMessage]
    metrics: dict

# --- GLOBAL INITIALIZATION (The Scaling Secret) ---
# We load these heavy models into memory once at startup. 
# Now, routing requests takes milliseconds, not seconds.
print("⏳ Initializing AI Engines (Loading HuggingFace models)...")
rag_indexer = RAGIndexer()
engine = CompareAIEngine()
streaming_agent = StreamingCompareAgent()
print("✅ AI Engines Ready!")

def helper_to_dict(obj):
    if obj is None: return {}
    if isinstance(obj, dict): return obj
    if hasattr(obj, "__dict__"): return obj.__dict__
    return str(obj)

# --- ROUTE 1: Initial Extraction & Indexing ---
@app.post("/api/compare")
async def compare_videos(request: ComparisonRequest):
    try:
        print("\n" + "="*50)
        print(f"📥 RECEIVED NEW REQUEST:\nURL A: {request.video_url_a}\nURL B: {request.video_url_b}")
        
        print("⚡ Phase 1: Extractor...")
        raw_data = extract_all_video_data(request.video_url_a, request.video_url_b)
        
        video_a_meta = helper_to_dict(raw_data.get("video_A") or raw_data.get("Video A"))
        video_b_meta = helper_to_dict(raw_data.get("video_B") or raw_data.get("Video B"))
        
        print("🗂️ Phase 2: Vector DB Ingestion...")
        tagged_documents = rag_indexer.process_and_tag(raw_data)
        rag_indexer.index_to_vector_db(tagged_documents)
        
        print("🤖 Phase 3: Groq Reasoning Agent...")
        report_markdown = engine.generate_comparison_report(video_a_meta, video_b_meta)
        print("✅ Report Generated!")
        print("="*50)
        
        return {
            "success": True,
            "metrics": {
                "video_a": video_a_meta,
                "video_b": video_b_meta
            },
            "report": report_markdown
        }
    except Exception as e:
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=str(e))

# --- ROUTE 2: Interactive RAG Chat Stream ---
@app.post("/api/chat/stream")
async def chat_stream_endpoint(request: ChatTurnRequest):
    try:
        # Parse history cleanly for the LangChain/Groq agent
        formatted_history = [{"role": m.role, "content": m.content} for m in request.history]
        
        # Call the globally initialized agent
        return StreamingResponse(
            streaming_agent.stream_chat_turn(request.query, formatted_history, request.metrics),
            media_type="text/event-stream"
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)