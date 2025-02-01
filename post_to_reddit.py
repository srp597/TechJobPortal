import praw
import json
import os
import logging
from datetime import datetime

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
    """Posts the latest job from jobs.json to Reddit following r/techjobs' title format."""
    try:
        with open("jobs.json", "r") as f:
            jobs = json.load(f)

        if not jobs:
            logging.info("No jobs available to post.")
            return

        latest_job = jobs[-1]  # Get the most recent job

        # Extract job details
        job_title = latest_job["title"]
        company = latest_job["company"]
        location = latest_job["location"]
        job_link = latest_job["link"]
        date_posted = latest_job["datePosted"]

        # 🛠️ Ensure correct format for location
        location_tag = "[Remote]" if "Remote" in location else "[Hybrid]"

        # ✅ Fix: Title follows r/techjobs format
        today = datetime.today().strftime("%b %d, %Y")
        title = f"[Hiring] {location_tag} [{location}] - {job_title} - {today}"
        logging.info(f"✅ Successfully generated the title to post: {title}.")

        # 📝 Format Reddit post body
        body = f"""
🚀 **New Job Alert!**  
**Position:** {job_title}  
**Company:** {company}  
**Location:** {location}  
**Date Posted:** {date_posted}  

🔗 **Apply Here:** [Click to Apply]({job_link})  

🌍 See More Tech Jobs: [swejobpostings](https://swejobpostings.com/job-listings)  

---  
"""

        # 🛠️ Submit the post to Reddit
        subreddit = reddit.subreddit(subreddit_name)
        subreddit.submit(title, selftext=body)

        logging.info(f"✅ Successfully posted job: {job_title} to r/{subreddit_name}.")

    except Exception as e:
        logging.error(f"❌ Error posting to Reddit: {e}")

if __name__ == "__main__":
    post_latest_job("techjobs")
