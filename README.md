# CompareAI 🚀
### *Elite Full-Stack RAG Video Cross-Examination Engine*

CompareAI is a high-performance, dynamic RAG (Retrieval-Augmented Generation) application built to extract, embed, index, and cross-examine multimedia content from YouTube and Instagram Reels simultaneously. 

The architecture is explicitly engineered to minimize infrastructure expenses, ensuring zero-pollution data indexing for high-volume content creators.

---

## 🏗️ Architectural Trade-Offs & Scalability Defense
This application was designed with a production-first mindset to scale cleanly to **1,000+ daily analytical actions** at the lowest possible cost structure.

### 1. The Embedding Layer (Zero Token Burning)
* **Standard Approach:** Developers default to cloud-hosted APIs like `text-embedding-3-small` from OpenAI, running up continuous API token debts for chunking large text transcripts.
* **Our Engineered Solution:** We decoupled the embedding pipeline and deployed the open-source `all-MiniLM-L6-v2` transformer model directly inside the local backend runtime environment via HuggingFace. Vector computation costs are reduced to **exactly $0.00**. Furthermore, its highly effective 384-dimensional output reduces storage requirements inside our Vector engine by over 75% compared to OpenAI’s 1536-dimension vectors.

### 2. Multi-Tenant Vector Db Footprint Optimization
* **Standard Approach:** Generating a unique vector index per user query or persistently hoarding thousands of transcripts quickly exhausts database boundaries and incurs massive infrastructure expenses.
* **Our Engineered Solution:** We isolated active user operations within a singular, ephemeral Pinecone namespace: `live_comparison`. When a fresh analysis payload hits our gateway endpoint, the system invokes an immediate flushing mechanism:
  ```python
  index.delete(delete_all=True, namespace="live_comparison")