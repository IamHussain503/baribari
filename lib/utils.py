from os import path
import re
import requests
import sys
import subprocess
import codecs
import wandb
import os
import git

def version2number(version):
    """Convert a version string into a comparable integer."""
    parts = version.split(".")
    return sum(int(part) * (100 ** (2 - index)) for index, part in enumerate(parts[:3]))

def get_remote_version():
    url = "https://raw.githubusercontent.com/IamHussain503/baribari/main/lib/__init__.py"
    response = requests.get(url)
    if response.status_code == 200:
        version_info = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", response.text, re.M)
        if version_info:
            return version_info.group(1)
    print("Failed to get file content")
    return None

def get_local_version():
    try:
        here = path.abspath(path.dirname(__file__))
        with codecs.open(path.join(here, "__init__.py"), encoding="utf-8") as init_file:
            version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", init_file.read(), re.M)
            if version_match:
                return version_match.group(1)
    except Exception as e:
        print(f"Error getting local version: {e}")
    return None

def check_version_updated():
    remote_version = get_remote_version()
    local_version = get_local_version()
    print(f"Version check - remote_version: {remote_version}, local_version: {local_version}")
    return version2number(remote_version) > version2number(local_version)

def update_repo():
    try:
        repo = git.Repo(search_parent_directories=True)
        origin = repo.remotes.origin
        origin.pull()
        print("Repository updated.")
        return True
    except Exception as e:
        print(f"Update failed: {e}")
    return False

def get_pm2_path():
    try:
        result = subprocess.run(["which", "pm2"], check=True, stdout=subprocess.PIPE, universal_newlines=True)
        pm2_path = result.stdout.strip()
        return pm2_path
    except subprocess.CalledProcessError:
        return None  # Return None if PM2 not found

def restart_app(pm2_path):
    if not pm2_path:
        print("PM2 not found. Make sure PM2 is installed and accessible.")
        return

    print("Restarting app due to the update...")
    try:
        subprocess.check_call([pm2_path, "stop", "miner"])
        print("App stopped successfully.")
        subprocess.check_call([pm2_path, "restart", "miner"])
        print("App restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart app with pm2: {e}")

def try_update():
    if check_version_updated():
        print("Found a newer version. Updating...")
        if update_repo():
            pm2_path = get_pm2_path()  # Get PM2 path after update (optional)
            restart_app(pm2_path)

