#!/usr/bin/env python3
"""
CatAPI Bug Reporter
This script automatically creates a Jira ticket when the test_vote_count_increases test fails.
It captures relevant information about the failure and formats it into a structured bug report.
"""

import os
import sys
import json
import logging
import argparse
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('cat_api_bug_reporter')


class JiraBugReporter:
    """Client for reporting bugs to Jira when CatAPI tests fail."""

    def __init__(self, jira_url, project_key, username, api_token):
        """
        Initialize the Jira Bug Reporter.

        Args:
            jira_url (str): Base URL for your Jira instance
            project_key (str): Jira project key where bugs should be created
            username (str): Jira username
            api_token (str): Jira API token or password
        """
        self.jira_url = jira_url.rstrip('/')
        self.project_key = project_key
        self.auth = HTTPBasicAuth(username, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def create_bug_report(self, test_name, error_details, api_responses=None, environment=None):
        """
        Create a bug report in Jira.

        Args:
            test_name (str): Name of the failing test
            error_details (str): Details of the test error
            api_responses (dict, optional): Dictionary of API responses collected during test
            environment (dict, optional): Environment information

        Returns:
            dict: Response from Jira API
        """
        # Format current datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build environment information
        env_info = "Not provided"
        if environment:
            env_info = "\n".join([f"- {k}: {v}" for k, v in environment.items()])

        # Format API responses
        api_response_text = "Not provided"
        if api_responses:
            api_response_text = "```json\n"
            api_response_text += json.dumps(api_responses, indent=2)
            api_response_text += "\n```"

        # Create description with all collected information
        description = f"""
Vote count not incrementing properly when voting for images via CatAPI

*Reported at: {current_time}*

h2. Description
When voting for an image using the CatAPI, the vote count does not increase as expected. This issue was detected by our automated test suite (specifically {test_name}).

h2. Steps to Reproduce
# Set up an image that already has 3 votes
# Cast a new vote for this image
# Retrieve the vote count for the image
# Verify that the vote count has increased by 1

h2. Expected Result
The vote count should increase from 3 to 4 after casting a new vote.

h2. Actual Result
The vote count remains at 3 or returns an incorrect value after the new vote is cast.

h2. Error Details
{error_details}

h2. Environment Information
{env_info}

h2. API Response Data
{api_response_text}

h2. Impact
This issue affects the core voting functionality of the application. Users' votes may not be properly counted, which impacts engagement metrics and feature reliability.

h2. Possible Causes
* Vote is not being properly saved in the database
* Vote count calculation logic is incorrect
* Race condition in the voting process
* Caching issue where new votes aren't reflected immediately
"""

        # Create the issue in Jira
        url = f"{self.jira_url}/rest/api/2/issue"

        payload = json.dumps({
            "fields": {
                "project": {
                    "key": self.project_key
                },
                "summary": "Vote count not incrementing properly when voting for images via CatAPI",
                "description": description,
                "issuetype": {
                    "name": "Bug"
                },
                "priority": {
                    "name": "High"
                },
                "labels": ["catapi", "voting", "automated-test-failure"],
                "components": [
                    {"name": "CatAPI Voting System"}
                ]
            }
        })

        try:
            response = requests.post(
                url,
                data=payload,
                headers=self.headers,
                auth=self.auth
            )

            if response.status_code == 201:
                result = response.json()
                logger.info(f"Successfully created Jira issue: {result['key']}")
                return result
            else:
                logger.error(f"Failed to create Jira issue. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Exception occurred while creating Jira ticket: {str(e)}")
            return None

    def attach_file_to_issue(self, issue_key, file_path, filename=None):
        """
        Attach a file to an existing Jira issue.

        Args:
            issue_key (str): The Jira issue key (e.g., 'PROJ-123')
            file_path (str): Path to the file to attach
            filename (str, optional): Name to use for the file in Jira

        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False

        url = f"{self.jira_url}/rest/api/2/issue/{issue_key}/attachments"

        headers = {
            "X-Atlassian-Token": "no-check"
        }

        if not filename:
            filename = os.path.basename(file_path)

        files = {
            "file": (filename, open(file_path, "rb"))
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                auth=self.auth,
                files=files
            )

            if response.status_code == 200:
                logger.info(f"Successfully attached file to {issue_key}")
                return True
            else:
                logger.error(f"Failed to attach file. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Exception occurred while attaching file: {str(e)}")
            return False


def collect_environment_info():
    """Collect information about the test environment."""
    return {
        "Python Version": sys.version,
        "Operating System": sys.platform,
        "Timestamp": datetime.now().isoformat(),
        "Test Framework": "PyTest"
    }


def parse_pytest_output(output_file):
    """
    Parse pytest output to extract error details.

    Args:
        output_file (str): Path to the file containing pytest output

    Returns:
        str: Extracted error message
    """
    try:
        with open(output_file, 'r') as f:
            content = f.read()

        # Very simple parsing - in a real implementation you'd want more robust parsing
        error_section = ""
        in_error_section = False

        for line in content.split('\n'):
            if 'test_vote_count_increases' in line and 'FAILED' in line:
                in_error_section = True
                error_section = line + "\n"
            elif in_error_section:
                error_section += line + "\n"
                if line.strip() == "":  # Empty line might indicate end of error section
                    if not any(
                            keyword in error_section.lower() for keyword in ["error", "assert", "fail", "exception"]):
                        in_error_section = False

        return error_section if error_section else "Could not parse error details from test output."
    except Exception as e:
        return f"Error parsing test output: {str(e)}"


def main():
    """Main function to handle command line arguments and create the bug report."""
    parser = argparse.ArgumentParser(description='Report CatAPI test failures to Jira')

    # Jira connection arguments
    parser.add_argument('--jira-url', required=False, default=os.environ.get('JIRA_URL'),
                        help='Jira URL (can also set JIRA_URL env var)')
    parser.add_argument('--project-key', required=False, default=os.environ.get('JIRA_PROJECT_KEY'),
                        help='Jira project key (can also set JIRA_PROJECT_KEY env var)')
    parser.add_argument('--username', required=False, default=os.environ.get('JIRA_USERNAME'),
                        help='Jira username (can also set JIRA_USERNAME env var)')
    parser.add_argument('--api-token', required=False, default=os.environ.get('JIRA_API_TOKEN'),
                        help='Jira API token (can also set JIRA_API_TOKEN env var)')

    # Test information
    parser.add_argument('--test-output', required=False, default='pytest_output.txt',
                        help='File containing pytest output')
    parser.add_argument('--api-responses', required=False, default=None,
                        help='JSON file containing API responses from the test')
    parser.add_argument('--log-file', required=False, default=None,
                        help='Log file to attach to the Jira ticket')

    args = parser.parse_args()

    # Validate required arguments
    missing_args = []
    for arg_name in ['jira_url', 'project_key', 'username', 'api_token']:
        if getattr(args, arg_name) is None:
            missing_args.append(arg_name)

    if missing_args:
        formatted_args = ', '.join([f'--{arg.replace("_", "-")}' for arg in missing_args])
        parser.error(f"Missing required arguments: {formatted_args}")

    # Parse API responses if provided
    api_responses = None
    if args.api_responses and os.path.exists(args.api_responses):
        try:
            with open(args.api_responses, 'r') as f:
                api_responses = json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Error parsing API responses file: {args.api_responses}")
            api_responses = {"error": "Failed to parse API responses"}

    # Parse test output
    error_details = "No test output provided"
    if args.test_output and os.path.exists(args.test_output):
        error_details = parse_pytest_output(args.test_output)

    # Collect environment information
    env_info = collect_environment_info()

    # Create Jira client
    jira_client = JiraBugReporter(
        args.jira_url,
        args.project_key,
        args.username,
        args.api_token
    )

    # Create the bug report
    result = jira_client.create_bug_report(
        "test_vote_count_increases",
        error_details,
        api_responses,
        env_info
    )

    # Attach log file if provided
    if result and args.log_file and os.path.exists(args.log_file):
        jira_client.attach_file_to_issue(result['key'], args.log_file)


if __name__ == "__main__":
    main()