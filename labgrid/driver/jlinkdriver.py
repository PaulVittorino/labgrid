# Labgrid driver for Segger J-Link
#
# Copyright 2023 by Garmin Ltd. or its subsidiaries.

import attr
import socket
import subprocess
import time

from .common import Driver
from ..driver.exception import ExecutionError
from ..factory import target_factory
from ..step import step
from ..util.helper import get_free_port
from ..util.proxy import proxymanager
from ..util import Timeout


@target_factory.reg_driver
@attr.s(eq=False)
class JLinkDriver(Driver):
    """A JLinkDriver is a remotely accessable J-Link Device via the J-Link Remote Server

    https://wiki.segger.com/J-Link_Remote_Server
    """

    bindings = {
        "jlink": {"JLinkDevice", "NetworkJLinkDevice"},
    }

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        if self.target.env:
            self.tool = self.target.env.config.get_tool("JLinkRemoteServer") or "JLinkRemoteServer"
        else:
            # Use the most recetly installed version
            # https://wiki.segger.com/Generic_IDE#Linux
            self.tool = "/opt/SEGGER/JLink/JLinkRemoteServer"

    def on_activate(self):
        """Using the bound JLinkDevice, start the J-Link Remote Server on a free port
        """
        self.remote_port = get_free_port()
        cmd = [self.tool, "-Port", f"{self.remote_port}", "-select", f"USB={self.jlink.serial}"]
        print(cmd)
        self._server_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)

        self.host, self.port = proxymanager.get_host_and_port(self.jlink, default_port=self.remote_port)

        #TODO wait for "Waiting for client connections... " to appear before returning. Otherwise the server is not ready to accept incoming connections.
        time.sleep(1)
        # try:
        #     print("Trying to connect to J-Link Server")
        #     s = socket.create_connection((self.host, self.port), timeout=10.0)
        #     print("Connected")
        #     s.close()
        # except socket.timeout:
        #     raise ExecutionError("Timeout while waiting for J-Link Remote Server to start")

        return super().on_activate()

    def on_deactivate(self):
        self._server_process.kill()
        return super().on_deactivate()

    @Driver.check_active
    @step()
    def get_ip_addr(self):
        """Retun the IP address and port of the J-Link Remote Server
        Suitable for passing to the pylink library.
        """
        # The J-Link software does not support host names ¯\_(ツ)_/¯
        ip_addr = socket.gethostbyname(self.jlink.host)
        # Workaround for Debian's /etc/hosts entry
        if ip_addr == "127.0.1.1":
            ip_addr = "127.0.0.1"
        return f"{ip_addr}:{self.port}"
