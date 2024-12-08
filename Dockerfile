# Usa uma imagem base de Python
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /apps/tgbot

# Copia todos os ficheiros do diretório atual para o diretório de trabalho no container
COPY . /apps/tgbot

# Instala as dependências do ficheiro requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Comando para correr o teu script principal (main.py)
CMD ["python", "bot.py"]

