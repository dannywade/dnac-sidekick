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


def test_env_vars_set():
    dnac_url = os.environ.get("DNAC_URL")
    dnac_user = os.environ.get("DNAC_USER")
    dnac_pass = os.environ.get("DNAC_PASS")
    dnac_token = os.environ.get("DNAC_TOKEN")

    assert None not in (dnac_url, dnac_user, dnac_pass, dnac_token)


def test_dnac_login():
    requests.packages.urllib3.disable_warnings()
    runner = CliRunner()
    result = runner.invoke(
        dnac_cli,
        [
            "login",
        ],
    )
    assert result.exit_code == 0


def test_dnac_get_devices_table_output():
    requests.packages.urllib3.disable_warnings()
    runner = CliRunner()
    result = runner.invoke(dnac_cli, ["get", "inventory", "devices"])
    assert result.exit_code == 0


def test_dnac_get_devices_json_output():
    requests.packages.urllib3.disable_warnings()
    runner = CliRunner()
    result = runner.invoke(
        dnac_cli, ["get", "inventory", "devices", "--output", "json"]
    )
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
        ["command-runner", "--device", "spine1.abc.inc", "--command", "show run"],
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


def test_dnac_generate_pyats_testbed():
    requests.packages.urllib3.disable_warnings()
    runner = CliRunner()
    result = runner.invoke(dnac_cli, ["generate", "pyats-testbed"], input="y\n")
    assert result.exit_code == 0
