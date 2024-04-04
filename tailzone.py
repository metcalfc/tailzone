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
import json
import logging
import argparse

def get_devices(api_key, tailnet):
    url = f'https://api.tailscale.com/api/v2/tailnet/{tailnet}/devices'
    headers = {'Authorization': f'Bearer {api_key}'}
    
    with requests.Session() as session:
        response = session.get(url, headers=headers)
        
        if response.status_code != 200:
            logging.error('Failed to retrieve the list of devices.')
            return None

        try:
            return response.json()['devices']
        except json.JSONDecodeError:
            logging.error('Failed to decode JSON from response.')
            return None

def write_zone_file(devices, file_path, domain_name):
    if devices is None:
        logging.error('No devices to write to zone file.')
        return

    if not all(isinstance(device, dict) for device in devices):
        logging.error('Devices should be a list of dictionaries.')
        return
    
    now = datetime.datetime.now()
    serial = now.strftime("%Y%m%d")
    zone_file_content = f"""
$TTL 86400
@ IN SOA ns1.{domain_name}. admin.{domain_name}. (
    {serial}01 ; Serial
    3600       ; Refresh
    1800       ; Retry
    604800     ; Expire
    86400      ; Minimum TTL
)

@ IN NS ns1.{domain_name}.
"""
    with open(file_path, 'w') as file:
        file.write(zone_file_content)
        for device in devices:
            device_name = device['hostname']
            ip_address = device['addresses'][0]
            file.write(f'{device_name}.{domain_name}. 3600 A {ip_address}\n')

def parse_arguments():
    parser = argparse.ArgumentParser(description='Retrieve devices from Tailscale API and create a BIND style zone file.')
    parser.add_argument('-k', '--key', help='Tailscale API key')
    parser.add_argument('-t', '--tailnet', help='Tailscale tailnet ID')
    parser.add_argument('-d', '--domain', help='Domain name for the zone file')
    return parser.parse_args()

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO)
    
    args = parse_arguments()
    api_key = args.key or os.environ.get('TS_KEY')
    if not api_key:
        logging.error('TS_KEY environment variable is not set.')
        sys.exit(1)
    
    tailnet = args.tailnet or os.environ.get('TAILNET')
    if not tailnet:
        logging.error('TAILNET environment variable is not set.')
        sys.exit(1)
    
    domain_name = args.domain or os.environ.get('DOMAIN_NAME')
    if not domain_name:
        logging.error('DOMAIN_NAME environment variable is not set.')
        sys.exit(1)
    
    logging.info('Retrieving devices from Tailscale API...')

    try:
        devices = get_devices(api_key, tailnet)
        write_zone_file(devices, './db.{0}'.format(domain_name), domain_name)
        logging.info('Zone file created successfully.')
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()