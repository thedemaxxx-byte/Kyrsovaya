import os
import json
import requests


def main():
    print("Preparing execution logs...")
    # Read pytest execution log
    log_content = ""
    if os.path.exists("pytest_execution.log"):
        try:
            with open("pytest_execution.log", "r", encoding="utf-8") as f:
                log_content = f.read()
            print("Successfully read pytest_execution.log")
        except Exception as e:
            print(f"Error reading log file: {e}")

    # Read Allure JSON data
    allure_data = []
    allure_results_dir = "allure-results"
    if os.path.exists(allure_results_dir):
        print(f"Reading Allure JSON files from {allure_results_dir}...")
        for filename in os.listdir(allure_results_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(allure_results_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        allure_data.append(json.load(f))
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
    else:
        print("Allure results directory not found")

    # Limit payload sizes to prevent LLM context overflow
    log_content_truncated = (
        log_content[-8000:] if log_content else "No logs found"
    )
    allure_json_str = (
        json.dumps(allure_data)[:8000] if allure_data else "[]"
    )

    # Send request to Dify Workflow API
    dify_api_key = os.environ.get("DIFY_API_KEY")
    if not dify_api_key:
        print("Error: DIFY_API_KEY environment variable is not set.")
        return

    # Get requirements_text from environment (passed from Dify via
    # repository_dispatch payload) or use a default description
    requirements_text = os.environ.get(
        "REQUIREMENTS_TEXT",
        "Проверка доступности главной страницы сайта котософт.рф, "
        "наличия ключевых UI элементов, проверка наличия Салют"
    )

    # Endpoint URL for running a workflow in Dify
    dify_url = "https://api.dify.ai/v1/workflows/run"

    headers = {
        "Authorization": f"Bearer {dify_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": {
            "requirements_text": requirements_text,
            "execution_logs": log_content_truncated,
            "allure_json_data": allure_json_str
        },
        "response_mode": "blocking",
        "user": "github-actions"
    }

    print(f"Requirements: {requirements_text}")
    print(f"Sending payload to Dify Workflow API at {dify_url}...")
    try:
        response = requests.post(dify_url, headers=headers, json=payload)
        print(f"Dify response status code: {response.status_code}")
        print("Dify response body:")
        print(response.text)
    except Exception as e:
        print(f"Failed to send request to Dify API: {e}")


if __name__ == "__main__":
    main()
