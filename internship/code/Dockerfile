# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Copy toolkit and install it first
COPY langchain-ritual-toolkit /app/langchain-ritual-toolkit
RUN cd /app/langchain-ritual-toolkit && pip install .

# Copy project files
COPY src /app/src
COPY pyproject.toml /app
# Install package
RUN pip install .

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose the API port
EXPOSE 8000

# Default command to run the FastAPI server
CMD ["uvicorn", "staking_optimizer.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
