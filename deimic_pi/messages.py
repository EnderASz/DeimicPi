import abc
import enum
import typing as t

import zmq
import zmq.asyncio as zmq_asyncio

if t.TYPE_CHECKING:
    from deimic_pi.devices import Device


class MessageType(str, enum.Enum):
    ERROR = 'ERROR'
    STATE_UPDATE = 'STATE_UPDATE'
    REQUEST = 'REQUEST'


class MessagePartType(str, enum.Enum):
    RAW = 'RAW'
    PYOBJ = 'PYOBJ'
    STRING = 'STRING'
    JSON = 'JSON'


PayloadPart = bytes | list | str | int | float | dict
Payload = list[PayloadPart]
Handling = t.AsyncGenerator[PayloadPart, MessagePartType]


async def send_parts(
    *,
    socket: zmq_asyncio.Socket,
    parts: list[tuple[MessagePartType, PayloadPart] | PayloadPart],
):
    for i, part in enumerate(parts):
        if isinstance(part, tuple):
            part_type, part_payload = part
        else:
            part_type, part_payload = MessagePartType.RAW, part

        match part_type or MessagePartType.RAW:
            case MessagePartType.RAW:
                send_method = socket.send
            case MessagePartType.PYOBJ:
                send_method = socket.send_pyobj
            case MessagePartType.STRING:
                send_method = socket.send_string
            case MessagePartType.JSON:
                send_method = socket.send_json
            case _:
                raise ValueError(f"Invalid 'part_type' parameter value: {part_type}")
        await send_method(part_payload, zmq.SNDMORE if i < len(parts)-1 else 0)


T_ = t.TypeVar('T_')


class MessageBearer(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def from_handling(cls: t.Type[T_], handling: Handling) -> T_:
        ...

    @classmethod
    @abc.abstractmethod
    def from_payload(
        cls: t.Type[T_],
        *,
        received_from: bytes,
        payload: Payload
    ) -> T_:
        ...

    @abc.abstractmethod
    def send(self, socket: zmq_asyncio.Socket, device: 'Device'):
        ...


class MessageHandler(abc.ABC):
    @classmethod
    async def handle_from_socket(cls, *, device: 'Device', socket: zmq_asyncio.Socket):
        message = _handle_multipart(socket)
        await anext(message)
        await cls.handle(device=device, handling=message)

    @classmethod
    @abc.abstractmethod
    async def handle(
        cls,
        *,
        device: 'Device',
        handling: Handling,
        **kwargs
    ):
        ...


async def _handle_multipart(socket: zmq_asyncio.Socket) -> Handling:
    part_type = yield
    while True:
        match part_type or MessagePartType.RAW:
            case MessagePartType.RAW:
                part_type = yield await socket.recv()
            case MessagePartType.PYOBJ:
                part_type = yield await socket.recv_pyobj()
            case MessagePartType.STRING:
                part_type = yield await socket.recv_string()
            case MessagePartType.JSON:
                part_type = yield await socket.recv_json()
            case _:
                raise ValueError(f"Invalid 'part_type' value: {part_type}")
        if not socket.getsockopt(zmq.RCVMORE):
            break


class Poller:
    _sockets: dict[zmq_asyncio.Socket, t.Type[MessageHandler]] = {}

    def __init__(
        self,
        device: 'Device'
    ):
        self._poller = zmq_asyncio.Poller()
        self.device = device

    def register(
        self,
        socket: zmq_asyncio.Socket,
        handler: t.Type[MessageHandler]
    ):
        self._poller.register(socket, zmq.POLLIN)
        self._sockets.update({socket: handler})

    async def handle(self):
        result = await self._poller.poll()
        if not result:
            return False

        for socket, _ in result:
            await self._sockets.get(socket).handle_from_socket(device=self.device, socket=socket)
