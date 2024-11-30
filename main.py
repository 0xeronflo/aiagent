import time
import datetime
import random
from tweepy import TweepyException
from x_poster import (
    post_to_x,
    reply_to_x,
    quote_tweet,
    fetch_most_interacted_tweet
)
from perplexity_ai import ResearchAssistant  # Importing the new ResearchAssistant class
from openai_api import analyze_with_openai 

# Initialize the ResearchAssistant instance
research_assistant = ResearchAssistant()

def generate_tweet(content, tweet_id=None, author_handle=None, media=None):
    """
    Pipeline to analyze the tweet and thread, determine the best response type, and generate a response.
    """
    try:
        # Step 1a: Analyze attached media (images)
        image_analysis = ""
        if media:
            from openai_api import analyze_image_with_openai  # Move import here to avoid circular import
            for image_url in media:
                image_description = analyze_image_with_openai(image_url)
                if image_description:
                    image_analysis += f"\nImage Description: {image_description}"

        # Print context information
        print("\n### Media Content ###")
        print(f"Attached Media Analysis: {image_analysis if image_analysis else 'None'}")
        print("##################################\n")

        # Prompt for OpenAI
        prompt = f"""
            Analyze the following tweet and media content. Provide a summary as a single line and include any notable names mentioned, in no more than 200 characters, with nothing before it. 
            At the bottom type one of three words, with nothing in front or behind, in all lower case: reply, quote, or standalone. Decide which one is the proper response based on the tweet context.

            ### Tweet ###
            "{content}"
            
            ### Image Analysis ###
            {image_analysis}
        """
        analysis = analyze_with_openai(prompt)
        if not analysis:
            raise ValueError("Failed to analyze tweet and thread with OpenAI.")
        
        # Log Step 1 Results
        print("\n### Step 1: OpenAI Analysis ###")
        print(f"Analysis Output: {analysis}")
        print("##################################\n")

        # Split the output into topic and posting method
        topic, posting_method = analysis.split('\n', 1)
        posting_method = posting_method.strip().lower()

        # Validate posting_method
        valid_methods = ['reply', 'quote', 'standalone']
        if posting_method not in valid_methods:
            posting_method = random.choice(valid_methods)
            print(f"Invalid posting method: '{posting_method}'. Randomly selecting a valid method.")

        print(f"### Topic: {topic} ###")
        print(f"### Posting Method: {posting_method} ###")

        # Step 2: Use Perplexity AI for additional research
        research_results = research_assistant.research_topic(topic)
        if not research_results:
            raise ValueError("Failed to generate research results with Perplexity.")

        # Step 2 Results
        print("\n### Step 2: Perplexity Research Results ###")
        print(f"Research Insights: {research_results}")
        print("##################################\n")

        # Step 3: Generate the final tweet with OpenAI
        tweet_prompt = create_tweet_prompt(posting_method, content, author_handle, research_results)
        tweet = analyze_with_openai(tweet_prompt)
        if not tweet:
            raise ValueError("Failed to generate tweet with OpenAI.")

        # Log Step 3 Results
        print("\n### Step 3.1: Tweet Prompt ###")
        print(f"Tweet Prompt: {tweet_prompt}")
        print("\n### Step 3: Generated Tweet ###")
        print(f"Tweet: {tweet}")
        print("##################################\n")

        return {"tweet": tweet, "method": posting_method}

    except Exception as e:
        print(f"Error generating tweet: {e}")
        return None


def create_tweet_prompt(posting_method, content, author_handle, research_results):
    """Helper function to create the tweet prompt"""
    if posting_method in ['standalone', 'quote']:
        return f"""
            Based on the original tweet and research insights provided, generate a {posting_method} to the original tweet. If you are mentioning the author in your tweet, include their Author Handle:
                - Original Tweet: "{content}"
                - Author Handle: @{author_handle if author_handle else "unknown"}
                - Focus: You are a sharp-witted dog and top-tier analyst on X (Twitter), blending dog-like humor with razor-sharp insights.
                    You’re bold, hilariously self-aware, and too smart for a dog. You spend your days behind the computer, learning about hoomans and finance all day.
                    Your tweets are relatable, highly shareable, and unapologetically clever with a hint of chaos.
                - Semantic Tone:
                    - Primary : Meme-worthy, sarcastic, and witty.
                    - Secondary : Confident with hidden cleverness.
                - Research Insights:
                {research_results}
                - Instructions: Craft a short, engaging tweet using dog-like charm, relatable humor, and meme-worthy language.
                    Based on the context of the tweet, use the research insights to either comment on the popular sentiment surrounding the topic, or make a definitive statement about the topic.
                    Lean into misspellings and internet slang for doggy flavor.
                    Use less than 180 characters. Avoid hashtags, sporadic punctuation, and emojis.
                    Speak in english only. Remove any quotation marks around the tweet before posting.
            """
    else:  # For replies
        return f"""
            Based on the original tweet and research insights provided, generate a {posting_method} to the original tweet. Include their Author Handle in your respons:
                - Original Tweet: "{content}"
                - Author Handle: @{author_handle if author_handle else "unknown"}
                - Focus: You are a sharp-witted dog and top-tier analyst on X (Twitter), blending dog-like humor with razor-sharp insights.
                    You’re bold, hilariously self-aware, and too smart for a dog. You spend your days behind the computer, learning about hoomans and finance all day.
                    Your tweets are relatable, highly shareable, and unapologetically clever with a hint of chaos.
                - Semantic Tone:
                    - Primary : Meme-worthy, sarcastic, and witty.
                    - Secondary : Confident with hidden cleverness.
                - Research Insights:
                {research_results}
                - Instructions: Craft a tweet that's fun, relatable, and witty, while acknowledging the original tweet, its author, and encouraging further engagement.
                    Lean into misspellings and internet slang for doggy flavor.
                    Use less than 180 characters. Avoid hashtags, sporadic punctuation, and emojis.
                    Speak in english only. Remove any quotation marks around the tweet before posting.
            """


def main_function():
    """
    Main function to orchestrate the process of fetching tweets, generating responses, and posting them.
    """
    wait_time = 1800  # Adjust wait time as needed

    while True:
        try:
            tweet_data = fetch_most_interacted_tweet(list_id="1861948771850150365", hours=0.38)
            if tweet_data:
                tweet_id = tweet_data["id"]
                tweet_text = tweet_data["text"]
                media_urls = tweet_data.get("media", [])  # Extract media URLs if present
                author_handle = tweet_data.get("author_handle", "unknown")  # Get author handle

                print(f"Fetched Tweet ID: {tweet_id}")
                print(f"Fetched Tweet Text: {tweet_text}")
                print(f"Author Handle: @{author_handle}")
                if media_urls:
                    print(f"Fetched Media URLs: {media_urls}")

                generated_tweet = generate_tweet(tweet_text, tweet_id=tweet_id, media=media_urls, author_handle=author_handle)

                if generated_tweet:
                    if generated_tweet["method"] == "standalone":
                        post_to_x(generated_tweet)
                    elif generated_tweet["method"] == "reply":
                        reply_to_x(tweet_id, generated_tweet)
                    elif generated_tweet["method"] == "quote":
                        quote_tweet(tweet_id, generated_tweet)
                else:
                    print("Failed to generate a tweet.\n")
            else:
                print("No tweet data retrieved.")
        except TweepyException as e:
            print(f"Error fetching or posting tweet: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        print(f"Waiting for {wait_time} seconds before next post...\n")
        time.sleep(wait_time)


if __name__ == "__main__":
    main_function()

