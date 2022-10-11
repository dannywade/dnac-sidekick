""" Commands to gather information related to device inventory in DNAC """

import click
from math import ceil
from rich.table import Table
from rich.console import Console
import requests


@click.pass_context
def get_device_count(ctx):
    """Retrieve device count from DNAC inventory"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Auth-Token": ctx.obj.token,
    }
    if not ctx.obj.dnac_url:
        raise click.ClickException(
            "DNAC URL has not been provided and has not been set as an environment variable."
        )
    device_count_url = f"{ctx.obj.dnac_url}/dna/intent/api/v1/network-device/count"
    response = requests.get(url=device_count_url, headers=headers, verify=False)
    if response.status_code == 200:
        device_count = response.json()["response"]
        return device_count


@click.command
@click.option(
    "--hostname",
    default="",
    help="Specify a device's hostname to retrieve from inventory",
)
@click.pass_context
def devices(ctx, hostname):
    """Retrieve all devices from DNAC inventory"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Auth-Token": ctx.obj.token,
    }
    if not ctx.obj.dnac_url:
        raise click.ClickException(
            "DNAC URL has not been provided and has not been set as an environment variable."
        )
    # Get total number of devices to figure out offset for larger inventories
    total_dev_count = get_device_count()
    # Default and max limit for device inventory is 500, so we need to figure out how many API calls to make
    total_pages = ceil(total_dev_count / 500)
    if hostname:
        dnac_devices_url = (
            f"{ctx.obj.dnac_url}/dna/intent/api/v1/network-device?hostname={hostname}"
        )
        response = requests.get(url=dnac_devices_url, headers=headers, verify=False)
        device_list = response.json()["response"]
    else:
        # Since hostname was not provided, get all devices from DNAC inventory
        # There's a hard limit to only return 500 devices per call, so we must change the params
        # if there's more than 500 devices in the inventory
        # Initialize device list
        device_list = []
        for page in range(total_pages):
            # Make additional calls (if necessary) - needed for inventories with more than 500 devices
            calc_offset = page * 500
            if calc_offset > 0:
                dnac_devices_url = f"{ctx.obj.dnac_url}/dna/intent/api/v1/network-device?limit=500&offset={calc_offset}"
            else:
                # No offset needed
                dnac_devices_url = (
                    f"{ctx.obj.dnac_url}/dna/intent/api/v1/network-device?limit=500"
                )
            response = requests.get(
                url=dnac_devices_url,
                headers=headers,
                verify=False,
            )
            if response.status_code == 200:
                # Add devices to the response from the initial call
                device_list.extend(response.json()["response"])
            else:
                raise click.ClickException(
                    f"There was an error collecting the device inventory. HTTP code: {response.status_code}. Error message: {response.text}"
                )
    if device_list:
        # Output nicely formatted table of inventory devices
        table = Table(title="DNAC Network Devices")
        table.add_column("Hostname", justify="left", style="purple")
        table.add_column("Device Type", justify="left", style="cyan")
        table.add_column("Serial Number", justify="center", style="green")
        table.add_column("Software Version", justify="right", style="red")

        for device in device_list:
            table.add_row(
                device["hostname"],
                device["type"],
                device["serialNumber"],
                device["softwareVersion"],
            )

        console = Console()
        console.print(table)
    elif response.status_code == 401:
        click.echo("Unauthorized. Please verify your token is valid.")
        click.echo(response.text)
    else:
        click.echo("Could not retrieve list of network devices from DNAC.")
