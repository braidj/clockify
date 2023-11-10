import requests
import json
from datetime import datetime

# Clockify API URL and authentication credentials
CLOCKIFY_API_URL = 'https://api.clockify.me/api/v1/'
API_KEY = 'MDYwYjIzYzgtYmY1ZS00ZGJjLTk2MTEtYTQyNWY3NzQ3MmZi'  # Replace with your Clockify API key

# Define the report parameters
workspace_id = '5ec2dd1a033e3636e7ecccaf'  # Replace with your workspace ID
start_date = '2023-01-01T00:00:00Z'  # Replace with your start date and time
end_date = '2023-01-31T23:59:59Z'    # Replace with your end date and time

# Define the request headers with API key
headers = {
    'X-Api-Key': API_KEY,
    'Content-Type': 'application/json',
}

# Define the request body with report parameters
report_data = {
    "dateRangeStart": start_date,
    "dateRangeEnd": end_date,
    "summaryFilter": {"groups": ["user"]},
    "exportType": "JSON",
}

# Make the API request to generate the report
report_url = f'{CLOCKIFY_API_URL}workspaces/{workspace_id}/reports/summary'
response = requests.post(report_url, headers=headers, data=json.dumps(report_data))

# Check if the request was successful (HTTP status code 200)
if response.status_code == 200:
    # Parse the JSON response
    report = response.json()
    
    # Save the report data to a file
    report_filename = 'clockify_report.json'
    with open(report_filename, 'w') as report_file:
        json.dump(report, report_file, indent=4)
    
    print(f'Detailed report has been saved to {report_filename}')
else:
    print(f'Failed to retrieve report. Status code: {response.status_code}')






data = {'x-api-key': API_KEY}
r = requests.get('https://api.clockify.me/api/v1/user', headers=data)
print(r.content)
