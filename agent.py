import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

class CompareAIEngine:
    def __init__(self, index_name: str = "compare-ai-os"):
        # 1. Initialize the same local embedding model used for indexing
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # 2. Connect to the existing Pinecone Index
        self.vector_store = PineconeVectorStore(
            index_name=index_name,
            embedding=self.embeddings
        )
        
        # 3. Initialize Groq with Llama 3.3 70B for high-quality reasoning
        self.llm = ChatGroq(
            temperature=0.2,
            model_name="llama-3.3-70b-versatile",  # Updated model identifier
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

    def _retrieve_video_context(self, video_tag: str, query: str = "main topic key hooks value proposition") -> str:
        """Queries Pinecone specifically filtering for either Video A or Video B."""
        # We use Pinecone's metadata filtering to avoid data cross-contamination
        results = self.vector_store.similarity_search(
            query,
            k=3,
            filter={"video_tag": video_tag}
        )
        
        # Combine retrieved chunks into a singular context string
        return "\n---\n".join([doc.page_content for doc in results])

    def generate_comparison_report(self, video_a_meta: Dict[str, Any], video_b_meta: Dict[str, Any]) -> str:
        """Orchestrates RAG retrieval and metric evaluation to generate the final report."""
        print("🔍 Querying Vector DB for Video A context...")
        context_a = self._retrieve_video_context("A")
        
        print("🔍 Querying Vector DB for Video B context...")
        context_b = self._retrieve_video_context("B")
        
        print("🤖 Orchestrating Groq Reasoning Agent...")
        
        # System prompt explicitly instructing the agent to do cross-examination
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
                "- Views: {views_a}\n"
                "- Likes: {likes_a}\n\n"
                "**Video B ({platform_b})**:\n"
                "- Creator: {creator_b}\n"
                "- Engagement Rate: {eng_b}%\n"
                "- Views: {views_b}\n"
                "- Likes: {likes_b}\n\n"
                "--- \n\n"
                "### RETRIEVED CONTENT CONTEXT (RAG CHUNKS)\n"
                "**Video A Transcript Context:**\n{context_a}\n\n"
                "**Video B Transcript Context:**\n{context_b}\n\n"
                "--- \n\n"
                "### REQUIRED ANALYSIS SECTIONS TO GENERATE:\n"
                "1. **Side-by-Side Metric Dashboard**: A markdown table comparing views, likes, and engagement rates.\n"
                "2. **Hook & Pacing Breakdown**: Analyze how each video captures attention in the first 3 seconds based on the context.\n"
                "3. **Content & Value Proposition Evaluation**: What are they actually offering/saying? Which script is tighter?\n"
                "4. **The Engagement Paradox**: Explain why the video with lower views might have a higher engagement rate, and what that means for monetization or growth.\n"
                "5. **Strategic Actionable Takeaways**: 3 clear bullet points on what Creator A can learn from Creator B, and vice-versa."
            ))
        ])
        
        # Chain composition
        chain = prompt | self.llm
        
        response = chain.invoke({
            "platform_a": video_a_meta.get("platform"),
            "creator_a": video_a_meta.get("creator"),
            "eng_a": video_a_meta.get("engagement_rate"),
            "views_a": video_a_meta.get("views"),
            "likes_a": video_a_meta.get("likes"),
            
            "platform_b": video_b_meta.get("platform"),
            "creator_b": video_b_meta.get("creator"),
            "eng_b": video_b_meta.get("engagement_rate"),
            "views_b": video_b_meta.get("views"),
            "likes_b": video_b_meta.get("likes"),
            
            "context_a": context_a,
            "context_b": context_b
        })
        
        return response.content

if __name__ == "__main__":
    # Mock metadata dictionaries mapping directly to what our extractor outputs
    # This allows us to test the agent stand-alone instantly
    mock_video_a = {
        "platform": "youtube",
        "creator": "Rick Astley",
        "engagement_rate": 1.21,
        "views": 1777703298,
        "likes": 19127911
    }
    
    mock_video_b = {
        "platform": "instagram",
        "creator": "kasumbi_by_anju",
        "engagement_rate": 2.68,
        "views": 47473,
        "likes": 1273
    }
    
    engine = CompareAIEngine()
    report = engine.generate_comparison_report(mock_video_a, mock_video_b)
    
    print("\n================== FINAL AI REPORT ==================\n")
    print(report)