FROM python:3.10-slim
WORKDIR /app

# Install dependencies first (cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest
COPY . .

# Start the bot
CMD ["python", "bot.py"]
