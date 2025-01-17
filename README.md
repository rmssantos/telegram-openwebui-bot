# Telegram OpenWebUI Bot

This project integrates a Telegram bot with [OpenWebUI](https://github.com/OpenWebUI/open-webui), enabling interaction with an AI model directly through Telegram. It supports conversational commands, chat summaries, image analysis, sentiment analysis, and context-aware interactions.

## Features

- **`/chat <message>`**: Engage with the bot and receive AI-generated responses.
- **`/summarize`**: Summarize recent group messages with AI-driven insights.
- **`/sentiment`**: Perform group sentiment analysis.
- **Image Analysis**: Upload an image to get an AI-powered analysis.
- **Contextual AI**: Responses are enriched with chat history and group-specific context.

---

## Prerequisites

### **1. Telegram Bot Token**
- Obtain a bot token via [BotFather](https://core.telegram.org/bots#botfather) on Telegram.
- Use the `/newbot` command and follow the setup instructions to receive your API key.

### **2. OpenWebUI**
- Install OpenWebUI from the [OpenWebUI GitHub repository](https://github.com/OpenWebUI/open-webui).
- Start the OpenWebUI server and note the URL (e.g., `http://localhost:3000/api`).

### **3. Python 3.10+**
- Ensure Python 3.10 or later is installed on your system.

### **4. Optional APIs**
- **Azure OpenAI API**: For integration with Azure-hosted AI models.
- **Bing Search API**: For enhanced search capabilities. Obtain an API key [here](https://www.microsoft.com/en-us/bing/apis/bing-search-api-v7).

---

## Installation & Setup

### **1. Clone the Repository**

```bash
git clone https://github.com/rmssantos/telegram-openwebui-bot.git
cd telegram-openwebui-bot
```

### **2. Configure the `.env` File**

- Copy the example file and edit it with your configuration:

```bash
cp .env.example .env
```

- Update the `.env` file with your details:

```env
# Telegram Bot API Key from BotFather
API_KEY=<YOUR_API_KEY>

# OPENWEBUI API
OPENWEBUI_BASE_URL=http://<OPENWEBUI_BASE_URL>:3000/api
OPENWEBUI_API_KEY=<OPENWEBUI_API_KEY>

# Azure OpenAI API
ENDPOINT_URL=https://<YOUR_ENDPOINT_URL>.openai.azure.com/
AZURE_OPENAI_API_KEY=<YOUR_AZURE_OPENAI_API_KEY>

# Custom configs
MODEL_NAME=<OPENAI_MODEL_NAME>
MAX_TOKENS=750
TEMPERATURE=0.7

# Knowledge Base Collection IDs
EXAMPLE_KB_ID=<YOUR_COLLECTION_ID>
EXAMPLE_KB_ID2=<YOUR_COLLECTION_ID>

# Logging Level
LOG_LEVEL=DEBUG

# History and Rotation Configuration
HISTORY_LENGTH=15
ROTATION_THRESHOLD_HOURS=12
MAX_GROUP_MESSAGES=2000
PERSIST_INTERVAL=15
MAX_CHANGES_BEFORE_PERSIST=3

# Cooldown Configuration
COOLDOWN_MINUTES=1

# Chunk Size for Sentiment Analysis
BASE_CHUNK_SIZE=6000

# Bing Search Key
BING_SEARCH_KEY=<YOUR_BING_SEARCH_KEY>
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4. Prepare SQLite Database**

Create an empty database file for the bot:

```bash
touch bot_data.db
```

### **5. Run the Bot**

```bash
python bot.py
```

- The bot will start listening for messages. Test it by sending a message on Telegram.

---

## Docker Setup

### **1. Build the Docker Image**

```bash
docker build -t telegram-openwebui-bot .
```

### **2. Prepare the SQLite Database File**

Before running the container, ensure the SQLite database file exists in the working directory. Create an empty file with:

```bash
touch bot_data.db
```

### **3. Run the Docker Container**

Run the container with the following command:

```bash
docker run -d \
  --env-file $(pwd)/.env \
  -v $(pwd)/bot_data.db:/apps/telegram-openwebui-bot/bot_data.db \
  --name telegram_openwebui_bot \
  telegram-openwebui-bot
```

### **4. Stop and Remove the Container**

To stop the container:

```bash
docker stop telegram_openwebui_bot
```

To remove the container:

```bash
docker rm telegram_openwebui_bot
```

---

## Commands

- **`/chat <message>`**: Chat with the bot using OpenWebUI.
- **`/summarize`**: Get a structured summary of recent group messages.
- **`/sentiment`**: Analyze the sentiment of recent group messages.
- **Image Analysis**: Upload an image to get insights.

---

## Environment Variables

- `API_KEY`: Telegram bot token from BotFather.
- `OPENWEBUI_BASE_URL`: Base URL of the OpenWebUI server.
- `OPENWEBUI_API_KEY`: API key for OpenWebUI, if applicable.
- `MODEL_NAME`: Model name to use with OpenWebUI.
- `MAX_TOKENS`: Maximum tokens for AI responses.
- `TEMPERATURE`: Sampling temperature for AI.
- `HISTORY_LENGTH`: Number of messages to keep for context.
- `CUSTOM1_COLLECTION_ID`: ID for the first knowledge base collection.
- `CUSTOM2_COLLECTION_ID`: ID for the second knowledge base collection.

---

## Troubleshooting

- **Connection Issues**: Ensure OpenWebUI is running and accessible via the specified URL.
- **Environment Variables**: Verify `.env` settings.
- **Debug Logs**: Check logs for detailed error messages.

---

## Contributing

Contributions are welcome! Please open an issue to discuss changes before submitting a pull request.

---

For more details, refer to the [GitHub repository](https://github.com/rmssantos/telegram-openwebui-bot).


