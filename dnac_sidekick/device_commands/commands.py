""" Commands to run CLI commands on network devices in DNAC inventory and view the output. """

import click
import requests
import json
import os


@click.command
@click.option(
    "--device", required=True, help="Specify a device's hostname to run commands."
)
@click.option(
    "--command", required=True, help="Specify a command to run on the specified device."
)
def command_runner(device, command):
    """Run 'show' commands on network devices in DNAC."""
    # Confirm all the necessary env vars are set
    dnac_url = os.environ.get("DNAC_URL")
    dnac_user = os.environ.get("DNAC_USER")
    dnac_pass = os.environ.get("DNAC_PASS")
    dnac_token = os.environ.get("DNAC_TOKEN")
    # Add values to context for read-only actions to use
    if None in (dnac_url, dnac_user, dnac_pass, dnac_token):
        raise click.ClickException("A necessary environment variable has not been set.")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Auth-Token": dnac_token,
    }
    dnac_devices_url = f"{dnac_url}/dna/intent/api/v1/network-device?hostname={device}"
    net_devices_resp = requests.get(url=dnac_devices_url, headers=headers, verify=False)
    if net_devices_resp.status_code == 200:
        dev_id = net_devices_resp.json()["response"][0].get("id")
        if not dev_id:
            raise click.ClickException("Device hostname not found in inventory.")
    dnac_command_run = (
        f"{dnac_url}/dna/intent/api/v1/network-device-poller/cli/read-request"
    )
    payload = {
        "timeout": 5,
        "description": "Just a simple command ran by DNAC sidekick",
        "name": "DNAC sidekick command run",
        "commands": [command],
        "deviceUuids": [dev_id],
    }
    # Run command, which kicks off a task in DNAC
    comm_run_resp = requests.post(
        url=dnac_command_run, headers=headers, json=payload, verify=False
    )
    if comm_run_resp.status_code == 202:
        task_id = comm_run_resp.json()["response"].get("taskId")
        if not task_id:
            raise click.ClickException("Task ID not found.")
    else:
        print("Could not get task ID.")
        print(f"Status code: {comm_run_resp.status_code}")
        print(f"Error: {comm_run_resp.text}")
    # Get task by ID
    task_check = f"{dnac_url}/api/v1/task/{task_id}"
    task_check_resp = requests.get(url=task_check, headers=headers, verify=False)
    if task_check_resp.status_code == 200:
        tasks_found = task_check_resp.json()["response"]
        task_end = tasks_found.get("endTime")
        while task_end is None:
            task_checkup = requests.get(url=task_check, headers=headers, verify=False)
            resp = task_checkup.json()["response"]
            end_time = resp.get("endTime")
            if end_time is not None:
                raw_file_id = json.loads(resp.get("progress"))
                file_id = raw_file_id.get("fileId")
                task_end = 0
    else:
        print(f"Status code: {task_check_resp.status_code}")
        print(f"Error! Error message: {task_check_resp.text}")
        raise click.ClickException("File ID not found.")
    # Get file by ID
    dnac_get_file = f"{dnac_url}/dna/intent/api/v1/file/{file_id}"
    file_resp = requests.get(url=dnac_get_file, headers=headers, verify=False)
    if net_devices_resp.status_code == 200:
        command_output = file_resp.json()[0]["commandResponses"]["SUCCESS"][command]
        print(command_output)
