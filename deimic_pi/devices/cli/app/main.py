import typing as t

from textual.driver import Driver
from textual.app import App
from textual.widgets import Placeholder

from deimic_pi.devices.cli import CLITool
from deimic_pi.devices.cli.app.views import (
    ConnectionEstablishView,
    AppConnected, BridgeConsoleView
)


class CLIApp(App):
    cli_device: CLITool

    def __init__(
        self,
        screen: bool = True,
        driver_class: t.Type[Driver] | None = None,
        log: str = "",
        log_verbosity: int = 1,
        title: str = "DeimicPi CLI Tool",
    ):
        super().__init__(screen, driver_class, log, log_verbosity, title)

    async def handle_app_connected(self, message: AppConnected):
        self.cli_device = message.cli_device
        self.view.layout.docks.clear()
        self.view.widgets.clear()

        await self.view.dock(BridgeConsoleView(self.cli_device))

    async def on_mount(self):
        await self.view.dock(ConnectionEstablishView())


if __name__ == '__main__':
    CLIApp.run()
