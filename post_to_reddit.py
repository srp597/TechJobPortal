import json
import os
import praw
import logging
from datetime import datetime, timedelta

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

POSTED_JOBS_FILE = "posted_jobs.json"

# Select flairs
SUBREDDIT_FLAIRS = {
    "techjobs": "Hiring",
    "remotejobs": "Job Posts"
}

# Load previously posted jobs from JSON file
def load_posted_jobs():
    if os.path.exists(POSTED_JOBS_FILE):
        with open(POSTED_JOBS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logging.warning("Invalid JSON format in posted_jobs.json. Resetting file.")
                return []
    return []

# Save updated posted jobs list to JSON file
def save_posted_jobs(posted_jobs):
    logging.info(f"Saving posted_jobs: {posted_jobs}")
    existing_jobs = load_posted_jobs()  # Load existing jobs
    updated_jobs = existing_jobs + [job for job in posted_jobs if job not in existing_jobs]  # Append new unique jobs
    
    with open(POSTED_JOBS_FILE, "w") as f:
        json.dump(updated_jobs, f, indent=4)
    logging.info(f"✅ Successfully updated posted_jobs.json with {len(updated_jobs)} total jobs.")


# Function to find the latest valid job
def find_latest_valid_job(jobs, posted_jobs, work_type_filter=None):
    cutoff_date = datetime.today() - timedelta(weeks=2)
    for job in reversed(jobs):
        job_identifier = job['link']
        job_date = datetime.strptime(job["datePosted"], "%Y-%m-%d")
        work_type = job.get("workType", "Hybrid")
        
        if not any(posted_job['link'] == job_identifier for posted_job in posted_jobs) and job_date >= cutoff_date:
            if work_type_filter is None or work_type == work_type_filter:
                return job
    return None

# Function to post a job to Reddit with enhanced visibility
def post_job(subreddits, job, posted_jobs):
    try:
        job_identifier = job['link']
        job_title = job["title"]
        company = job["company"]
        location = job["location"]
        country = job.get("country", "Anywhere")
        job_link = job["link"]
        date_posted = job["datePosted"]
        salary_range = job.get("salaryRange", "Not specified")
        work_type = job.get("workType", "Hybrid")

        today = datetime.today().strftime("%b %d, %Y")
        title = f"[Hiring] [{work_type}] [{country}] - {job_title} - {today}"
        logging.info(f"✅ Generating post title: {title}")

        # Format Reddit post body with engagement strategies
        body = f"""
🔥 **Exciting Career Opportunity!** 🔥  
🚀 **{job_title} at {company}** is hiring now!  
📍 **Location:** {location}  
📅 **Date Posted:** {date_posted}  
💰 **Salary Range Per Annum:** {salary_range}  

🔗 **Apply Now:** [Click Here]({job_link})  
🌍 **Explore More Tech Jobs:** [https://swejobpostings.com](https://swejobpostings.com/job-listings)  
💬 **Discuss the opportunity and tag your friends!**  

---  
*If you're looking for exciting and active job opportunities, follow us for daily updates!*  
"""
        for subreddit in subreddits:
            logging.info(f"Posting the job: {job_title} to r/{subreddit}.")
            
            subreddit_instance = reddit.subreddit(subreddit)
            submission = subreddit_instance.submit(title, selftext=body)
            #if subreddit in SUBREDDIT_FLAIRS:
                #flair_text = SUBREDDIT_FLAIRS[subreddit]
                #submission.flair.select(flair_text)
            logging.info(f"✅ Successfully posted job: {job_title} to r/{subreddit}.")

        # Save posted job identifier in the new structured format
        posted_jobs.append({"link": job_identifier, "datePosted": date_posted})
        save_posted_jobs(posted_jobs)
    except Exception as e:
        logging.error(f"❌ Error posting to Reddit: {e}")

if __name__ == "__main__":
    posted_jobs = load_posted_jobs()
    
    with open("jobs.json", "r") as f:
        jobs = json.load(f)
    
    latest_general_job = find_latest_valid_job(jobs, posted_jobs)
    latest_remote_job = find_latest_valid_job(jobs, posted_jobs, work_type_filter="Remote")
    
    general_subreddits = ["techjobs"]
    remote_subreddits = ["remotework"]
    #Add this subreddit back after fixing the flair permissions issue
    #remote_subreddits = ["remotework", "remotejobs"]
    
    
    logging.info(f"✅ Posting to general_subreddits.")
    if latest_general_job:
        post_job(general_subreddits, latest_general_job, posted_jobs)

    logging.info(f"✅ Posting to remote_subreddits.")
    if latest_remote_job:
        post_job(remote_subreddits, latest_remote_job, posted_jobs)
        
    logging.info(f"✅ Script run complete.")
