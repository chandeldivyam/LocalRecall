# Use NVIDIA CUDA base image
FROM huggingface/transformers-pytorch-gpu:4.41.2

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY src/api/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the API code
COPY src/api /app/api

# Set the Python path
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 8989

# Command to run the API server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8989"]