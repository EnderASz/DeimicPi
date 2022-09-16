import abc
import enum
import typing as t

import zmq.asyncio as zmq_asyncio

from deimic_pi.messages import Poller
from deimic_pi.settings import Settings

if t.TYPE_CHECKING:
    from deimic_pi.devices.bridge.settings import Settings as BridgeSettings
    from deimic_pi.devices.led_driver.settings import Settings as LedDriverSettings


@enum.unique
class DeviceType(enum.IntFlag):
    LED_DRIVER          = enum.auto()   # noqa
    VOICE_RECOGNITION   = enum.auto()   # noqa
    VOICE_NOTIFICATIONS = enum.auto()

    EXTERNAL_APP        = enum.auto()   # noqa
    CLI_TOOL            = enum.auto()   # noqa

    DEIMIC              = enum.auto()   # noqa

    BRIDGE              = enum.auto()   # noqa

    UNKNOWN             = 0b0           # noqa
    ALL                 = 0b1111111     # noqa

    def get_familiar_signatures(self) -> set[int]:
        """
        Returns set of all possible signatures familiar with device.

        Returns:
            Signatures set

        """
        return {
            prefix
            for prefix in range(DeviceType.UNKNOWN, DeviceType.ALL)
            if prefix & self
        }

    @classmethod
    def keys(cls):
        return cls.__members__.keys()

    @classmethod
    def values(cls):
        return cls.__members__.values()

    @classmethod
    def build_signature(cls, devices: list['DeviceType']) -> int:
        """
        Builds signature corresponding with all the given device types.

        Params:
            - devices: Devices type list

        Returns:
            Signature corresponding with all the given device types

        """
        return sum(devices)


_T_Settings = t.Union[
    'BridgeSettings',
    'LedDriverSettings'
]


class Device(abc.ABC):
    """
    Device abstract class representing "module" of DeimicPi project
    like bridge, led driver, voice recognition etc.

    Each inheriting class must define its own `DEVICE_TYPE` and `POLLER_CLS`
    attributes
    """
    DEVICE_TYPE: DeviceType
    POLLER_CLS: t.Type[Poller]

    _sockets: list[zmq_asyncio.Socket] = []

    def __init__(self, settings: _T_Settings):
        self.settings = settings

        self._ctx = zmq_asyncio.Context()

    def create_socket(self, socket_type: int, **kwargs) -> zmq_asyncio.Socket:
        socket = self._ctx.socket(socket_type, **kwargs)
        self._sockets.append(socket)
        return socket

    def __del__(self):
        for socket in self._sockets:
            socket.close()
        self._ctx.term()

    async def execute(self):
        poller = self.POLLER_CLS(device=self)
        while True:
            await poller.handle()


class DeimicCompatibleDevice(Device):
    connected_deimic: str | None = None
