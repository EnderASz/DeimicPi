import enum
import typing as t

from deimic_pi import types
from deimic_pi.devices.bridge import messages
import deimic_pi.messages as base
from deimic_pi.messages import MessagePartType

if t.TYPE_CHECKING:
    from deimic_pi.devices.bridge import Bridge


class DeimicHandler(base.MessageHandler):
    class DeimicMessageType(str, enum.Enum):
        OUTPUT = types.DeimicComponentType.OUTPUT 
        INPUT = types.DeimicComponentType.INPUT
        READY = "READY"
        REQUEST = "REQUEST"

    class ComponentUpdateInfo(base.MessageHandler):
        # Default values for kwargs, cause to: https://youtrack.jetbrains.com/issue/PY-41433
        @classmethod
        def handle(
            cls,
            *,
            device: 'Bridge',
            handling: t.Generator[
                bytes | list | str | int | float | dict,
                MessagePartType,
                None
            ],
            identity: bytes = None,
            payload: base.Payload = None,
            **kwargs
        ):
            if not isinstance(identity, bytes):
                raise ValueError(
                    "Identity value is invalid type:"
                    f" '{identity}' [{type(identity)}]"
                )

            if payload is None or len(payload) != 3:
                raise ValueError(
                    f"Invalid payload format: '{payload}' [{type(payload)}]"
                )

            messages.DeimicStateUpdateInfo.from_payload(
                payload=payload,
                received_from=identity
            ).send(
                socket=device.extern_broadcaster,
                device=device
            )

    class ApplicationForRequests(base.MessageHandler):
        # Default values for kwargs, cause to: https://youtrack.jetbrains.com/issue/PY-41433
        @classmethod
        def handle(
            cls,
            *,
            device: 'Bridge',
            handling: t.Generator[
                bytes | list | str | int | float | dict,
                MessagePartType,
                None
            ],
            identity: bytes = None,
            **kwargs
        ):
            print(f"Detected readiness for requests from Deimic[{identity}]")

            base.send_parts(
                socket=device.deimic_stream,
                parts=[
                    identity,
                    (MessagePartType.STRING, ":3")
                ]
            )

            # if device.deimic_requests_queue.empty():
            #     print(f"No request in queue for Deimic[{identity}]")
            #     base.send_parts(
            #         socket=device.deimic_stream,
            #         parts=[
            #             identity,
            #             (MessagePartType.STRING, "NO_REQUESTS")
            #         ]
            #     )
            # base.send_parts(
            #     socket=device.deimic_stream,
            #     parts=[
            #         identity,
            #         (MessagePartType.STRING, device.deimic_requests_queue.get())
            #     ]
            # )

    class Request(base.MessageHandler):
        # Default values for kwargs, cause to: https://youtrack.jetbrains.com/issue/PY-41433
        @classmethod
        def handle(
            cls,
            *,
            device: 'Bridge',
            handling: t.Generator[
                bytes | list | str | int | float | dict,
                MessagePartType,
                None
            ],
            identity: bytes = None,
            payload: base.Payload = None,
            **kwargs
        ):
            print(f"Received request message from Deimic[{identity}]: {payload}")

    @classmethod
    def handle(
        cls,
        *,
        device: 'Bridge',
        handling: t.Generator[
            bytes | list | str | int | float | dict,
            base.MessagePartType,
            None
        ],
        **kwargs
    ):
        identity: bytes = next(handling)
        payload: list[str] = handling.send(base.MessagePartType.STRING).split('-')
        # TODO: Replace `-` delimiter with `|`
        # payload: list[str] = handling.send(base.MessagePartType.STRING).split('|')

        message_type = payload.pop(0)
        match message_type:
            case "":
                print(f"Received empty message from Deimic[{identity}]. Propably it's start/end of connection.")
                return
            case cls.DeimicMessageType.OUTPUT | cls.DeimicMessageType.INPUT:
                cls.ComponentUpdateInfo.handle(
                    device=device,
                    handling=handling,
                    identity=identity,
                    payload=[message_type, *payload]
                )
            case cls.DeimicMessageType.READY:
                cls.ApplicationForRequests.handle(
                    device=device,
                    handling=handling,
                    identity=identity,
                    payload=payload
                )
            case cls.DeimicMessageType.REQUEST:
                cls.Request.handle(
                    device=device,
                    handling=handling,
                    identity=identity,
                    payload=payload
                )
            case _:
                print(f"Message of type `{message_type}` cannot be interpreted. Message payload: {payload}")


class InternalRepliesHandler(base.MessageHandler):
    @classmethod
    def handle(
        cls,
        *,
        device: 'Bridge',
        handling: t.Generator[
            bytes | list | str | int | float | dict,
            base.MessagePartType,
            None
        ],
        **kwargs
    ):
        pass


class ExternalRequestsHandler(base.MessageHandler):
    @classmethod
    def handle(
        cls,
        *,
        device: 'Bridge',
        handling: t.Generator[
            bytes | list | str | int | float | dict,
            base.MessagePartType,
            None
        ],
        **kwargs
    ):
        pass


class BridgePoller(base.Poller):
    def __init__(self, *, device: 'Bridge'):
        super().__init__(device)
        self.register(device.deimic_stream, DeimicHandler)
        self.register(device.inter_listener, InternalRepliesHandler)
        self.register(device.extern_listener, ExternalRequestsHandler)
