""" Commands to gather health information for network devices and clients in DNAC """

import click
from rich.table import Table
from rich.console import Console
import requests


@click.command()
@click.pass_context
def devices(ctx):
    """Retrieve device health for all devices in DNAC inventory"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Auth-Token": ctx.obj.token,
    }
    dnac_device_health = f"{ctx.obj.dnac_url}/dna/intent/api/v1/device-health"
    response = requests.get(url=dnac_device_health, headers=headers, verify=False)
    if response.status_code == 200:
        device_list = response.json()["response"]
        table = Table(title="DNAC Network Health")
        table.add_column("Hostname", justify="left", style="purple")
        table.add_column("Overall Health", justify="left", style="cyan")
        table.add_column("CPU Util (%)", justify="center", style="green")
        table.add_column("Memory Util (%)", justify="right", style="red")

        for device in device_list:
            if device.get("overallHealth", -1) < 0:
                device_overall = "N/A"
            else:
                device_overall = str(device.get("overallHealth", "N/A"))
            cpu_util = round(device.get("cpuUlitilization", 0), 1)
            device_cpu_util = str(cpu_util)
            mem_util = round(device.get("memoryUtilization", 0), 1)
            device_mem_util = str(mem_util)
            table.add_row(
                device["name"], device_overall, device_cpu_util, device_mem_util
            )

        console = Console()
        console.print(table)
    elif response.status_code == 401:
        click.echo("Unauthorized. Please verify your token is valid.")
    else:
        click.echo("Could not retrieve list of network devices from DNAC.")


@click.command()
@click.pass_context
def clients(ctx):
    """Retrieve client health for all tracked clients in DNAC"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Auth-Token": ctx.obj.token,
    }
    dnac_client_health = f"{ctx.obj.dnac_url}/dna/intent/api/v1/client-health"
    response = requests.get(url=dnac_client_health, headers=headers, verify=False)
    if response.status_code == 200:
        device_list = response.json()["response"]
        table = Table(title="DNAC Client Health")
        table.add_column("Client Type", justify="left", style="purple")
        table.add_column("Client Count", justify="center", style="cyan")
        table.add_column("Client Health Score", justify="right", style="green")

        for device in device_list:
            if device.get("siteId") == "global":
                for score in device.get("scoreDetail"):
                    client_type = score["scoreCategory"]["value"]
                    client_count = (
                        str(score["clientCount"]) if score["clientCount"] > 0 else "0"
                    )
                    client_score = (
                        str(score["scoreValue"]) if score["scoreValue"] > 0 else "0"
                    )

                    table.add_row(client_type, client_count, client_score)

        console = Console()
        console.print(table)
    elif response.status_code == 401:
        click.echo("Unauthorized. Please verify your token is valid.")
    else:
        click.echo("Could not retrieve list of network devices from DNAC.")
