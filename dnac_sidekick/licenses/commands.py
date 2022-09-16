""" Commands to run CLI commands on network devices in DNAC inventory and view the output. """

import click
from rich.table import Table
from rich.console import Console
import requests


@click.command
@click.option(
    "--device", default="", help="Specify a device's hostname to get licensing."
)
@click.pass_context
def licenses(ctx, device):
    """Get license info for devices in DNAC inventory."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Auth-Token": ctx.obj.token,
    }
    if not ctx.obj.dnac_url:
        raise click.ClickException(
            "DNAC URL has not been provided or has not been set as an environment variable."
        )
    # different workflow if a device hostname is specified
    if device:
        dnac_devices_url = (
            f"{ctx.obj.dnac_url}/dna/intent/api/v1/network-device?hostname={device}"
        )
        net_devices_resp = requests.get(
            url=dnac_devices_url, headers=headers, verify=False
        )
        if net_devices_resp.status_code == 200:
            dev_id = net_devices_resp.json()["response"][0].get("id")
            # raise exception if device ID is not found
            if not dev_id:
                raise click.ClickException("Device hostname not found in inventory.")
        # could handle more error codes (i.e. 400, 401, etc) instead of using else
        else:
            raise click.ClickException(
                f"Could not pull device ID. Status code: {net_devices_resp.status_code}. Error message: {net_devices_resp.text}"
            )
        dev_licensing_url = (
            f"{ctx.obj.dnac_url}/dna/intent/api/v1/licenses/device/{dev_id}/details"
        )
        dev_licensing_resp = requests.get(
            url=dev_licensing_url, headers=headers, verify=False
        )
        if dev_licensing_resp.status_code == 200:
            device_lic_details = dev_licensing_resp.json()
            table = Table(title="DNAC Network Device Licensing")
            table.add_column(
                "Network License Level", justify="left", style="turquoise2"
            )
            table.add_column("DNA License Level", justify="left", style="purple")
            table.add_column("License Validity", justify="center", style="cyan")
            table.add_column("Virtual Account", justify="center", style="green")
            table.add_column("Device UDI", justify="center", style="red")

            if device_lic_details.get("is_license_expired") == False:
                lic_validity = "[bold green3]Valid[bold green3]"
            else:
                lic_validity = "[bold red]Expired[/bold red]"

            table.add_row(
                device_lic_details.get("network_license", "N/A"),
                device_lic_details.get("dna_level", "N/A"),
                lic_validity,
                device_lic_details.get("virtual_account_name", "N/A"),
                device_lic_details.get("udi", "N/A"),
            )

            console = Console()
            console.print(table)
        elif dev_licensing_resp.status_code == 401:
            click.echo("Unauthorized. Please verify your token is valid.")
            click.echo(dev_licensing_resp.text)
        else:
            click.echo("Could not retrieve license status of network device from DNAC.")
    else:
        dnac_devices_url = f"{ctx.obj.dnac_url}/dna/intent/api/v1/network-device"
        net_devices_resp = requests.get(
            url=dnac_devices_url, headers=headers, verify=False
        )
        if net_devices_resp.status_code == 200:
            net_devs = net_devices_resp.json()["response"]
            dev_ids = []
            for dev in net_devs:
                dev_ids.append(dev.get("id"))
            # raise exception if device ID list is empty
            if not dev_ids:
                raise click.ClickException("Device IDs could not be found.")
        elif dev_licensing_resp.status_code == 401:
            click.echo("Unauthorized. Please verify your token is valid.")
            click.echo(dev_licensing_resp.text)
        else:
            click.echo(
                "Could not retrieve license status of network device(s) from DNAC."
            )
        # initialize table to pretty print data
        table = Table(title="DNAC Network Device Licensing")
        table.add_column("Network License Level", justify="left", style="blue")
        table.add_column("DNA License Level", justify="left", style="purple")
        table.add_column("License Validity", justify="center", style="cyan")
        table.add_column("Virtual Account", justify="center", style="green")
        table.add_column("Device UDI", justify="center", style="red")
        # Pull license data for each device found in inventory
        for net_id in dev_ids:
            dev_licensing_url = (
                f"{ctx.obj.dnac_url}/dna/intent/api/v1/licenses/device/{net_id}/details"
            )
            dev_licensing_resp = requests.get(
                url=dev_licensing_url, headers=headers, verify=False
            )
            if dev_licensing_resp.status_code == 200:
                device_lic_details = dev_licensing_resp.json()

                if device_lic_details.get("is_license_expired") == False:
                    lic_validity = "[bold green3]Valid[bold green3]"
                else:
                    lic_validity = "[bold red]Expired[/bold red]"

                table.add_row(
                    device_lic_details.get("network_license", "N/A"),
                    device_lic_details.get("dna_level", "N/A"),
                    lic_validity,
                    device_lic_details.get("virtual_account_name", "N/A"),
                    device_lic_details.get("udi", "N/A"),
                )
            elif dev_licensing_resp.status_code == 401:
                click.echo("Unauthorized. Please verify your token is valid.")
                click.echo(dev_licensing_resp.text)
            else:
                click.echo(
                    "Could not retrieve license status of network device(s) from DNAC."
                )

        console = Console()
        console.print(table)
