import os
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from langchain_huggingface import HuggingFaceEmbeddings

# Import your architectural pieces
from extractor import extract_all_video_data
from indexer import RAGIndexer
from agent import CompareAIEngine, StreamingCompareAgent 

app = FastAPI(title="CompareAI Core Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models 
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

# --- CLEAN GLOBAL INITIALIZATION (16GB RAM Safe) ---
print("⏳ Initializing Global Shared Embedding Engine...")
shared_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

print("🗂️ Initializing Sub-Services...")
rag_indexer = RAGIndexer(embeddings=shared_embeddings)
engine = CompareAIEngine(embeddings=shared_embeddings)
streaming_agent = StreamingCompareAgent(embeddings=shared_embeddings)
print("✅ All AI Engines Loaded and Ready!")

def helper_to_dict(obj):
    if obj is None: return {}
    if isinstance(obj, dict): return obj
    if hasattr(obj, "__dict__"): return obj.__dict__
    return str(obj)

# ROUTE 1: Initial Extraction & Indexing ---
@app.post("/api/compare")
async def compare_videos(request: ComparisonRequest):
    try:
        print("\n" + "="*50)
        print(f"📥 RECEIVED REQUEST:\nURL A: {request.video_url_a}\nURL B: {request.video_url_b}")
        
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

# ROUTE 2: Interactive RAG Chat Stream ---
@app.post("/api/chat/stream")
async def chat_stream_endpoint(request: ChatTurnRequest):
    try:
        formatted_history = [{"role": m.role, "content": m.content} for m in request.history]
        return StreamingResponse(
            streaming_agent.stream_chat_turn(request.query, formatted_history, request.metrics),
            media_type="text/event-stream"
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))