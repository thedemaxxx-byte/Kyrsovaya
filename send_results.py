import os
import json
import requests


def main():
    print("Preparing execution logs...")
    # Read pytest execution log
    log_content = ""
    if os.path.exists("pytest_execution.log"):
        try:
            with open("pytest_execution.log", "r", encoding="utf-8", errors="ignore") as f:
                log_content = f.read().replace('\x00', '')
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
    
    dify_text = ""
    try:
        response = requests.post(dify_url, headers=headers, json=payload)
        print(f"Dify response status code: {response.status_code}")
        print("Dify response body:")
        print(response.text)
        if response.status_code == 200:
            try:
                res_json = response.json()
                dify_text = res_json.get("data", {}).get("outputs", {}).get("text", "")
            except Exception as je:
                print(f"Failed to parse Dify JSON response: {je}")
    except Exception as e:
        print(f"Failed to send request to Dify API: {e}")

    # Update dashboard.html locally on the runner with latest test execution data
    print("Updating dashboard.html with latest run results...")
    import re
    from datetime import datetime

    run_number = int(os.environ.get("GITHUB_RUN_NUMBER", "0"))
    run_id = os.environ.get("GITHUB_RUN_ID", "0")
    commit_sha = os.environ.get("GITHUB_SHA", "unknown")
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    event = os.environ.get("GITHUB_EVENT_NAME", "workflow_dispatch")
    
    pytest_status = "success"
    if "FAILED" in log_content:
        pytest_status = "failure"
        
    now_iso = datetime.utcnow().isoformat() + "Z"
    
    steps = [
        {"name": "Set up job", "conclusion": "success", "started_at": now_iso, "completed_at": now_iso},
        {"name": "Checkout repository", "conclusion": "success", "started_at": now_iso, "completed_at": now_iso},
        {"name": "Install dependencies", "conclusion": "success", "started_at": now_iso, "completed_at": now_iso},
        {"name": "Patch tests for compatibility", "conclusion": "success", "started_at": now_iso, "completed_at": now_iso},
        {"name": "Run Tests for котософт.рф", "conclusion": pytest_status, "started_at": now_iso, "completed_at": now_iso},
        {"name": "Generate Allure Report", "conclusion": "success", "started_at": now_iso, "completed_at": now_iso},
        {"name": "Send results to Dify", "conclusion": "success", "started_at": now_iso, "completed_at": now_iso}
    ]
    
    current_run_data = {
        "id": int(run_id) if run_id.isdigit() else 0,
        "run_number": run_number,
        "display_title": "Dify Test Run" if event == "repository_dispatch" else "Manual Run",
        "conclusion": pytest_status,
        "created_at": now_iso,
        "run_started_at": now_iso,
        "updated_at": now_iso,
        "duration_seconds": 20,
        "head_branch": branch,
        "event": event,
        "requirements_text": requirements_text,
        "dify_response": dify_text,
        "pytest_logs": log_content_truncated,
        "allure_data": allure_data,
        "jobs": [
            {
                "name": "test-execution",
                "status": "completed",
                "conclusion": pytest_status,
                "steps": steps
            }
        ]
    }
    
    history = []
    files = {}
    if os.path.exists("dashboard.html"):
        try:
            with open("dashboard.html", "r", encoding="utf-8") as f:
                dash_content = f.read()
                
            # Use dynamic pattern to prevent self-matching during script serialization
            pattern = r'// ' + r'__LOCAL_DATA_START__\s*const LOCAL_DATA = (.*?);\s*// ' + r'__LOCAL_DATA_END__'
            match = re.search(pattern, dash_content, re.DOTALL)
            if match:
                old_local_data_str = match.group(1).strip()
                if old_local_data_str != "null":
                    old_data = json.loads(old_local_data_str)
                    history = old_data.get("history", [])
                    files = old_data.get("files", {})
        except Exception as e:
            print(f"Failed to read existing LOCAL_DATA: {e}")
            
    history.insert(0, current_run_data)
    history = history[:15]
    
    for filename in ["test_kotosoft.py", "send_results.py"]:
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    files[filename] = f.read()
            except Exception as e:
                print(f"Failed to read {filename} content: {e}")
                
    new_local_data = {
        "latest_run": current_run_data,
        "history": history,
        "files": files
    }
    
    if os.path.exists("dashboard.html"):
        try:
            with open("dashboard.html", "r", encoding="utf-8") as f:
                dash_content = f.read()
                
            json_str = json.dumps(new_local_data, ensure_ascii=False, indent=2)
            
            start_marker = '// ' + '__LOCAL_DATA_START__'
            end_marker = '// ' + '__LOCAL_DATA_END__'
            start_idx = dash_content.find(start_marker)
            # Use rfind to find the actual marker at the end of the script block
            end_idx = dash_content.rfind(end_marker)
            
            if start_idx != -1 and end_idx != -1:
                new_dash_content = (
                    dash_content[:start_idx] +
                    start_marker + "\n        const LOCAL_DATA = " + json_str + ";\n        " +
                    dash_content[end_idx:]
                )
                with open("dashboard.html", "w", encoding="utf-8") as f:
                    f.write(new_dash_content)
                print("Successfully updated dashboard.html with LOCAL_DATA")
            else:
                print("Error: Could not find LOCAL_DATA markers in dashboard.html")
        except Exception as e:
            print(f"Failed to write updated dashboard.html: {e}")


if __name__ == "__main__":
    main()
