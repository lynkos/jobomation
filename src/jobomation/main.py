from jobomation.collectors.greenhouse import fetch_job, fetch_jobs
from jobomation.db.repository import save_job
from jobomation.db.schema import initialize_database

def main() -> None:
    initialize_database()

    # Get all DoorDash jobs
    #jobs = fetch_jobs("doordashusa")
    #print(f"Found {len(jobs)} jobs")
    #first_job = jobs[0]
    #print(first_job.source_job_id)

    # Get specific DoorDash job
    job = fetch_job("doordashusa", 7263610)
    save_job(job)
    print(f"Saved {job.title} in {job.location} to database")

if __name__ == "__main__":
    main()