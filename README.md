# Reddit Commentor bot

## Overview

These scripts are designed to create a Reddit bot powered by OpenAI's GPT-3.5-turbo model. The bot monitors specified subreddits for certain keywords or phrases, and generates sarcastic responses to comments containing those triggers. The bot is able to handle multiple triggers and can be configured to respond to comments containing any of the listed triggers.

## Prerequisites

The scripts require several Python libraries:

- `praw`: The Python Reddit API Wrapper, used to interact with Reddit's API.
- `openai`: OpenAI's Python client library, used to generate responses with the GPT-3.5-turbo model.
- `transformers`: A library by Hugging Face used for tokenization.
- `time` and `random`: Standard Python libraries used to manage the timing of the script and to introduce random backoff times for error handling.
- `threading`: A standard Python library used for running the bot in the background.

## Configuration

The scripts rely on a separate `config` module for various configuration variables, such as Reddit and OpenAI API keys. This file is not included in the scripts and should be created with the following variables:

- `REDDIT_CLIENT_ID`
- `REDDIT_SECRET`
- `REDDIT_USER_AGENT`
- `REDDIT_USERNAME`
- `REDDIT_PASSWORD`
- `OPENAI_API_KEY`

The `subreddit_name` variable is a string containing the names of the subreddits the bot should monitor, separated by "+". The `triggers` variable is a list of keywords or phrases that the bot should respond to.

## Functionality

When a comment is made in a monitored subreddit that contains a trigger phrase, the bot generates a response using the OpenAI API. Before responding, the bot checks whether it has already replied to the comment and whether the comment's length exceeds the maximum token limit for the OpenAI model.

The bot's responses include a disclaimer notifying the user that they have activated the bot and that it is currently in testing.

## Error Handling

The scripts include a backoff mechanism. If an error occurs during the monitoring of subreddit comments, the bot will pause for a random period of time between 5 and 15 seconds before attempting to monitor comments again.

## Usage

The scripts are designed to be run as standalone Python scripts. To start the bot, simply run the scripts in your Python environment. The bot will begin monitoring the specified subreddits for the trigger phrases and respond to comments accordingly.
