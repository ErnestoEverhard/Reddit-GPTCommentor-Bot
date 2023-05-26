import praw  # Importing the Python Reddit API Wrapper
import openai  # Importing OpenAI API to generate responses
import config # Importing config variables
import time  # Importing the time module to manage the loop
import random  # Importing the random module for the random backoff time
from transformers import GPT2TokenizerFast  # Importing the transformer for tokenization
from threading import Thread  # Importing threading module to run bot in background
from datetime import datetime, timedelta

# Initialize Reddit API
reddit = praw.Reddit(
    client_id=config.REDDIT_CLIENT_ID,
    client_secret=config.REDDIT_SECRET,
    user_agent=config.REDDIT_USER_AGENT,
    username=config.REDDIT_USERNAME,
    password=config.REDDIT_PASSWORD,
)

# Initialize OpenAI API
openai.api_key = config.OPENAI_API_KEY

# Define max tokens and subreddit name
max_tokens = 1000
subreddit_name = "bottesting+dog+cat+"
system_message = "You are teenage animal lover that is obsessed with cats, dogs, and other cute pets. Respond by agreeing with the comment but adding something else that you find cute about the topic, don't sound too formal in your response, use slang or cutesie phrases. Do not use the phrase 'I completely agree!'"
triggers = ["1000/10", "10/10", "I love how cats", "I love how dogs"]
replied_posts = set()

def generate_response(prompt):
    messages = [
        { 
            "role": "system", 
            "content": f'{system_message}'
        },
        {
            "role": "user",
            "content": f'{prompt}'
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response.choices[0].message.content

# Function to check if the bot has already replied to a post
def has_already_replied_to_post(post):
    bot_username = config.REDDIT_USERNAME
    post.comments.replace_more(limit=0)  # replace MoreComments objects, limit=0 means all of them
    for comment in post.comments.list():  # list() flattens the comment tree
        if comment.author and comment.author.name.lower() == bot_username.lower():
            return True
    return False

# Function to check if comment contains any of the triggers
def contains_trigger(comment):
    return any(trigger.lower().strip() in comment.body.lower().strip() for trigger in triggers)

# Function to monitor subreddit comments
def monitor_subreddit_comments():
    print(f"Running")
    subreddit = reddit.subreddit(subreddit_name)

    # Get current time and subtract 24 hours to get "start of day"
    now = datetime.now()
    start_of_day = now - timedelta(hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)

    # Monitor new comments
    for comment in subreddit.stream.comments():
        # Convert the comment's creation time from UNIX timestamp to a datetime object
        comment_time = datetime.fromtimestamp(comment.created_utc)

        # Skip this comment if it's on a post that was created before today
        if comment_time < start_of_day:
            continue

        if contains_trigger(comment) and not has_already_replied_to_post(comment.submission):
            print(f"Trigger found in {comment.submission.permalink}")
            prompt = comment.body  # use comment body as the prompt

            # Check if the prompt is over the token limit
            if count_tokens(prompt) >= max_tokens:
                print(f"Ignoring comment due to exceeding token limit: {comment.id}")
                continue

            response = generate_response(prompt)

            # Reply to the comment
            comment.reply(response)
            post_url = f"https://www.reddit.com{comment.submission.permalink}"
            print(f"Replied to comment: {comment.id} on post: {post_url}")

            # Sleep for 120 seconds before checking for new comments
            time.sleep(120)

def count_tokens(text):
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    encoded = tokenizer.encode(text)
    return len(encoded)

def monitor_subreddit_comments_with_backoff():
    while True:
        try:
            monitor_subreddit_comments()
        except Exception as e:
            print(f"Error in monitor_subreddit_comments: {e}")
            backoff_time = random.randint(5, 15)  # Random backoff time between 5 to 15 seconds
            print(f"Backing off for {backoff_time} seconds in monitor_subreddit_comments...")
            time.sleep(backoff_time)

if __name__ == "__main__":
    monitor_subreddit_comments_with_backoff()
