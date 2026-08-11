from jobomation.collectors.greenhouse import fetch_job, fetch_jobs
from jobomation.db.repository import save_job, save_jobs, get_job, get_jobs, count_jobs
from jobomation.db.schema import initialize_database

DOORDASH = "doordashusa"

def main() -> None:
    initialize_database()

    # Get all DoorDash jobs
    jobs = fetch_jobs(DOORDASH)
    save_jobs(jobs)
    print(f"Saved {len(jobs)} jobs to database")

    # Get specific DoorDash job
    # job = fetch_job(DOORDASH, 7263610)
    # save_job(job)
    # print(f"Saved {job.title} in {job.location} to database")

    # job = get_jobs()
    # if job:
    #     print(f"Got {len(job)} jobs from database")

    #print(count_jobs())

if __name__ == "__main__":
    main()