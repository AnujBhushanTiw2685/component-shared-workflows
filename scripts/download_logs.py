import os
import urllib.request
import zipfile
import json

# with open("artifacts/failed_job.json", "r" ) as file:
#     failed_job = json.load(file)
# RUN_ID = failed_job["run_id"]


OWNER = os.environ["OWNER"]
REPOSITORY = os.environ["REPOSITORY"]
RUN_ID = os.environ["RUN_ID"]
TOKEN = os.environ["GITHUB_TOKEN"]

url = (
    f"https://api.github.com/repos/"
    f"{OWNER}/{REPOSITORY}/actions/runs/{RUN_ID}/logs"

)

request = urllib.request.Request(url)
request.add_header("Accept", "application/vnd.github+json")
request.add_header("Authorization", f"Bearer {TOKEN}")

response = urllib.request.urlopen(request)

# download the logs as a zip file

os.makedirs("artifacts", exist_ok=True)
with open("artifacts/workflow_logs.zip", "wb") as file:
    file.write(response.read())

print("Workflow logs downloaded successfully.")

# Extract the logs from the zip file

extract_folder = "artifacts/extracted_logs"

with zipfile.ZipFile("artifacts/workflow_logs.zip", "r") as zip_ref:
    zip_ref.extractall(extract_folder)

print(f"Logs extracted to '{extract_folder}'")


# Display the extracted log files

print("\nExtracted log files:\n")

for file in os.listdir(extract_folder):
    file_path = os.path.join(extract_folder, file)

    if os.path.isfile(file_path):
        print(file_path)

        