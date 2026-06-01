import os
from typing import List, Dict
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from extractor import VideoMetadata, extract_all_video_data

load_dotenv()

class RAGIndexer:
    def __init__(self, embeddings, index_name: str = "compare-ai-os"):
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = index_name
        self.namespace = "live_comparison" 
        
        self.embeddings = embeddings  # <-- Accept passed shared instance
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        existing_indexes = [index_info["name"] for index_info in self.pc.list_indexes()]
        if self.index_name not in existing_indexes:
            print(f"🛠️ Creating new serverless Pinecone index: '{self.index_name}'...")
            self.pc.create_index(
                name=self.index_name,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print("✅ Index created successfully.")
        else:
            print(f"✅ Found existing index: '{self.index_name}'")

    def process_and_tag(self, extracted_data: Dict[str, VideoMetadata]) -> List[Document]:
        docs = []
        for video_label, video_data in extracted_data.items(): 
            full_text = f"Title: {video_data.title}\nTranscript: {video_data.transcript}"
            chunks = self.text_splitter.split_text(full_text)
            
            for i, chunk in enumerate(chunks):
                metadata = {
                    "video_tag": "A" if "A" in video_label else "B",
                    "video_id": video_data.video_id,
                    "platform": video_data.platform,
                    "creator": video_data.creator,
                    "engagement_rate": video_data.engagement_rate,
                    "chunk_index": i
                }
                docs.append(Document(page_content=chunk, metadata=metadata))
                
        print(f"🧩 Split text into {len(docs)} tagged chunks.")
        return docs

    def index_to_vector_db(self, docs: List[Document]):
        """Wipes the old context clean, then embeds and uploads the new vectors."""
        print("🧹 Wiping previous video data from Vector DB...")
        try:
            index = self.pc.Index(self.index_name)
            index.delete(delete_all=True, namespace=self.namespace)
        except Exception as e:
            print(f"⚠️ Note on cleanup (Expected on first run): {e}")

        print(f"📤 Uploading {len(docs)} fresh chunks to Pinecone...")
        PineconeVectorStore.from_documents(
            documents=docs,
            embedding=self.embeddings,
            index_name=self.index_name,
            namespace=self.namespace 
        )
        print("✅ Successfully indexed fresh data into Vector DB.")

if __name__ == "__main__":
    # Test block
    sample_yt = "https://www.youtube.com/shorts/dQw4w9WgXcQ" 
    sample_ig = "https://www.instagram.com/reels/DYQSPVCT_V-/"
    raw_data = extract_all_video_data(sample_yt, sample_ig)
    indexer = RAGIndexer()
    tagged_documents = indexer.process_and_tag(raw_data)
    indexer.index_to_vector_db(tagged_documents)