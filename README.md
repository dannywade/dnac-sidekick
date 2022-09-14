[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/dannywade/dnac-sidekick/branch/main/graph/badge.svg?token=IWBEDN1YXH)](https://codecov.io/gh/dannywade/dnac-sidekick)

# dnac-sidekick
DNAC Sidekick is a CLI app used to interact with Cisco DNA Center. It's built using the [Click](https://github.com/pallets/click) and [Rich](https://github.com/Textualize/rich) libraries. The Rich library is what helps make the output look cleaner to the end-user. 

The goal of the tool is to provide a clean and user-friendly CLI interface. All interactions with DNAC use the available DNAC API, so please make sure that is enabled and the user account(s) used have proper permissions.

## Installation
Install using `pip` or any other PyPi package manager:
```
python -m pip install dnac-sidekick
```

## Getting Started

### Authenticating to DNAC
Users can either store their DNAC login credentials (username/password) as environment variables or use the CLI ` dnac-sidekick login` argument authenticate to their DNAC instance.

### CLI Login
```
dnac-sidekick login --dnac_url <url> --username <user> --password <password>
```
Once completed, these values will be used to generate a bearer token and store all values as local environment variables to use with future API requests.

### Environment Variables

Alternatively, you can set the environment variables yourself. If setting them manually, please use the following names:
```
DNAC_URL=<https://dnac_url>
DNAC_USER=<username>
DNAC_PASS=<password>
```

*IMPORTANT:* If setting the environment variables manually, please make sure to generate the bearer token using the `dnac-sidekick login` command. Since the environment variables are set, there's no need to set additional flags.

## Usage
If you are ever stuck with what commands are available, please use `--help`. Here's a brief look at what root commands/options available:
```
Options:
  --help  Show this message and exit.

Commands:
  command-runner  Retrieve all devices from DNAC inventory
  get             Action for read-only tasks and gathering information.
  login           Use username and password to authenticate to DNAC.
```

## Compatibility
Tested with:
- DNA Center 2.2.3.4

*Could definitely use help validating against other versions.*
