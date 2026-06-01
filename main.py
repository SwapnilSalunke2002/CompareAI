import os
import traceback
import asyncio
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

# --- NON-BLOCKING INITIALIZATION LAYERS ---
shared_embeddings = None
rag_indexer = None
engine = None
streaming_agent = None
is_ready = False

async def background_warm_up():
    """Loads the model from disk cache into RAM asynchronously.
    This protects incoming requests from hitting timeout bounds.
    """
    global shared_embeddings, rag_indexer, engine, streaming_agent, is_ready
    try:
        print("⏳ Background Worker: Mounting cached model into RAM...")
        shared_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        rag_indexer = RAGIndexer(embeddings=shared_embeddings)
        engine = CompareAIEngine(embeddings=shared_embeddings)
        streaming_agent = StreamingCompareAgent(embeddings=shared_embeddings)
        is_ready = True
        print("🚀 Background Worker: AI Engines loaded in memory successfully!")
    except Exception as e:
        print(f"❌ Background Worker Error: Failed to load models: {e}")

@app.on_event("startup")
async def startup_event():
    # Instantly yields control back to Uvicorn so the port opens immediately
    asyncio.create_task(background_warm_up())

def check_engine_health():
    """Fails defensively if a user hits the application before RAM is ready."""
    if not is_ready:
        raise HTTPException(
            status_code=503, 
            detail="AI Engine is still initializing. Please retry in 5 seconds."
        )
    return rag_indexer, engine, streaming_agent

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
        print(f"📥 REQUEST:\nURL A: {request.video_url_a}\nURL B: {request.video_url_b}")
        
        # Verify background states are active
        indexer_inst, engine_inst, _ = check_engine_health()
        
        print("⚡ Phase 1: Extractor...")
        raw_data = extract_all_video_data(request.video_url_a, request.video_url_b)
        
        video_a_meta = helper_to_dict(raw_data.get("video_A") or raw_data.get("Video A"))
        video_b_meta = helper_to_dict(raw_data.get("video_B") or raw_data.get("Video B"))
        
        print("🗂️ Phase 2: Vector DB Ingestion...")
        tagged_documents = indexer_inst.process_and_tag(raw_data)
        indexer_inst.index_to_vector_db(tagged_documents)
        
        print("🤖 Phase 3: Groq Reasoning Agent...")
        report_markdown = engine_inst.generate_comparison_report(video_a_meta, video_b_meta)
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
        
        _, _, agent_inst = check_engine_health()
        
        return StreamingResponse(
            agent_inst.stream_chat_turn(request.query, formatted_history, request.metrics),
            media_type="text/event-stream"
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))