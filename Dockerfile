FROM python:3.11-slim

# Graphics aur Audio (pyttsx3) ke Linux drivers taaki hidden crash na ho
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    alsa-utils \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render ka default Web Service port
EXPOSE 10000

# Streamlit ko explicitly 10000 port aur 0.0.0.0 host par chalana
CMD ["streamlit", "run", "frontend/frontend.py", "--server.port=10000", "--server.address=0.0.0.0"]