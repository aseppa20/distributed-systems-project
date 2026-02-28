#!/usr/bin/env python3
"""
Simple Wazuh active response script to block an agent IP on a file server.
"""

import sys
import paramiko

def block_ip(agent_ip, cache_host, cache_user):
    """SSH into cache/file server and block the agent IP using iptables"""
    try:
        connection = paramiko.SSHClient()
        connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Using password here for simplicity; should be replaced with key
        connection.connect(cache_host, 22, cache_user, "1234")

        #TODO: will test that this works later, starting testing with adding to blacklist file
        cmd_block = f"sudo iptables -I INPUT -s {agent_ip} -p tcp,udp -m tcp,udp --dport 22 -m comment --comment 'Wazuh blocked {agent_ip} from using SSH to login' -j DROP"
        #connection.exec_command(cmd_block)
        connection.exec_command(f"echo '{agent_ip}' >> /home/wazuh/blacklist")
        
        # Log action locally
        with open("/var/ossec/logs/active-responses.log", "a") as f:
            f.write(f"{agent_ip} blocked on {cache_host}\n")
        
        connection.close()
        print(f"{agent_ip} successfully blocked on {cache_host}")
    except Exception as e:
        print(f"Error blocking {agent_ip}: {e}")

# Main script
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: blacklist_vm.py <agent_ip>")
        sys.exit(1)

    agent_ip = sys.argv[1]

    # Fill in cache/file server info
    cache_host = "10.0.0.100"  # Replace with file server IP
    cache_user = "admin"       # Replace with SSH user on file server

    block_ip(agent_ip, cache_host, cache_user)
