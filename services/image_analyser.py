# services/image_analyser.py

from openai import AzureOpenAI
import base64
import os
import logging

logger = logging.getLogger(__name__)

# Azure OpenAI client setup
endpoint = os.getenv("ENDPOINT_URL", "REPLACE_WITH_YOUR_ENDPOINT_URL")
deployment = os.getenv("DEPLOYMENT_NAME", "REPLACE_WITH_YOUR_DEPLOYMENT_NAME")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "REPLACE_WITH_YOUR_KEY_VALUE_HERE")

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-08-01-preview",
)

def analyze_image(image_bytes, prompt="Please analyze this image."):
    """
    Analyze an image using Azure OpenAI GPT-4 Vision model.
    """
    try:
        # Encode image in base64
        encoded_image = base64.b64encode(image_bytes).decode('ascii')

        # Prepare the chat prompt
        chat_prompt = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are an AI assistant that helps people analyze images and provide information."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        }
                    }
                ]
            }
        ]

        # Call the Azure OpenAI API
        completion = client.chat.completions.create(
            model=deployment,
            messages=chat_prompt,
            max_tokens=1500,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
        )

        # Extract and return the analysis result
        return completion.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Error analyzing image with Azure OpenAI: {e}", exc_info=True)
        return f"An error occurred during image analysis: {e}"

