import requests
import json
import logging
from datetime import datetime, timedelta
from dateutil import parser  # Add this import to handle various date formats
import os
import re

# Setup logging
logging.basicConfig(filename="fetch_jobs.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# RemoteOK API Endpoint
REMOTEOK_API_URL = "https://remoteok.io/api"
# Remotive API Endpoint
REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"

# Get today's date and the past 24 hours
TODAY = datetime.utcnow()
ONE_DAY_AGO = TODAY - timedelta(days=1)

def load_existing_jobs():
    """Load existing jobs from jobs.json if available."""
    if os.path.exists("jobs.json"):
        with open("jobs.json", "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logging.warning("⚠ jobs.json is not valid JSON. Creating a new file.")
                return []
    return []

def clean_description(description):
    """Remove HTML tags and truncate the job description."""
    clean_text = re.sub('<.*?>', '', description)  # Remove HTML tags
    return clean_text[:200] + '...' if len(clean_text) > 200 else clean_text

def fetch_remoteok_jobs():
    """Fetch jobs from RemoteOK API and filter only those posted in the last 24 hours."""
    try:
        logging.info("Fetching jobs from RemoteOK...")
        response = requests.get(REMOTEOK_API_URL, headers={"User-Agent": "Mozilla/5.0"})

        if response.status_code != 200:
            logging.error(f"❌ Failed to fetch jobs (HTTP {response.status_code})")
            return []

        jobs_data = response.json()[1:]  # Skip first element (metadata)
        new_jobs = []

        for job in jobs_data:
            posted_date = datetime.utcfromtimestamp(job.get("epoch", 0))

            if posted_date >= ONE_DAY_AGO:  # Only keep jobs from the last 24 hours
                formatted_job = {
                    "title": job["position"],
                    "company": job["company"],
                    "location": "Not Applicable",
                    "country": "USA and others",
                    "workType": "Remote",
                    "datePosted": posted_date.strftime("%Y-%m-%d"),
                    "baseSalary": job.get("salary", "Not specified"),
                    "link": job["url"],
                    "description": clean_description(job.get("description", "No description available.")),
                    "source": "RemoteOK"
                }
                new_jobs.append(formatted_job)

        logging.info(f"✅ Fetched {len(new_jobs)} new jobs from RemoteOK.")
        return new_jobs

    except Exception as e:
        logging.error(f"❌ Error fetching jobs from RemoteOK: {e}")
        return []
    
def fetch_remotive_jobs():
    """Fetch jobs from Remotive API and filter those posted in the last 24 hours."""
    try:
        logging.info("Fetching jobs from Remotive...")
        response = requests.get(REMOTIVE_API_URL, headers={"User-Agent": "Mozilla/5.0"})

        if response.status_code != 200:
            logging.error(f"❌ Failed to fetch jobs from Remotive (HTTP {response.status_code})")
            return []

        jobs_data = response.json().get("jobs", [])
        new_jobs = []

        for job in jobs_data:
            posted_date_str = job.get("publication_date", "")

            try:
                # Automatically parse any valid date format
                posted_date = parser.parse(posted_date_str)
            except ValueError:
                logging.warning(f"⚠ Skipping job due to invalid date format: {posted_date_str}")
                continue

            if posted_date >= ONE_DAY_AGO:
                formatted_job = {
                    "title": job.get("title", "Unknown Title"),
                    "company": job.get("company_name", "Unknown Company"),
                    "location": job.get("candidate_required_location", "Not Available"),
                    "country": "USA and others",
                    "workType": "Remote",
                    "datePosted": posted_date.strftime("%Y-%m-%d"),
                    "baseSalary": job.get("salary", "Not specified"),
                    "link": job.get("url", ""),
                    "description": clean_description(job.get("description", "No description available.")),
                    "source": "Remotive"
                }
                new_jobs.append(formatted_job)

        logging.info(f"✅ Fetched {len(new_jobs)} new jobs from Remotive.")
        return new_jobs

    except Exception as e:
        logging.error(f"❌ Error fetching jobs from Remotive: {e}")
        return []

def save_jobs(updated_jobs):
    """Save updated jobs list to jobs.json."""
    with open("jobs.json", "w") as f:
        json.dump(updated_jobs, f, indent=2)
    logging.info(f"✅ Successfully updated jobs.json with {len(updated_jobs)} total jobs.")

def main():
    """Main job fetching and updating process."""
    logging.info("🚀 Starting job fetching process...")
    
    existing_jobs = load_existing_jobs()
    new_jobs = []
    new_jobs.extend(fetch_remoteok_jobs())
    new_jobs.extend(fetch_remotive_jobs())

    if new_jobs:
        # Remove duplicates based on job link
        all_jobs = existing_jobs + new_jobs
        unique_jobs = {job['link']: job for job in all_jobs}
        updated_jobs = list(unique_jobs.values())
        save_jobs(updated_jobs)
    else:
        logging.info("ℹ No new jobs found today.")

if __name__ == "__main__":
    main()
