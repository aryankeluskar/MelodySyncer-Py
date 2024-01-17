import subprocess
import sys

# List of packages to install
packages = ["aiohttp", "spotipy", "pydantic"]

# Install packages using pip
for package in packages:
    subprocess.check_call(["pip", "install", package])

    print(sys.version)
