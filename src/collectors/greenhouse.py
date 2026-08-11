import httpx
import json

# ## All currently published DoorDash jobs
# url = "https://boards-api.greenhouse.io/v1/boards/doordashusa/jobs"

# response = httpx.get(url)
# response.raise_for_status()

# jobs = response.json()["jobs"]

# for job in jobs:
#     print(job["id"], job["title"], job["location"]["name"])

# # Specific job with ID 7263610
# url = "https://boards-api.greenhouse.io/v1/boards/doordashusa/jobs/7263610"

# response = httpx.get(url)
# response.raise_for_status()

# job = response.json()

# print(job["title"])
# print(job["location"]["name"])

url = "https://boards-api.greenhouse.io/v1/boards/doordashusa/jobs"
params = {"content": "true"}

response = httpx.get(url, params=params)
response.raise_for_status()

data = response.json()

print(f"Found {len(data['jobs'])} jobs")

# print(json.dumps(data["jobs"], indent=4))

for job in data["jobs"][:1]:
    print(job.keys())
    print(job.values())

