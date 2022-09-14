import enum
import typing as t

from deimic_pi import types
from deimic_pi.devices.cli import messages
import deimic_pi.messages as base
from deimic_pi.messages import MessagePartType, PayloadPart

if t.TYPE_CHECKING:
    from deimic_pi.devices.cli import CLITool


class MonitorHandler(base.MessageHandler):
    @classmethod
    async def handle(
        cls,
        *,
        device: 'CLITool',
        handling: base.Handling,
        **kwargs
    ):
        pass


class CLIPoller(base.Poller):
    def __init__(self, *, device: 'CLITool'):
        super().__init__(device)
        self.register(device.monitor_socket, MonitorHandler)
