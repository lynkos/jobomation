from jobomation.collectors.ashby import fetch_jobs as fetch_ashby_jobs
from jobomation.collectors.greenhouse import fetch_jobs as fetch_greenhouse_jobs

COLLECTORS = {
    "greenhouse": fetch_greenhouse_jobs,
    "ashby": fetch_ashby_jobs,
}