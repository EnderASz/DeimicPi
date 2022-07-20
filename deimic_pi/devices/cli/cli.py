import zmq

from deimic_pi.devices.cli.handlers import CLIPoller
from deimic_pi.devices.cli.settings import Settings
from deimic_pi.devices import Device, DeviceType


class CLITool(Device):
    DEVICE_TYPE = DeviceType.CLI_TOOL
    POLLER_CLS = CLIPoller

    def __init__(
        self,
        settings: Settings
    ):
        super().__init__(settings)

        self.monitor_socket = self.create_socket(zmq.SUB)
        # TODO: Implement monitor filters
        self.monitor_socket.connect(
            self.settings.bridge_addr_form.format(
                port=self.settings.extern_bcst_port
            )
        )

        self.request_socket = self.create_socket(zmq.REQ)
        self.request_socket.connect(
            self.settings.bridge_addr_form.format(
                port=self.settings.extern_req_port
            )
        )
