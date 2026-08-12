from jobomation.collectors import COLLECTORS
from jobomation.config import load_targets, load_filters
from jobomation.filtering.rules import apply_filters_to_jobs
from jobomation.db.repository import save_job, save_jobs, get_job, get_jobs, count_jobs
from jobomation.db.schema import initialize_database

def main() -> None:
    initialize_database()

    targets = load_targets()
    filters = load_filters()

    for target in targets:
        collector = COLLECTORS.get(target.source)

        if collector is None:
            print(f"Unsupported source: {target.source}")
            continue

        try: jobs = collector(**target.args)
        except Exception as error:
            print(f"Failed to collect {target.name}: {error}")
            continue

        jobs = apply_filters_to_jobs(jobs, filters)
        save_jobs(jobs)
        filtered_count = sum(job.filtered for job in jobs)

        print(
            f"{target.name}: "
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