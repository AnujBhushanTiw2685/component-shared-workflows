import os
import json
import urllib.request
import subprocess
# from datetime import datetime, timezone
# import shutil

OWNER = os.environ["OWNER"]
TOKEN = os.environ["GITHUB_TOKEN"]

DISPATCH_FILE = "artifacts/nightly_dispatches.json"

with open(DISPATCH_FILE,"r") as file:
    dispatches = json.load(file)


nightly_runs = []

def github_get(url):
    request = urllib.request.Request(url)
    request.add_header(
        "Accept",
        "application/vnd.github+json"
    )
    request.add_header(
        "Authorization",
        f"Bearer {TOKEN}"
    )
    request.add_header(
        "X-Github-Api-Version",
        "2022-11-28"
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())

# def parse_timestamp(timestamp):
#     return datetime.fromisoformat(
#         timestamp.replace("Z", "+00:00")
#     )

for dispatch in dispatches:
    repository = dispatch["repository"]
    workflow_id = dispatch["workflow_id"]
    # dispatch_time = dispatch["dispatch_time"]
    run_id = dispatch["run_id"]

    print("="*60)
    print(f"Fetching nightly run for {repository}")
    print("="*60)

    url = (
        f"https://api.github.com/repos/"
        f"{OWNER}/{repository}/actions/runs/{run_id}"
        # f"{workflow_id}/runs"
        # f"?event=workflow_dispatch&per_page=100"
    )

    # data = github_get(url)
    # workflow_runs = data.get("workflow_runs", [])

    # nightly_run = None

    # dispatch_datetime = parse_timestamp(dispatch_time)

    # for run in workflow_runs:
    #     created_at = run.get("created_at")

    #     if not created_at:
    #         continue

    #     created_datetime = parse_timestamp(created_at)

    #     # We want the workflow run created after our nightly dispatch 
    #     if created_datetime >= dispatch_datetime:
    #         nightly_run = run
    #         break

    run = github_get(url)

    print(
            f"Nightly run found: "
            f"{run['id']}"

    )

    print(
        f"Status: "
        f"{run['status']}"
        
    )

    print(
        f"Conclusion: "
        f"{run['conclusion']}"
        
    )

    nightly_runs.append({
        "owner": OWNER,
        "repository": repository,
        "run_id": run["id"],
        "status": run["status"],
        "conclusion": run["conclusion"],
        "run_url": run["html_url"]
    })


    # if nightly_run:
    #     print(
    #         f"Nightly run found: "
    #         f"{nightly_run['id']}"

    #     )

    #     print(
    #         f"Status: "
    #         f"{nightly_run['status']}"
            
    #     )

    #     print(
    #         f"Conclusion: "
    #         f"{nightly_run['conclusion']}"
            
    #     )

    #     nightly_runs.append({
    #         "owner": OWNER,
    #         "repository": repository,
    #         "run_id": nightly_run["id"],
    #         "status": nightly_run["status"],
    #         "conclusion": nightly_run["conclusion"],
    #         "run_url": nightly_run["html_url"]
    #     })

    # else:
    #     print(
    #         f"No nightly workflow run found"
    #         f"for {repository}"
    #     )

    #     nightly_runs.append({
    #         "owner": OWNER,
    #         "repository": repository,
    #         "run_id": "",
    #         "status": "not_triggered",
    #         "conclusion": "",
    #         "run_url": ""
    #     })

# Save nightly run information

os.makedirs("artifacts",exist_ok=True)

with open(
    "artifacts/nightly_runs.json",
    "w"
) as file:
    json.dump(
        nightly_runs,
        file,
        indent=4
    )

print("\n===== NIGHTLY SUMMARY =====")

print(
    json.dumps(
        nightly_runs,
        indent=4
    )
)

