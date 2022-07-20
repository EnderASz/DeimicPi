import abc
import typing as t

import zmq

import deimic_pi.messages as base
from deimic_pi import types

if t.TYPE_CHECKING:
    from deimic_pi.devices.device import Device
