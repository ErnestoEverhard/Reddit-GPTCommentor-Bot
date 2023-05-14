import praw  # Importing the Python Reddit API Wrapper
import openai  # Importing OpenAI API to generate responses
import config # Importing config variables
import time  # Importing the time module to manage the loop
import random  # Importing the random module for the random backoff time
from transformers import GPT2TokenizerFast  # Importing the transformer for tokenization
from threading import Thread  # Importing threading module to run bot in background

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
subreddit_name = "Sysadmin+WindowsServer+Windows+Windows10+WindowsServer+bash+batch+bottesting"
system_message = "You are a sarcastic PowerShell, BASH, and BAT expert respond to this Reddit comment by mocking the content of the comment and/or the commenter."
triggers = ["PowerShell", "BASH", ".bat"]

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

# Function to check if the bot has already replied to the comment
def has_already_replied(comment):
    bot_username = config.REDDIT_USERNAME
    comment.refresh()
    for reply in comment.replies:
        if reply.author and reply.author.name == bot_username:
            return True
    return False

# Function to check if comment contains any of the triggers
def contains_trigger(comment):
    return any(trigger in comment.body.lower().strip() for trigger in triggers)

# Function to monitor subreddit comments
def monitor_subreddit_comments():
    print(f"Running")    
    subreddit = reddit.subreddit(subreddit_name)

    # Monitor new comments
    for comment in subreddit.stream.comments():
        if contains_trigger(comment) and not has_already_replied(comment):
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
