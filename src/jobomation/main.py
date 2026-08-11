from jobomation.collectors.greenhouse import fetch_job, fetch_jobs
from jobomation.db.repository import save_job, save_jobs
from jobomation.db.schema import initialize_database

def main() -> None:
    initialize_database()

    # Get all DoorDash jobs
    jobs = fetch_jobs("doordashusa")
    save_jobs(jobs)
    print(f"Saved {len(jobs)} jobs to database")

    # Get specific DoorDash job
    # job = fetch_job("doordashusa", 7263610)
    # save_job(job)
    # print(f"Saved {job.title} in {job.location} to database")

if __name__ == "__main__":
    main()