FROM python:3.11-slim

# Set up a clean working directory
WORKDIR /code

# Copy and install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of your application code
COPY . .

# Pre-download the embedding weights during the build phase so container starts instantly
RUN python -c "from langchain_huggingface import HuggingFaceEmbeddings; HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')"

# Hugging Face Spaces strictly requires port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]