import platform
import plistlib
import subprocess
from pathlib import Path
from rich import print

from .base_info import BaseInfo


class HostInfo(BaseInfo):
    """
    Print host info
    """
    def __init__(self):
        super().__init__()

    def query_host(self) -> dict:
        """
        Get information about current host.
        """
        host = {'hostname': platform.node()}
        if self.OS == 'darwin':
            # get model identifier from sysctl
            model = subprocess.check_output(["/usr/sbin/sysctl", "-n", "hw.model"]).strip().decode('utf-8')
            plist_file_path = Path("/System/Library/PrivateFrameworks/ServerInformation.framework/Versions/A/Resources/"
                                   "en.lproj/SIMachineAttributes.plist")
            # in older versions of MacOS: en.lproj -> English.lproj
            if not plist_file_path.is_file():
                plist_file_path = Path("/System/Library/PrivateFrameworks/ServerInformation.framework/Versions/A/"
                                       "Resources/English.lproj/SIMachineAttributes.plist")

            # read property list file
            with open(plist_file_path, 'rb') as fp:
                plist = plistlib.load(fp)

            # check, whether the model obtained from sysctl is in the property list file
            if model in plist:
                host['model marketing name'] = plist[model]["_LOCALIZABLE_"]["marketingModel"]
            else:
                host['model marketing name'] = model

        return host

    def print_host_info(self, host):
        """
        Print users hostname. Additionally, on MacOS, try to print the model marketing name.
        """
        print(f'[bold blue]Hostname: {host["hostname"]}')
        if 'model marketing name' in host.keys():
            print(f'[bold blue]Model name: {host["model marketing name"]}')
