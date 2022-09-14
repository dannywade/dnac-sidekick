import pytest
import requests
from requests.auth import HTTPBasicAuth


@pytest.fixture
def devnet_sbx_dnac():
    requests.packages.urllib3.disable_warnings()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    dnac_token_url = "https://sandboxdnac.cisco.com/dna/system/api/v1/auth/token"
    token = requests.post(
        url=dnac_token_url,
        headers=headers,
        auth=HTTPBasicAuth(username="devnetuser", password="Cisco123!"),
        verify=False,
    )
    if token.status_code == 200:
        actual_token = token.json()["Token"]
        print("Token generated successfully!")
        return actual_token
    else:
        print("Token not generated. Please try again...")
