import openai  # Explicitly import the openai library
from openai import OpenAI  # Also import OpenAI client
import config  # Assuming you're using a config file for the API keys

class ResearchAssistant:
    def __init__(self):
        # Set the OpenAI API key
        openai.api_key = config.OPENAI_API_KEY

        # Initialize the Perplexity client
        self.client = OpenAI(
            api_key=config.PERPLEXITY_API_KEY,  # This is the Perplexity API key
            base_url="https://api.perplexity.ai"  # Perplexity API base URL
        )

    def research_topic(self, topic):
        """
        Use OpenAI (via Perplexity API) to research a topic.
        :param topic: The topic to research.
        :return: The AI-generated research summary.
        """
        try:
            print(f"\n### Researching Topic: {topic} ###")

            # Define the role and user input for the conversation
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an artificial intelligence assistant tasked with providing a concise, detailed summary of any topic, prioritizing the latest relevant news or research available."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Please provide concise, detailed research on this topic, designed to inform a person who will be writing a tweet on the topic, ensuring you consider the latest developments first: {topic}. \
                    Break down the analysis into the following subtopics, ensuring brevity and clarity: \
                    - Brief overview of the topic \
                    - Latest developments in the news \
                    - Financial/economic implications \
                    - Popular consensus \
                    - Key arguments for and against the consensus \
                    - Conclusion",
                },
            ]


            # Send the request to the Perplexity API using the OpenAI client
            response = self.client.chat.completions.create(
                model="llama-3.1-sonar-large-128k-online",  # OpenAI GPT model or the desired model
                messages=messages,
            )

            # Correct way to access the message content
            research_summary = response.choices[0].message.content  # Accessing the content properly

            return research_summary

        except Exception as e:
            print(f"Error while researching topic: {e}")
            return None
