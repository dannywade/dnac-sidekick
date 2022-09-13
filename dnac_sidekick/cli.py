#!/usr/bin/env python

"""DNAC Sidekick
A simple CLI app built on the Click library to interact with Cisco DNA Center.
Currently, there's limited functionality, as this was built as part of a learning exercise.
Here are the current features/functions of the tool:
    * Get device information for all of DNAC's inventory or just a specific device
      (via hostname)
    * Get device health statistics for all devices
    * Get client health statistics for all clients or just a specific client
      (via the client's MAC address)
Use --help to check available commands and options.
Feel free to open a PR or fork the project to modify to your needs.
"""

import click
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv, set_key

from inventory import commands as inventory_cmds
from health import commands as health_cmds

dotenv_file = "../.env"
load_dotenv(dotenv_file)
requests.packages.urllib3.disable_warnings()

class DnacUser(object):
    def __init__(self, dnac_url=None, username=None, password=None, token=None):
        self.dnac_url = dnac_url
        self.dnac_user = username
        self.dnac_pass = password
        self.token = token

@click.group()
@click.pass_context
def dnac_cli(ctx):
    dnac_url = os.environ.get("DNAC_URL")
    username = os.environ.get("DNAC_USER")
    password = os.environ.get("DNAC_PASS")
    token = os.environ.get("DNAC_TOKEN")
    if (dnac_url, username, password, token):
        ctx.obj = DnacUser(dnac_url=dnac_url,username=username,password=password,token=token)
    else:
        click.echo("A necessary environment variable is not set.")

@dnac_cli.command
@click.option("--dnac_url", default="", envvar="DNAC_URL", help="IP/hostname to the DNA Center appliance")
@click.option("--username", default="", envvar="DNAC_USER", help="User for login account")
@click.option("--password", default="", envvar="DNAC_PASS", help="Password for login account")
@click.pass_context
def login(ctx, dnac_url, username, password):
    """ Use username and password to authenticate to DNAC. """
    click.echo("Attempting to login to DNAC...")
    if not dnac_url:
        raise ValueError("DNAC URL has not been provided and has not been set as an environment variable.")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    dnac_token_url = f"{dnac_url}/dna/system/api/v1/auth/token"
    token = requests.post(url=dnac_token_url, headers=headers, auth=HTTPBasicAuth(username=username, password=password), verify=False)
    if token.status_code == 200:
        actual_token = token.json()["Token"]
        click.echo("Token generated successfully!")
        # Set new token as env var and update .env file
        os.environ["DNAC_TOKEN"] = actual_token
        set_key(dotenv_file, "DNAC_TOKEN", os.environ["DNAC_TOKEN"])
    else:
        click.echo("Token not generated. Please try again...")

@dnac_cli.group()
@click.pass_context
def get(ctx):
    """ Action for read-only tasks and gathering information. """
    click.echo("Getting information...")
    pass

@get.group()
@click.pass_context
def inventory(ctx):
    """ Gathers information related to device inventory in DNAC """
    pass

@get.group()
@click.pass_context
def health(ctx):
    """ Gathers health information for network devices and clients in DNAC """
    pass

inventory.add_command(inventory_cmds.devices)
health.add_command(health_cmds.devices)
health.add_command(health_cmds.clients)

if __name__ == "__main__":
    dnac_cli()