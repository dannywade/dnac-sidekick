""" Commands to generate testbeds and other inventory files sourcing from DNAC inventory """

import json
import click
from dnac_sidekick.helpers.topology import get_assigned_devices, get_site_hierarchy
from dnac_sidekick.inventory.commands import devices
from jinja2 import Environment, FileSystemLoader
import os
from rich import print
import requests
import yaml


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
    """Generate pyATS testbed of all devices in DNAC inventory"""
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


# @click.command()
# @click.option(
#     "--output",
#     type=click.Choice(["yaml"], case_sensitive=False),
#     default="yaml",
#     show_default=True,
#     help="Specify an output format",
# )
def ansible_inventory():
    """Generate Ansible inventory of all devices in DNAC inventory"""
    site_topo = get_site_hierarchy()
    devices = get_assigned_devices()
    inventory = {"all": {"children": {}}}
    # Create site hierarchy, then add devices
    # Create top-level sites in hierarchy
    for site_id, dets in site_topo.items():
        if dets["groupNameHierarchy"].count("/") == 1:
            # Confirms that parentId is 'Global' and is a top-level "area" in DNAC
            inventory["all"]["children"].update(
                {dets["name"]: {"children": {}, "hosts": {}}}
            )
    # Add sites that are belong to a parent site
    for site_id, dets in site_topo.items():
        for key, val in site_topo.items():
            if key == dets["parentId"]:
                inventory["all"]["children"][val["name"]]["children"].update(
                    {dets["name"]: {"hosts": {}}}
                )

    # TODO: Add devices to their assigned sites

    print(yaml.dump(inventory))


if __name__ == "__main__":
    ansible_inventory()
