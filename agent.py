import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from groq import Groq  # The native Groq client for streaming

load_dotenv()

# ==========================================
# ENGINE 1: The Static Report Generator
# ==========================================
class CompareAIEngine:
    def __init__(self, index_name: str = "compare-ai-os"):
        # Local open-source embeddings (Zero cost)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = PineconeVectorStore(
            index_name=index_name,
            embedding=self.embeddings
        )
        self.llm = ChatGroq(
            temperature=0.2,
            model_name="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

    def _retrieve_video_context(self, video_tag: str, query: str = "main topic key hooks value proposition") -> str:
        """Queries Pinecone specifically filtering for either Video A or Video B."""
        results = self.vector_store.similarity_search(
            query,
            k=3,
            filter={"video_tag": video_tag}
        )
        return "\n---\n".join([doc.page_content for doc in results])

    def generate_comparison_report(self, video_a_meta: Dict[str, Any], video_b_meta: Dict[str, Any]) -> str:
        """Generates the initial static markdown breakdown."""
        context_a = self._retrieve_video_context("A")
        context_b = self._retrieve_video_context("B")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an elite Social Media Growth Strategist and Content Analyst.\n"
                "Your task is to provide a rigorous, data-backed side-by-side comparison of two videos (Video A and Video B).\n"
                "You must look past shallow view counts and analyze conversion hooks, script pacing, and actual audience retention indicators.\n\n"
                "CRITICAL FORMATTING INSTRUCTIONS:\n"
                "- Write a direct, professional report using markdown headers.\n"
                "- Use bolding for emphasis, tables for clear metrics, and blockquotes for script breakdown.\n"
                "- Do not output conversational filler or intro/outro pleasantries. Go straight into the analysis."
            )),
            ("user", (
                "### RAW QUANTITATIVE METRICS\n"
                "**Video A ({platform_a})**:\n"
                "- Creator: {creator_a}\n"
                "- Engagement Rate: {eng_a}%\n"
                "- Views: {views_a}\n\n"
                "**Video B ({platform_b})**:\n"
                "- Creator: {creator_b}\n"
                "- Engagement Rate: {eng_b}%\n"
                "- Views: {views_b}\n\n"
                "--- \n\n"
                "### RETRIEVED CONTENT CONTEXT (RAG CHUNKS)\n"
                "**Video A Transcript Context:**\n{context_a}\n\n"
                "**Video B Transcript Context:**\n{context_b}\n\n"
                "--- \n\n"
                "### REQUIRED ANALYSIS SECTIONS TO GENERATE:\n"
                "1. **Hook & Pacing Breakdown**: Analyze how each video captures attention in the first 3 seconds based on the context.\n"
                "2. **Content & Value Proposition Evaluation**: What are they actually offering/saying? Which script is tighter?\n"
                "3. **The Engagement Paradox**: Explain why the video with lower views might have a higher engagement rate, and what that means for monetization or growth.\n"
                "4. **Strategic Actionable Takeaways**: 3 clear bullet points on what Creator A can learn from Creator B, and vice-versa."
            ))
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "platform_a": video_a_meta.get("platform"),
            "creator_a": video_a_meta.get("creator"),
            "eng_a": video_a_meta.get("engagement_rate"),
            "views_a": video_a_meta.get("views"),
            
            "platform_b": video_b_meta.get("platform"),
            "creator_b": video_b_meta.get("creator"),
            "eng_b": video_b_meta.get("engagement_rate"),
            "views_b": video_b_meta.get("views"),
            
            "context_a": context_a,
            "context_b": context_b
        })
        
        return response.content

# ==========================================
# ENGINE 2: The Interactive Streaming Agent
# ==========================================
class StreamingCompareAgent:
    def __init__(self, index_name: str = "compare-ai-os"):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = PineconeVectorStore(
            index_name=index_name, 
            embedding=self.embeddings
        )
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def get_context(self, query: str) -> str:
        """Retrieves raw relevant context text blocks along with source document metadata."""
        docs = self.vector_store.similarity_search(query, k=4)
        context_blocks = []
        for d in docs:
            tag = d.metadata.get("video_tag", "UNKNOWN")
            creator = d.metadata.get("creator", "N/A")
            context_blocks.append(f"[Source: Video {tag} by {creator}]\nContent: {d.page_content}")
        return "\n\n---\n\n".join(context_blocks)

    def stream_chat_turn(self, query: str, history: List[Dict[str, str]], metrics: dict):
        """Streams tokens from Groq while enforcing cross-examination guidelines and source citations."""
        context = self.get_context(query)
        
        system_prompt = f"""You are an elite Social Media Growth & Quant Analyst. Your task is to conduct an interactive cross-examination of two videos based on retrieved transcript context and live engagement metrics.

CRITICAL METRICS DATA:
Video A: {metrics.get('video_a', {})}
Video B: {metrics.get('video_b', {})}

RETRIEVED SOURCE TRANSCRIPT FRAGMENTS:
{context}

RULES:
1. Always ground your analysis directly in the metrics data and the provided transcript context fragments.
2. You MUST explicitly cite your sources when using transcript context (e.g., "[Source: Video A]").
3. Maintain a technical, high-signal, zero-fluff tone. Focus on hooks, pacing, structure, and retention strategies.
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        for turn in history:
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": query})
        
        completion = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.2,
            stream=True
        )
        
        for chunk in completion:
            token = chunk.choices[0].delta.content
            if token:
                yield token