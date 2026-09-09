# Use lightweight Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install dependencies first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Command to run the dashboard
CMD ["streamlit", "run", "frontend/frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]