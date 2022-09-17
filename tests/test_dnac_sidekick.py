import requests
from click.testing import CliRunner
from dnac_sidekick.cli import dnac_cli
import os
import time

"""
Tests for DNAC Sidekick CLI tool. Must have the following environment variables set:
- DNAC_URL
- DNAC_TOKEN

All tests use the Always-On DNA Center Cisco DevNet sandbox (https://sandboxdnac.cisco.com).
If the DNAC URL or any login credentials change, the tests will need changed accordingly.
"""

os.environ["DNAC_URL"] = "https://sandboxdnac.cisco.com"


def test_dnac_login():
    requests.packages.urllib3.disable_warnings()
    runner = CliRunner()
    result = runner.invoke(
        dnac_cli,
        [
            "login",
            "--dnac_url",
            "https://sandboxdnac.cisco.com",
            "--username",
            "devnetuser",
            "--password",
            "Cisco123!",
        ],
    )
    assert result.exit_code == 0


def test_dnac_get_devices(devnet_sbx_dnac):
    requests.packages.urllib3.disable_warnings()
    os.environ["DNAC_TOKEN"] = devnet_sbx_dnac
    runner = CliRunner()
    result = runner.invoke(dnac_cli, ["get", "inventory", "devices"])
    assert result.exit_code == 0


def test_dnac_get_device_by_hostname():
    requests.packages.urllib3.disable_warnings()
    runner = CliRunner()
    result = runner.invoke(
        dnac_cli, ["get", "inventory", "devices", "--hostname", "leaf1.abc.inc"]
    )
    assert result.exit_code == 0


def test_dnac_get_device_health():
    requests.packages.urllib3.disable_warnings()
    runner = CliRunner()
    result = runner.invoke(dnac_cli, ["get", "health", "devices"])
    assert result.exit_code == 0


def test_dnac_get_client_health():
    requests.packages.urllib3.disable_warnings()
    runner = CliRunner()
    result = runner.invoke(dnac_cli, ["get", "health", "clients"])
    assert result.exit_code == 0


def test_dnac_command_runner():
    requests.packages.urllib3.disable_warnings()
    runner = CliRunner()
    result = runner.invoke(
        dnac_cli,
        ["command-runner", "--device", "spine1.abc.inc", "--command", "show version"],
    )
    time.sleep(3)
    assert result.exit_code == 0


def test_dnac_get_licenses():
    requests.packages.urllib3.disable_warnings()
    runner = CliRunner()
    result = runner.invoke(
        dnac_cli,
        ["get", "licenses"],
    )
    time.sleep(3)
    assert result.exit_code == 0


def test_dnac_get_device_licenses():
    requests.packages.urllib3.disable_warnings()
    runner = CliRunner()
    result = runner.invoke(
        dnac_cli,
        ["get", "licenses", "--device", "spine1.abc.inc"],
    )
    time.sleep(3)
    assert result.exit_code == 0
