FROM python:3.9-slim

# Install system dependencies (wget, gnupg, unzip)
RUN apt-get update && apt-get install -y wget gnupg2 unzip curl

# Add Google Chrome repository and install Google Chrome Stable
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set up the working directory
WORKDIR /app

# Copy the requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Start the web server using Uvicorn
CMD ["uvicorn", "web_app:app", "--host", "0.0.0.0", "--port", "8000"]
