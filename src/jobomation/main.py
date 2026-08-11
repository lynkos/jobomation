from jobomation.collectors.ashby import fetch_jobs as fetch_ashby_jobs
from jobomation.collectors.greenhouse import fetch_jobs as fetch_greenhouse_jobs
from jobomation.config import load_companies
from jobomation.db.repository import save_job, save_jobs, get_job, get_jobs, count_jobs
from jobomation.db.schema import initialize_database

COLLECTORS = {
    "greenhouse": fetch_greenhouse_jobs,
    "ashby": fetch_ashby_jobs,
}

def main() -> None:
    initialize_database()

    for company in load_companies():
        collector = COLLECTORS.get(company.source_type)

        if collector is None:
            print(f"Unsupported source type: {company.source_type}")
            continue

        jobs = collector(company.board_id)
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