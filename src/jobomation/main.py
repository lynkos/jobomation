from jobomation.collectors import COLLECTORS
from jobomation.config import load_companies
from jobomation.filtering.rules import apply_filters_to_jobs
from jobomation.db.repository import save_job, save_jobs, get_job, get_jobs, count_jobs
from jobomation.db.schema import initialize_database

def main() -> None:
    initialize_database()

    for company in load_companies():
        collector = COLLECTORS.get(company.source_type)

        if collector is None:
            print(f"Unsupported source type: {company.source_type}")
            continue

        jobs = collector(company.board_id)
        jobs = apply_filters_to_jobs(jobs)
        save_jobs(jobs)
        print(f"Saved {len(jobs)} jobs to database")

        filtered_count = sum(job.filtered for job in jobs)

        print(
            f"{company.name}: "
            f"{len(jobs)} collected, "
            f"{filtered_count} filtered, "
            f"{len(jobs) - filtered_count} visible"
        )
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