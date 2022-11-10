""" Commands to generate testbeds and other inventory files sourcing from DNAC inventory """

import json
import click
from dnac_sidekick.helpers.topology import (
    get_assigned_devices,
    get_site_hierarchy,
    get_site_name_by_id,
)
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
    """Generate pyATS testbed of all devices in DNAC inventory and assign global credentails pulled from DNAC."""
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

    device_list = ctx.invoke(devices, output="none")
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
        current_dir = os.path.dirname(os.path.realpath(__file__))
        env = Environment(loader=FileSystemLoader(f"{current_dir}/j2_templates"))
        tb_template = env.get_template("pyats_testbed.j2")
        generated_tb = tb_template.render(**table_data)
        with open("testbed.yaml", "w") as outfile:
            outfile.write(generated_tb)
            print(
                f"[bold bright_yellow]pyATS testbed file saved at {os.path.dirname(os.getcwd())}/testbed.yaml[/bold bright_yellow]"
            )


@click.command()
@click.option(
    "--output",
    type=click.Choice(["yaml"], case_sensitive=False),
    default="yaml",
    show_default=True,
    help="Specify an output format",
)
def ansible_inventory(output):
    """
    Generate Ansible inventory of all devices in DNAC inventory.

    Note: Currently limited to a nested depth of 2. If site hierarchy is deeper than 2 sites/buildings, then nested devices (nested depth > 2) will be rolled up to a higher-level site. For example, if a site hierarchy looks like this: Site1 -> Building1 -> Floor1, then any device assigned to Floor1 will be grouped under Building1. Floor1 will not be included in the inventory file. This is to reduce nested complexity in the resulting Ansible inventory file.
    """
    site_topo = get_site_hierarchy()
    devices = get_assigned_devices()
    inventory = {"all": {"children": {}, "hosts": {}}}
    # Create site hierarchy, then add devices
    # Create top-level sites in hierarchy
    for key, dets in site_topo.items():
        if dets["groupNameHierarchy"].count("/") == 1:
            # Confirms that parentId is 'Global' and is a top-level "area" in DNAC
            inventory["all"]["children"].update(
                {dets["name"]: {"children": {}, "hosts": {}}}
            )

    # Add sites that are belong to a parent site
    for key, dets in site_topo.items():
        if dets.get("parentId") is not None:
            par_id = dets.get("parentId")
            par_name = get_site_name_by_id(site_topo, par_id)
            if par_name != "all":
                if inventory["all"]["children"].get(par_name) is not None:
                    # Assumes parent is already in the inventory
                    child_loc = inventory["all"]["children"].get(par_name)
                    child_loc["children"].update({dets["name"]: {"hosts": {}}})
                else:
                    # Assumes parent is not in inventory
                    par_name = get_site_name_by_id(site_topo, par_id)
        else:
            print(f"{dets['name']} has no parent site.")
    # Add devices to site hierarchy
    # Use 'groupNameHierarchy' to figure out where the device belongs. Only use first two locations under Global
    for dev in devices.values():
        # Don't waste time on 'unassigned' devices in DNAC
        if dev["siteId"] != "unassigned":
            for site_id, dets in site_topo.items():
                if dev["siteId"] == site_id:
                    # Get site hierarchy assigned to device from site list (ex. Global/SanJose/Building1/Floor1)
                    site_loc = dets["groupNameHierarchy"]
                    hier = site_loc.split("/")
                    if len(hier) < 3:
                        new_hier = (
                            "/children/".join(hier[1])
                            .lower()
                            .replace(" ", "_")
                            .replace("-", "_")
                        )
                    else:
                        new_hier = (
                            "/children/".join(hier[1:3])
                            .lower()
                            .replace(" ", "_")
                            .replace("-", "_")
                        )
                    # Create list of the dict path (ex. ["all", "children", "site1"] => dict["all"]["children"]["site1"])
                    site_list = new_hier.split("/")
                    # Prepend 'all' and 'children', as they are top-level keys in Ansible inventory
                    site_list.insert(0, "all")
                    site_list.insert(1, "children")
                    # Add hosts to end of list, as that's the key where the hostnames/IPs will be added
                    site_list.append("hosts")
                    # Creates a string that will have the proper syntax to find the proper "hosts" key
                    # For ex: inventory["all"]["children"]["san_jose"]["children"]["sjc_20"]["hosts"]
                    inv_str_eval = "inventory"
                    for idx, site in enumerate(site_list):
                        if site != site_list:
                            inv_str_eval += f"['{site_list[idx]}']"
                    # Once proper path is created, update the the "hosts" key (last key in path) with host info
                    inv_str_eval += f".update({{'{dev['hostname']}' : {{'ansible_host': '{dev['ip']}'}}}})"
                    # Once string literal is built, use eval() to parse and run the expression
                    eval(inv_str_eval)
                    # Ex. inventory["all"]["children"]["san_jose"]["children"]["sjc_20"]["hosts"].update({"leaf2.abc.inc" : {"ansible_host": "10.10.20.82"}})
        else:
            inventory["all"]["hosts"].update(
                {dev["hostname"]: {"ansible_host": dev["ip"]}}
            )
    if output == "yaml":
        print(yaml.dump(inventory))
        with open("inventory.yaml", "w") as outfile:
            outfile.write(yaml.dump(inventory))
            print(
                f"[bold bright_yellow]Ansible inventory file saved at {os.path.dirname(os.getcwd())}/inventory.yaml[/bold bright_yellow]"
            )
