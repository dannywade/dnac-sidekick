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
from rich.console import Console
from rich.table import Table
import os
from dotenv import load_dotenv

load_dotenv()
requests.packages.urllib3.disable_warnings()

class DnacUser(object):
    def __init__(self, dnac_url=None, username=None, password=None, token=None):
        self.dnac_url = dnac_url
        self.username = username
        self.password = password
        self.token = token

@click.group()
@click.pass_context
def dnac_cli(ctx):
    pass

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

@dnac_cli.command()
@click.option("--dnac_url", default="", show_default=True, envvar="DNAC_URL", help="IP/hostname to the DNA Center appliance")
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
        click.echo(f"GENERATED TOKEN: {actual_token}")
        os.environ["DNAC_TOKEN"] = actual_token
        click.echo("TOKEN SUCCESSFULLY STORED AS ENVIRONMENT VARIABLE!")
        ctx.obj = DnacUser(dnac_url=dnac_url,username=username,password=password,token=actual_token)
    else:
        click.echo("Token not generated. Please try again...")

if __name__ == "__main__":
    dnac_cli()