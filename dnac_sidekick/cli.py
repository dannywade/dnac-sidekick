#!/usr/bin/env python

"""DNAC Sidekick
A simple CLI app built on the Click library to interact with Cisco DNA Center.
Here are the current features/functions of the tool:
    * Get device information for all of DNAC's inventory or just a specific device
      (via hostname)
    * Get device health statistics for all devices
    * Get client health statistics for all clients or just a specific client
      (via the client's MAC address)
    * Run arbitrary "show" commands against a specific device in DNAC's inventory
Use --help to check available commands and options.
Feel free to open a PR or fork the project to modify to your needs.
"""

import click
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

from dnac_sidekick.inventory import commands as inventory_cmds
from dnac_sidekick.health import commands as health_cmds
from dnac_sidekick.device_commands import commands as device_commands_cmds
from dnac_sidekick.licenses import commands as license_cmds

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
    """
    Extract sensitive info from environment variables that will be used to connect to DNA Center and add to Click Context.
    By adding to Click Context, these values can be used across all commands.
    """
    pass


@dnac_cli.command
def login():
    """Helper function to quickly generate bearer token and authenticate to DNAC."""
    # Pull env vars that should be set by user
    dnac_url = os.environ.get("DNAC_URL")
    username = os.environ.get("DNAC_USER")
    password = os.environ.get("DNAC_PASS")
    # Confirm set env var values are not None
    if None in (dnac_url, username, password):
        raise click.ClickException("A necessary environment variable has not been set.")
    # Since value is being read from env var, and not context, need to add extra logic
    if dnac_url[-1] == "/":
        dnac_url = dnac_url.rstrip(dnac_url[-1])
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    dnac_token_url = f"{dnac_url}/dna/system/api/v1/auth/token"
    click.echo("Attempting to login to DNAC...")
    token = requests.post(
        url=dnac_token_url,
        headers=headers,
        auth=HTTPBasicAuth(username=username, password=password),
        verify=False,
    )
    if token.status_code == 200:
        actual_token = token.json()["Token"]
        click.echo("Token generated successfully!")
        # Set new token as env var and update .env file
        click.echo(
            "Copy token below and set as environment variable for future requests:"
        )
        click.echo(actual_token)

    elif token.status_code == 401:
        click.echo(
            "Unauthorized. Token not generated. Please make sure a proper username and password are provided and correct."
        )
    else:
        click.echo("Token not generated. Please try again...")
        click.echo(f"Status code: {token.status_code}. Error message: {token.text}.")


@dnac_cli.group()
@click.pass_context
def get(ctx):
    """Action for read-only tasks and gathering information."""
    click.echo("Getting information...")

    # Confirm all the necessary env vars are set
    dnac_url = os.environ.get("DNAC_URL")
    dnac_user = os.environ.get("DNAC_USER")
    dnac_pass = os.environ.get("DNAC_PASS")
    dnac_token = os.environ.get("DNAC_TOKEN")
    # Add values to context for read-only actions to use
    if None not in (dnac_url, dnac_user, dnac_pass, dnac_token):
        ctx.obj = DnacUser(
            dnac_url=dnac_url,
            username=dnac_user,
            password=dnac_pass,
            token=dnac_token,
        )
    else:
        raise click.ClickException("A necessary environment variable has not been set.")


@get.group()
@click.pass_context
def inventory(ctx):
    """Gathers information related to device inventory in DNAC"""
    pass


@get.group()
@click.pass_context
def health(ctx):
    """Gathers health information for network devices and clients in DNAC"""
    pass


inventory.add_command(inventory_cmds.devices)
health.add_command(health_cmds.devices)
health.add_command(health_cmds.clients)
dnac_cli.add_command(device_commands_cmds.command_runner)
get.add_command(license_cmds.licenses)

if __name__ == "__main__":
    dnac_cli()
