from threading import Thread, Event

import zmq
from zmq import Frame

from deimic_pi.devices.led_driver.messages import LedDriverPoller
from deimic_pi.devices.led_driver.settings import Settings
from deimic_pi.devices import Device, DeviceType


class LedDriver(Device):
    DEVICE_TYPE = DeviceType.LED_DRIVER
    POLLER_CLS = LedDriverPoller

    def __init__(self, settings: Settings):
        super().__init__(settings)

        self.requests_socket = self.ctx.socket(zmq.SUB)
        self.requests_socket.connect(
            self.settings.bridge_addr_form.format(
                port=self.settings.inter_broadcaster_port
            )
        )
        for signature in self.DEVICE_TYPE.get_familiar_signatures():
            self.requests_socket.subscribe(str(signature))

        self.broadcaster = self.ctx.socket(zmq.PUB)
        self.broadcaster.connect(
            self.settings.bridge_addr_form.format(
                port=self.settings.inter_listener_port
            )
        )

        self.led_executor: Thread | None = None
        self.executor_stop_controller: Event = Event()
        self.executor_run_controller: Event = Event()
