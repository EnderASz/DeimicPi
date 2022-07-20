import asyncio
import os
from pathlib import Path

import click

from deimic_pi.devices.bridge import Bridge
from deimic_pi.devices.bridge.settings import Settings, BridgeSettings
from deimic_pi.types import Port


@click.command()
@click.option(
    '--bcst-port',
    '-b',
    'inter_broadcaster_port',
    default=Settings.get_default('inter_broadcaster_port'),
    show_default=True,
    type=Port(),
    help="Internal requests broadcaster's port")
@click.option(
    '--listener-port',
    '-l',
    'inter_listener_port',
    default=Settings.get_default('inter_listener_port'),
    show_default=True,
    type=Port(),
    help="Internal replies receiver's port")
def execute(inter_broadcaster_port, inter_listener_port):
    settings = Settings.from_file(
        bridge=BridgeSettings(),
        inter_broadcaster_port=inter_broadcaster_port,
        inter_listener_port=inter_listener_port
    )
    bridge = Bridge(settings)
    bridge.execute()


if __name__ == '__main__':
    execute()
