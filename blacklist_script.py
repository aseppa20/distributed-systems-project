#!/usr/bin/env python3
"""
Simple Wazuh active response script to block an agent IP on a file server.
"""

import sys
import json
import datetime
import paramiko

# Fill in cache/file server info
CACHE_HOST = "192.168.0.19"  # Replace with file server IP
CACHE_USER = "user"       # Replace with SSH user on file server
LOG_FILE = "/var/ossec/logs/active-responses.log"

def write_debug_file(ar_name, msg):
    '''Write debug messages to a log file with timestamp and AR name.'''
    with open(LOG_FILE, mode="a") as log_file:
        log_file.write(str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')) + " " +  ar_name + ": " + msg +"\n")

def block_ip(agent_ip, cache_host, cache_user):
    """SSH into cache/file server and block the agent IP using iptables, 
    add the ip to a blacklist file, and log the action."""
    write_debug_file("we are in the block_ip function", "Blocking IP: " + agent_ip)
    try:
        connection = paramiko.SSHClient()
        connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Using password here for simplicity; should be replaced with key
        connection.connect(cache_host, 22, cache_user, "password")

        write_debug_file("SSH CONNECTION", str(connection.__getstate__))

        #TODO: will test that this works later, starting testing with adding to blacklist file
        cmd_block = f"sudo iptables -I INPUT -s {agent_ip} -p tcp,udp -m tcp,udp --dport 22 -m comment --comment 'Wazuh blocked {agent_ip} from using SSH to login' -j DROP"
        #connection.exec_command(cmd_block)
        connection.exec_command(f"echo '{agent_ip}' >> /home/wazuh/blacklist")

        # Log action locally
        write_debug_file("MAIN ACTION", f"IP {agent_ip} blocked on: {cache_host}")

        connection.close()
    except Exception as e:
        write_debug_file("ERROR", f"Error blocking {agent_ip}: {e}")

def main(argv):
    ''''Main function to read alert from stdin, parse JSON, and block IP if command is "add".'''
    write_debug_file(argv[0], "Started")
    # get alert from stdin
    input_str = ""
    for line in sys.stdin:
        input_str = line
        break

    write_debug_file(argv[0], input_str)
    write_debug_file(argv[0], "Json input received")

    try:
        data = json.loads(input_str)
    except ValueError:
        write_debug_file(argv[0], 'Decoding JSON has failed, invalid input format')
        sys.exit(1)

    action = data.get("command")
    write_debug_file(argv[0], "Command received: " + action)

    if action == "add":
        write_debug_file(argv[0], "We are in the add block")
        alert = data.get("parameters", {}).get("alert", {})
        write_debug_file(argv[0], "Alert: "+ str(alert))
        keys = [alert["rule"]["id"]]
        write_debug_file(argv[0], 'DONE: ' + str(keys))
        ip=data.get("parameters", {}).get("alert", {}).get("agent", {}).get("ip", "")
        if not ip:
            write_debug_file(argv[0], "No source IP found in alert data")
        else:
            write_debug_file(argv[0], "IP: " + ip)
            block_ip(ip, CACHE_HOST, CACHE_USER)

# Main script
if __name__ == "__main__":
    main(sys.argv)
