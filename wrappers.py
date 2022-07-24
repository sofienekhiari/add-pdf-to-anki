"""Wrappers needed for the app"""

import os

# Wrapper to catch errors in case commands not installed
def run_command(command):
    """Run command if it's installed"""
    command_exit_code = os.system(command)
    if command_exit_code !=0:
        raise Exception(f"There was an error while running the following command: {command}")
