# Deadline Bot

A quick and simple implementation of a twitter bot that is basically a countdown timer for CG,CV, and Vis conferences.

Checkout the bot in action [here](https://x.com/confclock)!

## How to setup environment for running the scripts
```
conda create -n dlbot python=3.10
conda activate dlbot
pip install tweepy python-dotenv crawl4ai
pip install langchain langchain-community langchain-google-genai
```

<!-- Check [this blog post](https://srihegde.github.io/post/dlbot/) for more info on setting up and using the scripts to run the bot. -->

## File Structure

```bash
├── README.md:                     This file
|
├── app.py:                        Main script to run the bot
|
├── conf_curator.py:               Script for LLM-based deadline curation
|
├── dl.csv:                        CSV file containing the conference deadlines
|
└── setup_bot.ipynb:               Jupyter notebook to setup the bot

```

Ideal way to run the bot is to use a cron job to sequentially run `conf_curator.py` followed by `app.py` script at a specific time of the day. 
