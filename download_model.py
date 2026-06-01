import os
from langchain_huggingface import HuggingFaceEmbeddings

print("📦 Pre-downloading model weights to cache...")
# This forces HuggingFace to fetch the files and write them to disk
HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print("✅ Embedding model weights cached successfully!")