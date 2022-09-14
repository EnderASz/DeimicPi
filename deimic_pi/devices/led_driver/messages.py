import enum
import typing as t
from threading import Thread

from deimic_pi.devices.led_driver import LedDriver
from deimic_pi.devices.led_driver.patterns import PatternBearer, get_pattern
from deimic_pi.messages import (
    MessageHandler,
    Poller,
    MessagePartType,
    Handling
)


class RequestTypes(enum.IntEnum):
    OFF = enum.auto()
    ON = enum.auto()
    PATTERN = enum.auto()


class RequestHandler(MessageHandler):
    @classmethod
    async def handle(
        cls,
        *,
        device: LedDriver,
        handling: Handling,
        **kwargs
    ):
        _ = await anext(handling)   # Request targets signature
        request_type = await handling.asend(MessagePartType.STRING)
        match request_type:
            case RequestTypes.OFF:
                device.executor_run_controller.clear()
            case RequestTypes.ON:
                device.executor_run_controller.set()
            case RequestTypes.PATTERN:
                # TODO: Replace with selecting pattern by name
                pattern_name = await handling.asend(MessagePartType.STRING)
                pattern_cls = get_pattern(pattern_name)

                pattern_kwargs = await handling.asend(MessagePartType.JSON)

                if device.led_executor is not None:
                    device.executor_stop_controller.set()
                    device.led_executor.join()
                with pattern_cls(
                    device.settings,
                    **pattern_kwargs
                ) as pattern:
                    device.led_executor = Thread(
                        daemon=True,
                        target=pattern.execute,
                        args=(
                            device.executor_stop_controller,
                            device.executor_run_controller
                        )
                    )

    @staticmethod
    def _pattern_handle(self, payload) -> PatternBearer:
        pass

    # async def _execute_leds(
    #         self,
    #         pattern_cls: type[PatternBearer],
    #         **pattern_kwargs
    # ):
    #     pattern = pattern_cls(self.settings, **pattern_kwargs)
    #     await pattern.execute()

    # @staticmethod
    # async def _recv_pattern(
    #     recv_socket: zmq.Socket
    # ) -> t.Union[
    #      tuple[None, None, None],
    #      tuple[PatternBearer, dict, list[bytes | Frame]]
    # ]:
    #     """
    #     Waits for multipart message from given socket and returns received led
    #     pattern, keyword pattern parameters and list of leftover message parts.
    #
    #     Params:
    #         - recv_socket: Receiving socket
    #
    #     Returns:
    #         Three element tuple of pattern class, keyword pattern parameters
    #         and list of leftover message parts.
    #     """
    #     _ = recv_socket.recv_string()   # Receive group signature
    #
    #     # TODO: Replace with own exception class in raises
    #     try:
    #         pattern_cls = recv_socket.recv_pyobj(zmq.NOBLOCK)
    #         pattern_kwargs = recv_socket.recv_pyobj(zmq.NOBLOCK)
    #     except zmq.error.Again:
    #         return None, None, None
    #     if not (
    #         isinstance(pattern_cls, PatternBearer)
    #         and isinstance(pattern_kwargs, dict)
    #     ):
    #         return None, None, None
    #
    #     additional_parts = list()
    #     while recv_socket.getsockopt(zmq.RCVMORE):
    #         additional_parts.append(recv_socket.recv())
    #
    #     return pattern_cls, pattern_kwargs, additional_parts


class LedDriverPoller(Poller):
    def __init__(self, *, device: LedDriver):
        super().__init__(device)
        self.register(device.requests_socket, RequestHandler)

#
# class PatternMessage(MessageBearer):
#     MESSAGE_TYPE = MessageType.PATTERN
#
#     pattern_cls: PatternBearer
#     pattern_kwargs: dict[str, t.Any]
#
#     def __init__(self, pattern_cls: PatternBearer, **pattern_kwargs):
#         self.pattern_cls = pattern_cls
#         self.pattern_kwargs = pattern_kwargs
#
#     async def send(
#         self,
#         ctx: zmq.asyncio.Context
#     ):
#         pass
