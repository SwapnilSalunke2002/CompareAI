import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from groq import Groq  

load_dotenv()

# ENGINE 1: The Static Report Generator
class CompareAIEngine:
    def __init__(self, embeddings, index_name: str = "compare-ai-os"):
        self.embeddings = embeddings 
        self.vector_store = PineconeVectorStore(
            index_name=index_name,
            embedding=self.embeddings,
            namespace="live_comparison" 
        )
        self.llm = ChatGroq(
            temperature=0.1, 
            model_name="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

    def _retrieve_video_context(self, video_tag: str, query: str = "main topic key hooks value proposition") -> str:
        results = self.vector_store.similarity_search(
            query,
            k=3,
            filter={"video_tag": video_tag}
        )
        return "\n---\n".join([doc.page_content for doc in results])

    def generate_comparison_report(self, video_a_meta: Dict[str, Any], video_b_meta: Dict[str, Any]) -> str:
        context_a = self._retrieve_video_context("A")
        context_b = self._retrieve_video_context("B")
        
        # Detect if it is short-form or long-form to give the AI context
        format_a = "Short-form (Short/Reel)" if video_a_meta.get("duration", 0) < 61 else "Long-form Video"
        format_b = "Short-form (Short/Reel)" if video_b_meta.get("duration", 0) < 61 else "Long-form Video"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an elite Social Media Growth Strategist and Content Analyst.\n"
                "Your task is to provide a rigorous, data-backed side-by-side comparison of two videos (Video A and Video B).\n"
                "You must strictly analyze the provided RAG context and respect the video format (Short-form vs Long-form).\n\n"
                "CRITICAL FORMATTING INSTRUCTIONS:\n"
                "- Write a direct, professional report using markdown headers.\n"
                "- Use bolding for emphasis, tables for clear metrics, and blockquotes for script breakdown.\n"
                "- Do not hallucinate content. If the transcript context doesn't mention something, do not invent it."
            )),
            ("user", (
                "### RAW QUANTITATIVE METRICS\n"
                "**Video A ({platform_a} - {format_a})**:\n"
                "- Creator: {creator_a}\n"
                "- Duration: {duration_a} seconds\n"
                "- Engagement Rate: {eng_a}%\n"
                "- Views: {views_a}\n\n"
                "**Video B ({platform_b} - {format_b})**:\n"
                "- Creator: {creator_b}\n"
                "- Duration: {duration_b} seconds\n"
                "- Engagement Rate: {eng_b}%\n"
                "- Views: {views_b}\n\n"
                "--- \n\n"
                "### RETRIEVED CONTENT CONTEXT (RAG CHUNKS)\n"
                "**Video A Transcript Context:**\n{context_a}\n\n"
                "**Video B Transcript Context:**\n{context_b}\n\n"
                "--- \n\n"
                "### REQUIRED ANALYSIS SECTIONS TO GENERATE:\n"
                "1. **Hook & Pacing Breakdown**: Analyze how each video captures attention based on the text.\n"
                "2. **Content & Value Proposition Evaluation**: What are they actually offering/saying?\n"
                "3. **The Engagement Paradox**: Explain why the video with lower views might have a higher engagement rate.\n"
                "4. **Strategic Actionable Takeaways**: 3 clear bullet points."
            ))
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "platform_a": video_a_meta.get("platform"),
            "format_a": format_a,
            "creator_a": video_a_meta.get("creator"),
            "duration_a": video_a_meta.get("duration"),
            "eng_a": video_a_meta.get("engagement_rate"),
            "views_a": video_a_meta.get("views"),
            
            "platform_b": video_b_meta.get("platform"),
            "format_b": format_b,
            "creator_b": video_b_meta.get("creator"),
            "duration_b": video_b_meta.get("duration"),
            "eng_b": video_b_meta.get("engagement_rate"),
            "views_b": video_b_meta.get("views"),
            
            "context_a": context_a,
            "context_b": context_b
        })
        
        return response.content

class StreamingCompareAgent:
    def __init__(self, embeddings, index_name: str = "compare-ai-os"):
        self.embeddings = embeddings  
        self.vector_store = PineconeVectorStore(
            index_name=index_name, 
            embedding=self.embeddings,
            namespace="live_comparison"
        )
        self.llm = ChatGroq(
            temperature=0.1,
            model_name="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

    def get_context(self, query: str) -> str:
        docs = self.vector_store.similarity_search(query, k=4)
        context_blocks = []
        for d in docs:
            tag = d.metadata.get("video_tag", "UNKNOWN")
            creator = d.metadata.get("creator", "N/A")
            idx = d.metadata.get("chunk_index", "0") # <-- Extract Chunk Index
            context_blocks.append(f"[Source: Video {tag}, Chunk {idx} by {creator}]\nContent: {d.page_content}")
        return "\n\n---\n\n".join(context_blocks)

    def stream_chat_turn(self, query: str, history: List[Dict[str, str]], metrics: dict):
        context = self.get_context(query)
        
        system_prompt = f"""You are an elite Social Media Growth & Quant Analyst. 
CRITICAL METRICS DATA:
Video A: {metrics.get('video_a', {})}
Video B: {metrics.get('video_b', {})}

RETRIEVED SOURCE TRANSCRIPT FRAGMENTS:
{context}

RULES:
1. Ground your analysis directly in the provided context and metrics.
2. You MUST explicitly cite the video and the exact chunk index when referencing context (e.g., "[Source: Video A, Chunk 2]").
"""
        # Formulate compliant LangChain base message formats
        messages = [("system", system_prompt)]
        for turn in history:
            messages.append((turn["role"], turn["content"]))
        messages.append(("user", query))
        
        # Use LangChain's unified stream engine interface
        for chunk in self.llm.stream(messages):
            if chunk.content:
                yield chunk.content