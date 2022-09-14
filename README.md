# dnac-sidekick
DNAC Sidekick is a CLI app used to interact with Cisco DNA Center. It's built using the [Click](https://github.com/pallets/click) and [Rich](https://github.com/Textualize/rich) libraries. The Rich library is what helps make the output look cleaner to the end-user. 

The goal of the tool is to provide a clean and user-friendly CLI interface. All interactions with DNAC use the available DNAC API, so please make sure that is enabled and the user account(s) used have proper permissions.

## Installation
Install using `pip` or any other PyPi package manager:
```
python -m pip install dnac-sidekick
```

## Getting Started

Users can either store their DNAC login credentials as environment variables or use CLI `login` argument authenticate to their DNAC instance.

### CLI Login
```
dnac-sidekick login --dnac_url <url> --username <user> --password <password>
```
Once completed, these values will be stored as local environment variables to use with future API requests.

### Environment Variables

If using local environment variables to configure DNAC credentials, please use the following names:
```
DNAC_URL=<https://dnac_url>
DNAC_USER=<username>
DNAC_PASS=<password>
```

*IMPORTANT:* Once the local environment variables are set, make sure to generate a token using the `dnac-sidekick login` command. Unlike the previous CLI Login example, the DNAC URL, username, and password will automatically be pulled from the environment variables, so there's no need to set additional flags.

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
