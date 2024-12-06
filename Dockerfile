FROM python:3.10-slim

WORKDIR /apps/tgbot

# Copy all files into the container
COPY . /apps/tgbot

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot
CMD ["python", "bot.py"]
