FROM python:3.11-slim

# Yeh command Linux ke saare missing graphics drivers ek baar mein install kar degi
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8508
CMD ["streamlit", "run", "frontend/frontend.py", "--server.port=10000", "--server.address=0.0.0.0"]

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