for run in nightly_runs:

    repository = run["repository"]

    # SUCCESS
    if run["status"] == "completed" and run["conclusion"] == "success":
        summary = {
            "repository": repository,
            "workflow": "Release Pipeline",
            "component": repository,
            "job": "",
            "status": "SUCCESS",
            "timestamp": "",
            "error": "",
            "run_id": run["run_id"],
            "run_url": run["run_url"],
            "exit_code": ""
        }

        with open(
            f"artifacts/{repository}_summary.json",
            "w"
        ) as file:
            json.dump(
                summary,
                file,
                indent=4
            )
        print(
            f"{repository} -> SUCCESS"
        )

    # FAILURE
    elif run["status"] == "completed" and run["conclusion"] == "failure":

        print(
            f"{repository} -> FAILURE"
        )

        env = os.environ.copy()

        env["OWNER"] = OWNER
        env["REPOSITORY"] = repository
        env["RUN_ID"] = str(run["run_id"])
        env["GITHUB_TOKEN"] = TOKEN

        env["OUTPUT_SUMMARY_FILE"] = (
            f"artifacts/{repository}_summary.json"
        )

        subprocess.run(
            [
                "python","scripts/fetch_workflow_jobs.py"
            ],
            check=True,
            env=env
        )

        subprocess.run(
            [
                "python","scripts/download_logs.py"
            ],
            check=True,
            env=env
        )
        subprocess.run(
            [
                "python","scripts/parse_logs.py"
            ],
            check=True,
            env=env
        )
    elif run["status"] == "queued":
        print(
            f"{repository} -> QUEUED"
            f"(nightly window expired)"
        )
        summary = {
            "repository": repository,
            "workflow": "Release Pipeline",
            "component": repository,
            "job": "",
            "status": "QUEUED",
            "timestamp": "",
            "error": (
                "Workflow was still queued when the "
                "nightly execution window expired."
            ),
            "run_id": run["run_id"],
            "run_url": run["run_url"],
            "exit_code": ""

        }
        with open(
            f"artifacts/{repository}_summary.json",
            "w"
        ) as file:
            json.dump(
                summary,
                file,
                indent=4
            )

    elif run["status"] == "in_progress":

        summary = {
            "repository": repository,
            "workflow": "Release Pipeline",
            "component": repository,
            "job": "",
            "status": "RUNNING",
            "timestamp": "",
            "error": (
                "Workflow was still running when the "
                "nightly execution window expired."
            ),
            "run_id": run["run_id"],
            "run_url": run["run_url"],
            "exit_code": ""
        }

        with open(
            f"artifacts/{repository}_summary.json",
            "w"
        ) as file:

            json.dump(
                summary,
                file,
                indent=4
            )

# for repository in components:

#     print("="*60)
#     print(f"Fetching latest nightly run for {repository}")
#     print("="*60)

#     url = (
#         f"https://api.github.com/repos/"
#         f"{OWNER}/{repository}/actions/runs"
#         f"?event=repository_dispatch&per_page=1"
#     )

#     request = urllib.request.Request(url)
#     request.add_header("Accept", "application/vnd.github+json")
#     request.add_header("Authorization", f"Bearer {TOKEN}")

#     with urllib.request.urlopen(request) as response:
#         data = json.loads(response.read())

#     workflow_runs = data.get("workflow_runs", [])

#     if workflow_runs:
#         run = workflow_runs[0]

#         nightly_runs.append({

#             "owner": OWNER,
#             "repository": repository,
#             "run_id": run["id"],
#             "status": run["status"],
#             "conclusion": run["conclusion"],
#             "run_url": run["html_url"]
            
#         })
#     else:
#         nightly_runs.append({

#             "owner": OWNER,
#             "repository": repository,
#             "run_id": "",
#             "status": "not_triggered",
#             "conclusion": "",
#             "run_url":  ""
            
#         })

# os.makedirs("artifacts", exist_ok=True)

# with open("artifacts/nightly_runs.json", "w") as file:
#     json.dump(nightly_runs, file, indent=4)

# print("\n===== NIGHTLY SUMMARY =====")
# print(json.dumps(nightly_runs, indent=4))

# print("\n===== PROCESSING COMPONENTS =====\n")

# for run in nightly_runs:
#     repository = run["repository"]

#     #success
#     if run["conclusion"] == "success":
#         summary = {
#             "repository": repository,
#             "workflow": run.get("workflow_name", ""),
#             "component": repository,
#             "job": "",
#             "status": "SUCCESS",
#             "timestamp": "",
#             "error": "",
#             "run_id": run["run_id"],
#             "run_url": run["run_url"],
#             "exit_code": ""
#         }
#         with open(f"artifacts/{repository}_summary.json", "w") as file:
#             json.dump(summary, file, indent=4)
#         print(f"{repository} -> SUCCESS")

#     #failure
#     elif run["conclusion"] == "failure":

#         print(f"{repository} -> FAILURE")

#         env = os.environ.copy()

#         env["OWNER"] = OWNER
#         env["REPOSITORY"] = repository
#         env["RUN_ID"] = str(run["run_id"])

#         env["OUTPUT_SUMMARY_FILE"] = (
#             f"artifacts/{repository}_summary.json"
#         )
#         try:
#             subprocess.run(
#                     ["python", "scripts/fetch_workflow_jobs.py"],
#                     check=True,
#                     env=env,
#             )
            
#             subprocess.run(
#                     ["python", "scripts/download_logs.py"],
#                     check=True,
#                     env=env,
#             )
            
#             subprocess.run(
#                     ["python", "scripts/parse_logs.py"],
#                     check=True,
#                     env=env,
#             )
#         except subprocess.CalledProcessError as e:
#             print(f"Failed to process {repository}: {e}")
#             summary = {

#                 "repository": repository,
#                 "workflow": run.get("workflow_name",""),
#                 "component": repository,
#                 "job": "",
#                 "status": "PROCESSING_FAILED",
#                 "timestamp": "",
#                 "error": str(e),
#                 "run_id": run["run_id"],
#                 "run_url": run["run_url"],
#                 "exit_code": ""

#             }

#             with open(
#                 f"artifacts/{repository}_summary.json",
#                 "w"
#             ) as file:
#                 json.dump(summary, file, indent=4)



        
    