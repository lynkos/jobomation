from jobomation.collectors.greenhouse import fetch_job
from jobomation.collectors.ashby import fetch_jobs
from jobomation.db.repository import save_job, save_jobs, get_job, get_jobs, count_jobs
from jobomation.db.schema import initialize_database

DOORDASH = "doordashusa"
TWITCH = "twitch"
RAMP = "ramp"

def main() -> None:
    initialize_database()

    # Get all Ramp jobs
    jobs = fetch_jobs(RAMP)
    save_jobs(jobs)
    print(f"Saved {len(jobs)} jobs to database")

    # Get specific Twitch job
    # job = fetch_job(TWITCH, 8623401002)
    # save_job(job)
    # print(f"Saved {job.title} in {job.location} to database")

    # job = get_jobs()
    # if job:
    #     print(f"Got {len(job)} jobs from database")

    #print(count_jobs())

if __name__ == "__main__":
    main()