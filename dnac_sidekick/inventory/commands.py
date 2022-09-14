""" Commands to gather information related to device inventory in DNAC """

import click
from rich.table import Table
from rich.console import Console
import requests


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
    if hostname:
        dnac_devices_url = (
            f"{ctx.obj.dnac_url}/dna/intent/api/v1/network-device?hostname={hostname}"
        )
    else:
        dnac_devices_url = f"{ctx.obj.dnac_url}/dna/intent/api/v1/network-device"
    response = requests.get(url=dnac_devices_url, headers=headers, verify=False)
    if response.status_code == 200:
        device_list = response.json()["response"]
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
        # click.echo(f"Here's a list of devices: {console.print(table)}")
    elif response.status_code == 401:
        click.echo("Unauthorized. Please verify your token is valid.")
        click.echo(response.text)
    else:
        click.echo("Could not retrieve list of network devices from DNAC.")
