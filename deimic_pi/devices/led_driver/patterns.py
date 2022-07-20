import abc
import colorsys
import time
import typing as t
from threading import Event

import board
from neopixel import NeoPixel

from deimic_pi.devices.led_driver.settings import Settings


_patterns: dict[str, t.Type['PatternBearer']] = dict()


def _pattern_class(cls: t.Type['PatternBearer']):
    _patterns.update({cls.__name__: cls})
    return cls


def get_pattern(name: str):
    return _patterns.get(name)


class PatternBearer(abc.ABC):
    def __init__(
        self,
        settings: Settings,
        **pattern_kwargs
    ):
        self.led_strip = NeoPixel(
            pin=settings.led_driver.data_pin,
            n=settings.led_driver.strip_length
        )

    def __del__(self):
        pass

    @abc.abstractmethod
    def step(self, time_elapsed: float) -> int:
        """
        _summary_

        Params:
            - time_elapsed: Time elapsed since led pattern loop execution

        Returns:
            Number of milliseconds, that loop should wait before executing next
            loop step.
            If 0 returned no more steps should be executed.
        """
        ...

    def execute(self, stop_controller: Event, run_controller: Event):
        execute_time = time.time()
        time_elapsed = 0
        to_next_step = self.step(time_elapsed)
        while not stop_controller.is_set() and to_next_step:
            time.sleep(to_next_step/1000)
            run_controller.wait()
            time_elapsed = time.time() - execute_time
            to_next_step = self.step(time_elapsed)
        # TODO: Do not finish after last step


@_pattern_class
class ConstColorPattern(PatternBearer):
    def __init__(
        self,
        settings: Settings,
        *,
        color: tuple[int, int, int]
    ):
        super().__init__(settings)

        r, g, b = colorsys.hsv_to_rgb(*color)
        color = int(r), int(g), int(b)

        self.led_strip.fill(color)

    def step(self, time_elapsed: float) -> int:
        pass
