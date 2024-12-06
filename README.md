<<<<<<< HEAD
<<<<<<< HEAD
# Telegram OpenWebUI Bot

This project integrates a Telegram bot with [OpenWebUI](https://github.com/OpenWebUI/open-webui), enabling you to interact with a language model through Telegram. You can chat with the bot, summarize group chats, and maintain context using an external knowledge base if desired.

## Features

- **`/chat <message>`**: Send a message to the bot and receive a model-generated response.
- **`/summarize`** (in group chats): Summarize the last 24 hours of group messages, combined with recent chat context.
- **`/reset`**: Reset the conversation history for the current chat.

## Prerequisites

1. **Telegram Bot Token**:
   - Use the [BotFather](https://core.telegram.org/bots#6-botfather) on Telegram to create a new bot.
   - Start a chat with **@BotFather** and use `/newbot`.
   - Follow the instructions to name your bot and get your bot token.
   - Copy the provided token (e.g., `123456789:ABCDEF...`).

2. **OpenWebUI**:
   - Download and install OpenWebUI from the [OpenWebUI GitHub repository](https://github.com/OpenWebUI/open-webui).
   - Start the OpenWebUI server and note the URL where it is hosted (e.g., `http://localhost:3000/api`).
   - If OpenWebUI requires an API key, have it ready.

3. **Python 3.10+**:
   Ensure you have Python 3.10 or a later version installed on your system.

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/telegram-openwebui-bot.git
   cd telegram-openwebui-bot
   ```

2. **Create and configure the `.env` file**:
   - Copy the example `.env.example` file:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and add your Telegram API key, OpenWebUI URL, and other configurations:
     ```
     API_KEY=YOUR_TELEGRAM_BOT_TOKEN
     OPENWEBUI_BASE_URL=http://YOUR_OPENWEBUI_SERVER/api
     OPENWEBUI_API_KEY=YOUR_OPENWEBUI_API_KEY
     MODEL_NAME=neon-nomad
     MAX_TOKENS=500
     TEMPERATURE=0.7
     KNOWLEDGE_BASE_ID=YOUR_KNOWLEDGE_BASE_ID
     HISTORY_LENGTH=10
     KEYWORD=seedify
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the bot**:
   ```bash
   python bot.py
   ```
   - The bot will start polling for messages. Send a message to your bot on Telegram to test it.

## Docker Usage (Optional)

1. **Build the Docker image**:
   ```bash
   docker build -t telegram-openwebui-bot .
   ```

2. **Run the container**:
   ```bash
   docker run -d --env-file .env --name telegram_openwebui_bot telegram-openwebui-bot
   ```
   - Ensure `.env` is configured correctly before running this command.

## Environment Variables

- `API_KEY`: Your Telegram bot token from BotFather.
- `OPENWEBUI_BASE_URL`: Base URL of your OpenWebUI server (e.g., `http://localhost:3000/api`).
- `OPENWEBUI_API_KEY`: API key for OpenWebUI, if required.
- `MODEL_NAME`: The model name you want to use with OpenWebUI.
- `MAX_TOKENS`: Maximum number of tokens for responses.
- `TEMPERATURE`: Model sampling temperature.
- `KNOWLEDGE_BASE_ID`: ID for the knowledge base (optional). If the `KEYWORD` is detected in the user's message, this knowledge base is attached.
- `HISTORY_LENGTH`: Number of recent messages to maintain as context.
- `KEYWORD`: Keyword that triggers the attachment of the knowledge base.

## Usage Examples

### Chat
```bash
/chat Hello, how are you?
```
The bot will respond using the OpenWebUI model.

### Summarize (in a group chat)
```bash
/summarize
```
The bot returns a structured summary of the last 24 hours of group messages plus recent chat context.

### Reset conversation history
```bash
/reset
```
Clears the chat history for the current conversation.

## Troubleshooting

- If you encounter timeouts or connection issues, ensure the OpenWebUI server is running and accessible at the given `OPENWEBUI_BASE_URL`.
- Check if `.env` variables are set correctly and that the bot token is valid.
- Review logs for detailed error messages.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

MIT License

Copyright (c) 2024 [Ruben Santos]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

=======
# telegram-openwebui-bot
>>>>>>> main
=======
# telegram-openwebui-bot
>>>>>>> 8a1b71e (Initial commit)
