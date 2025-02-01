import tweepy
import json
import os
import logging

# Setup logging
logging.basicConfig(filename="twitter_post.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Load API keys from GitHub Secrets
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# Your job listings page URL
JOBS_PAGE_URL = "https://yourdomain.com/jobs"

# Authenticate with Twitter API
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

def post_latest_job():
    """Posts the latest job from jobs.json to Twitter."""
    try:
        with open("jobs.json", "r") as f:
            jobs = json.load(f)

        if not jobs:
            logging.info("No jobs available to post.")
            return

        latest_job = jobs[-1]  # Get the most recent job
        job_title = latest_job["title"]
        company = latest_job["company"]
        location = latest_job["location"]
        date_posted = latest_job["datePosted"]
        job_link = latest_job["link"]

        # Construct tweet with job details and a call-to-action
        tweet_text = (
            f"🚀 Hiring Now: {job_title} at {company}\n"
            f"🌍 {location} | 📅 {date_posted}\n"
            f"🔗 Apply Here: {job_link}\n\n"
            f"🔎 More Tech Jobs: {JOBS_PAGE_URL}"
        )

        # Trim tweet if it exceeds 280 characters
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."

        # Post the tweet
        api.update_status(tweet_text)
        logging.info(f"✅ Posted job: {job_title} to Twitter.")

    except Exception as e:
        logging.error(f"❌ Error posting to Twitter: {e}")

if __name__ == "__main__":
    post_latest_job()
