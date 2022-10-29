"""Module for helper fuctions to pull topology and site information from DNA Center"""
import click
import os
import requests


def get_site_hierarchy() -> dict:
    """
    Get site topology information from DNA Center.

    Example output:
    {
        "27eb9050-63bf-4832-92a0-95796391a92b": {
            "name": "san_jose",
            "parentId": "b73390ce-b713-49c1-899b-1605853c321d",
            "groupNameHierarchy": "Global/San Jose"
        },
        "c323fba3-b7f4-462a-9867-f2eb865ece19": {
            "name": "sjc_20",
            "parentId": "27eb9050-63bf-4832-92a0-95796391a92b",
            "groupNameHierarchy": "Global/San Jose/SJC-20"
        }
    }
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Auth-Token": os.environ.get("DNAC_TOKEN"),
    }
    # Get available CLI device credentials stored in DNAC
    dnac_sites = (
        f"{os.environ.get('DNAC_URL')}/dna/intent/api/v1/topology/site-topology"
    )
    response = requests.get(url=dnac_sites, headers=headers, verify=False)
    # Site structure dict will hold important values that are needed to build site hierarchy for Ansible inventory
    # Site IDs will be used as keys for each site in the output. This will ensure each site captured is unique.
    site_structure = {}
    if response.status_code == 200:
        for site in response.json()["response"]["sites"]:
            site_key = {site["id"]: {}}
            site_structure.update(site_key)
            site_structure[site["id"]].update(
                {"name": site["name"].replace(" ", "_").replace("-", "_").lower()}
            )
            site_structure[site["id"]].update({"parentId": site["parentId"]})
            site_structure[site["id"]].update(
                {"groupNameHierarchy": site["groupNameHierarchy"]}
            )
    else:
        click.echo(f"HTTP Status Code: {response.status_code}")
        click.echo("Unauthorized. Please verify your token is valid.")
    print(site_structure)
    return site_structure


def get_assigned_devices() -> dict:
    """
    Get list of devices and the site IDs they are assigned to in DNA Center.

    Example output:
    {
        "6b741b27-f7e7-4470-b6fc-d5168cc59502": {
            "hostname": "c3504.abc.inc",
            "ip": "10.10.20.51",
            "siteId": "unassigned"
        },
        "aa0a5258-3e6f-422f-9c4e-9c196db115ae": {
            "hostname": "leaf1.abc.inc",
            "ip": "10.10.20.81",
            "siteId": "c323fba3-b7f4-462a-9867-f2eb865ece19"
        },
        "f0cb8464-1ce7-4afe-9c0d-a4b0cc5ee84c": {
            "hostname": "leaf2.abc.inc",
            "ip": "10.10.20.82",
            "siteId": "unassigned"
        },
        "f16955ae-c349-47e9-8e8f-9b62104ab604": {
            "hostname": "spine1.abc.inc",
            "ip": "10.10.20.80",
            "siteId": "unassigned"
        }
    }
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Auth-Token": os.environ.get("DNAC_TOKEN"),
    }
    # Get available CLI device credentials stored in DNAC
    dnac_sites = f"{os.environ.get('DNAC_URL')}/dna/intent/api/v1/topology/physical-topology?nodeType=device"
    response = requests.get(url=dnac_sites, headers=headers, verify=False)
    # Site structure dict will hold important values that are needed to build site hierarchy for Ansible inventory
    # Device IDs will be used as keys for each device in the output. This will ensure each device captured is unique.
    node_structure = {}
    if response.status_code == 200:
        for node in response.json()["response"]["nodes"]:
            node_key = {node["id"]: {}}
            node_structure.update(node_key)
            node_structure[node["id"]].update({"hostname": node["label"]})
            node_structure[node["id"]].update({"ip": node["ip"]})
            if node["additionalInfo"].get("siteid") is not None:
                node_structure[node["id"]].update(
                    {"siteId": node["additionalInfo"]["siteid"]}
                )
            else:
                node_structure[node["id"]].update({"siteId": "unassigned"})
    else:
        click.echo(f"HTTP Status Code: {response.status_code}")
        click.echo("Unauthorized. Please verify your token is valid.")

    return node_structure


def iterate_all(iterable, returned="key"):

    """Returns an iterator that returns all keys or values
    of a (nested) iterable.

    Arguments:
        - iterable: <list> or <dictionary>
        - returned: <string> "key" or "value"

    Returns:
        - <iterator>
    """

    if isinstance(iterable, dict):
        for key, value in iterable.items():
            if returned == "key":
                yield key
            elif returned == "value":
                if not (isinstance(value, dict) or isinstance(value, list)):
                    yield value
            else:
                raise ValueError("'returned' keyword only accepts 'key' or 'value'.")
            for ret in iterate_all(value, returned=returned):
                yield ret
    elif isinstance(iterable, list):
        for el in iterable:
            for ret in iterate_all(el, returned=returned):
                yield ret
