from httpx import Response, post as post_request
from os import getenv
from dotenv import load_dotenv
from datetime import datetime, timezone
from jobomation.models import Compensation, Job
from jobomation.models import Collector
from jobomation.collectors.utils import clean_description
from jobomation.exceptions import CollectorConfigError

JOB_SEARCH_QUERY = """
query GetJobData {{
    jobSearch(
        {what}
        {location}
        limit: 100
        {cursor}
        sort: RELEVANCE
        {filters}
    ) {{
        pageInfo {{
            nextCursor
        }}
        results {{
            trackingKey
            job {{
                source {{
                    name
                }}
                key
                title
                datePublished
                dateOnIndeed
                description {{
                    html
                }}
                location {{
                    countryName
                    countryCode
                    admin1Code
                    city
                    postalCode
                    streetAddress
                    formatted {{
                        short
                        long
                    }}
                }}
                compensation {{
                    estimated {{
                        currencyCode
                        baseSalary {{
                            unitOfWork
                            range {{
                                ... on Range {{
                                    min
                                    max
                                }}
                            }}
                        }}
                    }}
                    baseSalary {{
                        unitOfWork
                        range {{
                            ... on Range {{
                                min
                                max
                            }}
                        }}
                    }}
                    currencyCode
                }}
                attributes {{
                    key
                    label
                }}
                employer {{
                    relativeCompanyPageUrl
                    name
                }}
                recruit {{
                    viewJobUrl
                    detailedSalary
                    workSchedule
                }}
            }}
        }}
    }}
}}
"""

load_dotenv()

class IndeedCollector(Collector):
    source = "indeed"
    api_url = "https://apis.indeed.com/graphql"

    def __init__(self, *, search_term: str, location: str, results_wanted: int = 100, radius: int = 50) -> None:
        self.search_term = search_term
        self.location = location
        self.results_wanted = results_wanted
        self.radius = radius

    def _send_request(self, cursor: str | None = None) -> Response:
        query = self._build_query(search_term = self.search_term, location = self.location, cursor = cursor)

        return post_request(
            self.api_url,
            headers = self._headers(),
            json = { "query": query },
            timeout = self.timeout
        )

    def _fetch_page(self, cursor: str | None = None) -> tuple[list[dict], str | None]:
        job_search = self.get_response(cursor)["data"]["jobSearch"]
        return (job_search["results"], job_search["pageInfo"]["nextCursor"])

    def _headers(self) -> dict[str, str]:
        api_key = getenv("INDEED_API_KEY")
        
        if not api_key: raise CollectorConfigError("No Indeed API Key found!")
        
        return {
            "content-type": "application/json",
            "accept": "application/json",
            "indeed-locale": "en-US",
            "accept-language": "en-US,en;q=0.9",
            "indeed-api-key": api_key,
            "Host": "apis.indeed.com",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Indeed App 193.1",
            "indeed-app-info": "appv=193.1; appid=com.indeed.jobsearch; osv=16.6.1; os=ios; dtype=phone",
        }

    def _build_query(self, search_term: str | None = None, location: str | None = None, cursor: str | None = None) -> str:
        what = ""
        location_query = ""
        cursor_query = ""

        if search_term:
            escaped = search_term.replace('"', '\\"')
            what = f'what: "{escaped}"'

        if location:
            escaped = location.replace('"', '\\"')
            location_query = (
                f'location: {{where: "{escaped}", '
                f'radius: {self.radius}, radiusUnit: MILES}}'
            )

        if cursor: cursor_query = f'cursor: "{cursor}"'

        return JOB_SEARCH_QUERY.format(
            what = what,
            location = location_query,
            cursor = cursor_query,
            filters = ""
        )

    def _format_timestamp(self, timestamp_ms: int | None) -> str:
        if timestamp_ms is None: return ""
        return datetime.fromtimestamp(timestamp_ms / 1000, timezone.utc).isoformat()

    @staticmethod
    def _raw_to_compensation(raw: dict) -> Compensation | None:
        if not raw["baseSalary"] and not raw["estimated"]: return None
        comp = raw["baseSalary"] if raw["baseSalary"] else raw["estimated"]["baseSalary"]
        if not comp: return None
        
        min_range = comp["range"].get("min")
        max_range = comp["range"].get("max")
        
        return Compensation(
            min_amount = min_range if min_range is not None else None,
            max_amount = max_range if max_range is not None else None,
            currency = raw["estimated"]["currencyCode"] if raw["estimated"] else raw["currencyCode"],
            interval = comp["unitOfWork"] if comp["unitOfWork"] else None,
            description = None
        )

    def _raw_to_job(self, raw: dict) -> Job:
        location = raw.get("location") or {}
        employer = raw.get("employer") or {}
        description = raw.get("description") or {}
        compensation = raw.get("compensation") or {}

        formatted_location = (
            location.get("formatted", {}).get("long")
            or ", ".join(
                part
                for part in (
                    location.get("city"),
                    location.get("admin1Code"),
                    location.get("countryCode"),
                )
                if part
            )
        )

        return Job(
            source = self.source,
            source_job_id = raw["key"],
            title = raw["title"],
            company = employer.get("name") or "",
            location = formatted_location,
            url = f"https://www.indeed.com/viewjob?jk={raw['key']}",
            first_published = self._format_timestamp(raw.get("datePublished")),
            updated_at = None,
            description = clean_description(description.get("html", "")),
            compensation = self._raw_to_compensation(compensation) if compensation else None
        )

    def fetch_jobs(self) -> list[Job]:
        jobs: list[Job] = []
        seen_ids: set[str] = set()
        cursor: str | None = None

        while len(jobs) < self.results_wanted:
            results, next_cursor = self._fetch_page(cursor)

            if not results: break

            for result in results:
                raw = result["job"]
                job_id = raw["key"]

                if job_id in seen_ids: continue

                seen_ids.add(job_id)
                jobs.append(self._raw_to_job(raw))

                if len(jobs) >= self.results_wanted: break

            if not next_cursor: break

            cursor = next_cursor

        return jobs