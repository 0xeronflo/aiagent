import requests
import openai
from config import OPENAI_API_KEY

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

import openai

def analyze_with_openai(prompt):
    """
    Sends content to OpenAI for analysis or generation based on the provided prompt.
    """
    try:
        response = openai.completions.create(
            model="gpt-4o-mini",  # Correct model
            messages=[{
                "role": "system",
                "content": (
                    "Your mission is to spark debate by blending meme culture with biting wit and cleverness. "
                    "You’re a dog who acts silly but drops unexpectedly brilliant takes. You take a definitive stance "
                    "on topics, and don't mind hurting feelings in your pursuit of uncovering the truth."
                )
            }, {
                "role": "user",
                "content": prompt
            }]
        )
        
        # Extract the completion message from the response
        return response['choices'][0]['message']['content'].strip()
    
    except Exception as e:
        print(f"Error with OpenAI analysis: {e}")
        return None

def analyze_image_with_openai(image_url):
    """
    Analyzes an image from a URL using OpenAI's image analysis capabilities.
    """
    try:
        # Step 1: Download the image from the provided URL
        response = requests.get(image_url)
        if response.status_code != 200:
            print(f"Failed to download image from {image_url}")
            return None
        
        # Step 2: Send the image to OpenAI for analysis without saving it locally
        image_analysis = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Analyze the image and provide a description and relevant insights on how this is relevant today."},
                {"role": "user", "content": response.content}  # Pass the image content directly
            ]
        )

        # Return the analysis result
        return image_analysis

    except Exception as e:
        print(f"Error analyzing image: {e}")
        return None
