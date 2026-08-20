import json
import glob
import os

MODE = os.environ.get("MODE", "manual")

summaries = []

# Load Summary Files

if MODE == "manual":

    with open("artifacts/failure_summary.json", "r") as file:
        summaries.append(json.load(file))

else:

    for file in sorted(glob.glob("artifacts/*_summary.json")):

        with open(file, "r") as f:
            summaries.append(json.load(f))


# MANUAL EMAIL

if MODE == "manual":

    failure = summaries[0]

    repository = failure["repository"]
    workflow = failure["workflow"]
    component = failure["component"]
    job = failure["job"]
    status = failure["status"]
    timestamp = failure["timestamp"]
    error = failure["error"]
    run_id = failure["run_id"]
    run_url = failure["run_url"]
    exit_code = failure["exit_code"]

    with open(
        "templates/email_template.html",
        "r",
        encoding="utf-8"
    ) as file:

        html = file.read()

    html = html.replace("{{REPOSITORY}}", repository)
    html = html.replace("{{WORKFLOW}}", workflow)
    html = html.replace("{{COMPONENT}}", component)
    html = html.replace("{{JOB}}", job)
    html = html.replace("{{STATUS}}", status)
    html = html.replace("{{TIMESTAMP}}", timestamp)
    html = html.replace("{{ERROR}}", error)
    html = html.replace("{{RUN_ID}}", str(run_id))
    html = html.replace("{{RUN_URL}}", run_url)
    html = html.replace("{{EXIT_CODE}}", exit_code)

# NIGHTLY EMAIL

else:

    with open(
        "templates/nightly_email_template.html",
        "r",
        encoding="utf-8"
    ) as file:

        html = file.read()

    rows = ""

    passed = 0
    failed = 0
    queued = 0
    running = 0

    for summary in summaries:

        status = summary["status"]

        if status.upper() == "SUCCESS":
            css = "success"
            passed += 1
        elif status.upper() == "FAILURE":
            css = "failure"
            failed += 1
        elif status.upper() == "QUEUED":
            css = "queued"
            queued += 1
        elif status.upper() == "RUNNING":
            css = "running"
            running += 1
        else:
            css = "failure"
            failed += 1

        job = summary["job"] if summary["job"] else "-"
        error = summary["error"] if summary["error"] else "-"

        rows += f"""
        <tr>
            <td>{summary["component"]}</td>

            <td class="{css}">
                {status}
            </td>

            <td>
                {job}
            </td>

            <td>
                {error}
            </td>

            <td>
                <a href="{summary["run_url"]}">
                    Open Workflow
                </a>
            </td>
        </tr>
        """

    html = html.replace(
        "{{TABLE_ROWS}}",
        rows
    )

    html = html.replace(
        "{{TOTAL}}",
        str(len(summaries))
    )

    html = html.replace(
        "{{PASSED}}",
        str(passed)
    )

    html = html.replace(
        "{{FAILED}}",
        str(failed)
    )
    html = html.replace(
        "{{QUEUED}}",
        str(queued)
    )

    html = html.replace(
        "{{RUNNING}}",
        str(running)
    )



# Write HTML

with open(
    "artifacts/notification.html",
    "w",
    encoding="utf-8"
) as file:

    file.write(html)

print("HTML notification generated successfully.")
print("Location: artifacts/notification.html")