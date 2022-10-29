""" Commands to generate testbeds and other inventory files sourcing from DNAC inventory """

import ast
import json
import click
from dnac_sidekick.helpers.topology import (
    get_assigned_devices,
    get_site_hierarchy,
    iterate_all,
)
from dnac_sidekick.inventory.commands import devices
from genie.utils import Dq
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
    inventory = {"all": {"children": {}, "hosts": {}}}
    # Create site hierarchy, then add devices
    # Create top-level sites in hierarchy
    for dets in site_topo.values():
        if dets["groupNameHierarchy"].count("/") == 1:
            # Confirms that parentId is 'Global' and is a top-level "area" in DNAC
            inventory["all"]["children"].update(
                {dets["name"]: {"children": {}, "hosts": {}}}
            )
    # Add sites that are belong to a parent site
    for dets in site_topo.values():
        for key, val in site_topo.items():
            # TODO: Create recursive algorithm to discover all parents
            if key == dets["parentId"]:
                inventory["all"]["children"][val["name"]]["children"].update(
                    {dets["name"]: {"hosts": {}}}
                )

    for dev in devices.values():
        if dev["siteId"] != "unassigned":
            for site_id, dets in site_topo.items():
                if dev["siteId"] == site_id:
                    site_loc = Dq(inventory).contains(dets["name"]).reconstruct()
                    # Captures entire path needed to add hosts to a particular site in a list
                    site_list = list(iterate_all(site_loc))
                    print(site_list)
                    inv_str_eval = "inventory"
                    # Creates a string that will have the proper syntax to find the proper "hosts" key
                    # For ex: inventory["all"]["children"]["san_jose"]["children"]["sjc_20"]["hosts"]
                    for idx, site in enumerate(site_list):
                        if site != site_list:
                            inv_str_eval += f"['{site_list[idx]}']"
                    # Once proper path is created, update the the "hosts" key (last key in path) with host info
                    inv_str_eval += f".update({{'{dev['hostname']}' : {{'ansible_host': '{dev['ip']}'}}}})"
                    # Once string literal is built, use eval() to parse and run the expression
                    eval(inv_str_eval)
                    print(inventory)
        else:
            inventory["all"]["hosts"].update(
                {dev["hostname"]: {"ansible_host": dev["ip"]}}
            )

    print(yaml.dump(inventory))


if __name__ == "__main__":
    ansible_inventory()
