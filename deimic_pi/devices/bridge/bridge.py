import json
import os
from os.path import isfile
from pathlib import Path

import zmq

from deimic_pi.devices.bridge.handlers import BridgePoller
from deimic_pi.devices.bridge.settings import Settings
from deimic_pi.devices import Device, DeviceType


class Bridge(Device):
    DEVICE_TYPE = DeviceType.BRIDGE
    POLLER_CLS = BridgePoller

    deimic_requests_queue = []

    def __init__(self, settings: Settings):
        super().__init__(settings)

        self.deimic_stream = self.create_socket(zmq.STREAM)
        self.deimic_stream.bind(f'tcp://*:{self.settings.deimic_port}')

        self.inter_broadcaster = self.create_socket(zmq.PUB)
        self.inter_broadcaster.bind(f'tcp://*:{self.settings.inter_broadcaster_port}')

        self.inter_listener = self.create_socket(zmq.SUB)
        self.inter_listener.bind(f'tcp://*:{self.settings.inter_listener_port}')
        self.inter_listener.subscribe('')

        self.extern_listener = self.create_socket(zmq.ROUTER)
        self.extern_listener.bind(f'tcp://*:{self.settings.extern_req_port}')

        self.extern_broadcaster = self.create_socket(zmq.PUB)
        self.extern_broadcaster.bind(f'tcp://*:{self.settings.extern_bcst_port}')
