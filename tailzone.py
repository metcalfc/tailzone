#!/usr/bin/env python3

# tailzone.py
# This script retrieves the list of devices from Tailscale API and creates a BIND style zone file.
# You will need to set the following environment variables:
# - TS_KEY: Tailscale API key
# - TAILNET: Tailscale tailnet ID
# - DOMAIN_NAME: Domain name for the zone file

import requests
import datetime
import os
import sys
import pprint
import json

def get_devices(api_key, tailnet):
    response = requests.get(f'https://api.tailscale.com/api/v2/tailnet/{tailnet}/devices', headers={'Authorization': f'Bearer {api_key}'})
    if response.status_code != 200:
        raise Exception('Failed to retrieve the list of devices.')
    return response.json()['devices']

def write_zone_file(devices, file_path, domain_name):
    with open(file_path, 'w') as file:
        now = datetime.datetime.now()
        serial = now.strftime("%Y%m%d")
        file.write('$TTL 86400\n')
        file.write('@ IN SOA ns1.{0}. admin.{0}. (\n'.format(domain_name))
        file.write(f'    {serial}01 ; Serial\n')
        file.write( '    3600       ; Refresh\n')
        file.write( '    1800       ; Retry\n')
        file.write( '    604800     ; Expire\n')
        file.write( '    86400      ; Minimum TTL\n')
        file.write(')\n')
        file.write('\n')
        file.write('@ IN NS ns1.{0}.\n'.format(domain_name))
        file.write('\n')
        for device in devices:
            device_name = device['hostname']
            ip_address = device['addresses'][0]
            file.write(f'{device_name}.{domain_name}. 3600 A {ip_address}\n')

def main():
    api_key = os.environ.get('TS_KEY')
    if not api_key:
        print('TS_KEY environment variable is not set.')
        sys.exit(1)

    tailnet = os.environ.get('TAILNET')
    if not tailnet:
        print('TAILNET environment variable is not set.')
        sys.exit(1)

    domain_name = os.environ.get('DOMAIN_NAME')
    if not domain_name:
        print('DOMAIN_NAME environment variable is not set.')
        sys.exit(1)

    try:
        devices = get_devices(api_key, tailnet)
        write_zone_file(devices, './db.{0}'.format(domain_name), domain_name)
        print('BIND style zone db file created successfully.')
    except Exception as e:
        print(str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()
