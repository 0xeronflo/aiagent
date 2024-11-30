import tweepy
import datetime
from openai_api import analyze_image_with_openai
from tweepy import TweepyException
from config import (
    X_BEARER_TOKEN,
    X_API_KEY,
    X_API_SECRET,
    X_ACCESS_TOKEN,
    X_ACCESS_SECRET,
)

# Initialize the Tweepy client
client = tweepy.Client(
    bearer_token=X_BEARER_TOKEN,
    consumer_key=X_API_KEY,
    consumer_secret=X_API_SECRET,
    access_token=X_ACCESS_TOKEN,
    access_token_secret=X_ACCESS_SECRET,
    return_type=dict,
    wait_on_rate_limit=True,
)


def post_to_x(tweet_data):
    """Post a standalone tweet."""
    try:
        # If tweet_data is a dictionary, extract the tweet text
        if isinstance(tweet_data, dict):
            tweet = tweet_data["tweet"]
        else:
            tweet = tweet_data

        # Add a check to ensure tweet isn't too long
        if len(tweet) > 270:  # Twitter's character limit
            tweet = tweet[:270]

        response = client.create_tweet(text=tweet)
        if "data" in response:
            print(f"Tweet posted successfully: {tweet}")
        else:
            print("Failed to post tweet.")
    except tweepy.TweepyException as e:
        print(f"Error posting tweet: {e}")


def reply_to_x(tweet_id, reply_text):
    """Reply to a tweet."""
    try:
        # If reply_text is a dictionary, extract the tweet text
        if isinstance(reply_text, dict):
            reply = reply_text["tweet"]
        else:
            reply = reply_text

        # Add a check to ensure reply isn't too long
        if len(reply) > 270:  # Twitter's character limit
            reply = reply[:270]

        response = client.create_tweet(
            text=reply, 
            in_reply_to_tweet_id=tweet_id
        )
        
        if "data" in response:
            print(f"Replied to Tweet ID {tweet_id} with: {reply}")
        else:
            print("Failed to post reply.")
            print(f"Response details: {response}")
    
    except tweepy.TweepyException as e:
        print(f"Error replying to tweet: {e}")
        # If possible, log the full error details
        print(f"Error details: {str(e)}")


def quote_tweet(tweet_id, quote_text):
    """Quote a tweet."""
    try:
        # If quote_text is a dictionary, extract the tweet text
        if isinstance(quote_text, dict):
            quote = quote_text["tweet"]
        else:
            quote = quote_text
        
        # Add a check to ensure quote isn't too long
        if len(quote) > 270:  # Twitter's character limit
            quote = quote[:270]

        response = client.create_tweet(
            text=quote, 
            quote_tweet_id=tweet_id
        )
        if "data" in response:
            print(f"Quoted Tweet ID {tweet_id} with: {quote}")
        else:
            print("Failed to post quote.")
    except tweepy.TweepyException as e:
        print(f"Error quoting tweet: {e}")


def fetch_most_interacted_tweet(list_id, hours=0.38, max_calls=1):
    """Fetch the most interacted-with tweet from an X List and analyze its media."""
    try:
        # Correct datetime usage to get UTC time minus the timedelta
        time_limit = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
        tweets = []

        for _ in range(max_calls):
            # Make sure to expand "author_id" to get user details (author handle)
            response = client.get_list_tweets(
                id=list_id,
                max_results=5,
                tweet_fields=["created_at", "public_metrics", "text", "attachments"],
                media_fields=["url"],  # Ensure media information is included
                expansions=["attachments.media_keys", "author_id"],  # Expand media keys and author_id
                user_fields=["username"],  # Fetch username (author's handle)
                pagination_token=None
            )

            if "data" in response:
                tweets.extend(response["data"])
            else:
                break

        if not tweets:
            print(f"No tweets found in list: {list_id}")
            return None

        # Create a lookup for media and users based on expansions
        media_lookup = {media["media_key"]: media for media in response.get("includes", {}).get("media", [])}
        users_lookup = {user["id"]: user["username"] for user in response.get("includes", {}).get("users", [])}

        most_interacted_tweet = None
        highest_interaction_score = 0

        for tweet in tweets:
            # Use datetime.datetime.strptime() to parse the date correctly
            created_at = datetime.datetime.strptime(tweet["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
            if created_at >= time_limit:
                metrics = tweet.get("public_metrics", {})
                interaction_score = (
                    metrics.get("like_count", 0) +
                    metrics.get("retweet_count", 0) +
                    metrics.get("reply_count", 0)
                )

                if interaction_score > highest_interaction_score:
                    most_interacted_tweet = tweet
                    highest_interaction_score = interaction_score

        if most_interacted_tweet:
            # Extract the author handle
            author_id = most_interacted_tweet.get("author_id")
            author_handle = users_lookup.get(author_id, "unknown")  # Default to "unknown" if not found
            most_interacted_tweet["author_handle"] = author_handle  # Add author handle to the tweet data

            # Extract media URLs if available
            media_keys = most_interacted_tweet.get("attachments", {}).get("media_keys", [])
            media_urls = []
            for key in media_keys:
                # Check for "url" field in the media object
                if key in media_lookup and "url" in media_lookup[key]:
                    media_urls.append(media_lookup[key]["url"])
            most_interacted_tweet["media"] = media_urls  # Add media URLs to tweet data
            
            # Step 4: If media exists, analyze the image(s)
            if media_urls:
                for media_url in media_urls:
                    print(f"Downloading and analyzing image from {media_url}")
                    image_analysis = analyze_image_with_openai(media_url)  # Use the function from main.py
                    print(f"Image analysis result: {image_analysis}")
            else:
                print("No media in the tweet, skipping image analysis.")

        return most_interacted_tweet

    except TweepyException as e:
        print(f"Error fetching tweets for list {list_id}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None