import praw
import json
import os
import logging

# Setup logging
logging.basicConfig(filename="reddit_post.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Load Reddit API credentials from GitHub Secrets
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USERNAME = os.getenv("REDDIT_USERNAME")
PASSWORD = os.getenv("REDDIT_PASSWORD")

# Configure Reddit API (OAuth)
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    username=USERNAME,
    password=PASSWORD,
    user_agent="TechJobBot/1.0 (by u/{})".format(USERNAME)
)

def post_latest_job(subreddit_name):
    """Posts the latest job from jobs.json to Reddit."""
    try:
        with open("jobs.json", "r") as f:
            jobs = json.load(f)

        if not jobs:
            logging.info("No jobs available to post.")
            return

        latest_job = jobs[-1]  # Get the most recent job

        # ✅ Fix: Ensure the title follows subreddit rules
        title = f"[HIRING] {latest_job['title']} at {latest_job['company']} ({latest_job['location']})"

        body = f"""
🚀 **New Job Alert!**  
**Position:** {latest_job['title']}  
**Company:** {latest_job['company']}  
**Location:** {latest_job['location']}  
**Date Posted:** {latest_job['datePosted']}  

🔗 **Apply Here:** [Click to Apply]({latest_job['link']})  

🌍 See More Tech Jobs: [https://www.swejobpostings.com](https://www.swejobpostings.com/job-listings)  

"""

        subreddit = reddit.subreddit(subreddit_name)
        subreddit.submit(title, selftext=body)

        logging.info(f"✅ Successfully posted job: {latest_job['title']} to r/{subreddit_name}.")

    except Exception as e:
        logging.error(f"❌ Error posting to Reddit: {e}")

if __name__ == "__main__":
    post_latest_job("techjobs")
