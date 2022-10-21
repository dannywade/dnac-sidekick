""" Commands to generate testbeds and other inventory files sourcing from DNAC inventory """

import json
import click
from dnac_sidekick.inventory.commands import devices
from jinja2 import Environment, FileSystemLoader
import os
from rich import print
from rich.table import Table
from rich.console import Console
import requests


@click.command()
@click.option(
    "--output",
    type=click.Choice(["yaml"], case_sensitive=False),
    default="yaml",
    show_default=True,
    help="Specify an output format",
)
@click.pass_context
def pyats_testbed(ctx, output):
    """Retrieve device health for all devices in DNAC inventory"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Auth-Token": ctx.obj.token,
    }
    # Get available CLI device credentials stored in DNAC
    dnac_device_creds = f"{ctx.obj.dnac_url}/dna/intent/api/v1/device-credential"
    response = requests.get(url=dnac_device_creds, headers=headers, verify=False)
    if response.status_code == 200:
        cli_creds = response.json()["cli"]
        users = []
        for cred in cli_creds:
            users.append(cred["username"])
        if os.environ.get("DNAC_CLI_USER"):
            selected_user = os.environ.get("DNAC_CLI_USER")
        else:
            selected_user = click.prompt(
                f"Which username would you like to use {users}"
            )
        if os.environ.get("DNAC_CLI_PASS"):
            selected_pass = os.environ.get("DNAC_CLI_PASS")
        else:
            selected_pass = click.prompt(
                f"What's the CLI password for {selected_user}?"
            )
        if click.confirm("Is enable password the same as previous password?"):
            enable_pass = selected_pass
        else:
            enable_pass = click.prompt(
                f"What's the enable password for {selected_user}?"
            )
    elif response.status_code == 401:
        click.echo("Unauthorized. Please verify your token is valid.")
    else:
        click.echo("Could not retrieve device credentials from DNAC.")

    device_list = ctx.invoke(devices, output="json")
    device_list = json.loads(device_list)

    if (selected_user, selected_pass, enable_pass):
        table_data = {
            "user": selected_user,
            "pass": selected_pass,
            "enable_pass": enable_pass,
            "device_data": device_list,
        }
    else:
        raise click.ClickException("Device credentials not found.")

    if output == "yaml":
        # print(table_data)
        current_dir = os.path.dirname(os.path.realpath(__file__))
        env = Environment(loader=FileSystemLoader(f"{current_dir}/j2_templates"))
        tb_template = env.get_template("pyats_testbed.j2")
        generated_tb = tb_template.render(**table_data)
        with open("pyats_testbed.yaml", "w") as outfile:
            outfile.write(generated_tb)
            print(
                f"[bold bright_yellow]YAML testbed saved at {os.path.dirname(os.getcwd())}/pyats_testbed.yaml[/bold bright_yellow]"
            )
