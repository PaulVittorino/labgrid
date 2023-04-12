# Labgrid driver for Segger J-Link
#
# Copyright 2023 by Garmin Ltd. or its subsidiaries.

import attr
import subprocess

from labgrid.factory import target_factory
from labgrid.driver.common import Driver
import labgrid.util.helper


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
            self.tool = "/opt/SEGGER/JLink/JLinkRemoteServer"

    def on_activate(self):
        self.port = labgrid.util.helper.get_free_port()
        cmd = [self.tool, "-Port", f"{self.port}", "-select", f"USB={self.jlink.serial}"]
        print(cmd)
        self._server_process = subprocess.Popen(cmd)
        return super().on_activate()

    def on_deactivate(self):
        self._server_process.kill()
        return super().on_deactivate()
