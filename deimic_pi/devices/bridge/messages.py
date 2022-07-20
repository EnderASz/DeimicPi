import abc
import typing as t

import zmq

import deimic_pi.messages as base
from deimic_pi import types

if t.TYPE_CHECKING:
    from deimic_pi.devices.device import Device


class DeimicStateUpdateInfo(base.MessageBearer):
    def __init__(
        self,
        component_type: types.DeimicComponentType,
        address: int,
        number: int,
        new_state: base.PayloadPart,
        received_from: bytes = None
    ):
        self.received_from = received_from
        self.component_type = component_type
        self.address = address
        self.number = number
        self.new_state = new_state

    @classmethod
    @abc.abstractmethod
    def from_handling(cls, handling: base.Handling) -> 'DeimicStateUpdateInfo':
        raise NotImplementedError()

    @classmethod
    def from_payload(
        cls,
        *,
        received_from: bytes,
        payload: base.Payload
    ) -> 'DeimicStateUpdateInfo':
        return cls(*payload, received_from=received_from)

    def send(self, socket: zmq.Socket, device: 'Device'):
        print(
            f"Received Deimic[{self.received_from}] component state update:"
            f" '{self.component_type} {self.address}-{self.number}'"
            f" ({self.new_state})"
        )
        base.send_parts(
            socket=socket,
            parts=[
                (base.MessagePartType.STRING, base.MessageType.STATE_UPDATE),
                b'',

                (base.MessagePartType.STRING, "DEIMIC"),
                b'',
                (base.MessagePartType.PYOBJ, self.component_type),
                (base.MessagePartType.PYOBJ, self.address),
                (base.MessagePartType.PYOBJ, self.number),
                (base.MessagePartType.PYOBJ, self.new_state)
            ]
        )
