# tailzone

Create a BIND Zone from the devices in a Tailscale account

## Usage

1. Install the required dependencies by running the following command:
    ```bash
    pip install -r requirements.txt
    ```

2. You will need to set the following environment variables:
    - `TS_KEY`: Tailscale API key
    - `TAILNET`: Tailscale tailnet ID
    - `DOMAIN_NAME`: Domain name for the zone file

2. Run the `tailzone.py` script with the desired options. For example:
    ```bash
    python tailzone.py
    ```
3. The script will generate a BIND Zone file based on the devices in your Tailscale account and save it to `db.DOMAIN_NAME`.

4. You can then use the generated BIND Zone file in your DNS server configuration to resolve the devices in your Tailscale network.
