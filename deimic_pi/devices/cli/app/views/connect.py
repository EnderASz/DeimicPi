import rich.repr
from textual import events, log
from textual.views import GridView
from textual.message import Message, MessageTarget

from deimic_pi.devices.cli import CLITool
from deimic_pi.devices.cli.app.widgets import (
    TextInput,
    PortInput,
    SubmitButton,
    Submitted,
    Submittable
)
from deimic_pi.devices.cli.settings import Settings


class AppConnected(Message):
    __slots__ = (
        'cli_device'
    )

    def __init__(self, sender: MessageTarget, cli_device: CLITool):
        super().__init__(sender)
        self.cli_device = cli_device

    def __rich_repr__(self) -> rich.repr.Result:
        yield from super().__rich_repr__()
        yield 'cli_device', self.cli_device


class ConnectionEstablishView(GridView):
    address_input: TextInput
    monitor_port_input: TextInput
    request_port_input: TextInput
    submit_input: SubmitButton

    async def handle_submitted(self, message: Submitted):
        if not isinstance(message.sender, Submittable):
            log(
                f"Warning: {message} sent from {message.sender} instead of"
                f" {Submittable} instance"
            )
        if message.sender in [
            self.address_input,
            self.monitor_port_input,
            self.request_port_input,
            self.submit_input
        ]:
            valid = True

            address = self.address_input.value
            if not address:
                log(f"{self} - Bridge address cannot be empty value!")
                self.address_input.title_style = "red"
                valid = False
            else:
                self.address_input.title_style = ""

            try:
                monitor_port = self.monitor_port_input.value
            except ValueError as e:
                log(f"{self} - Invalid monitor_port value! - {e}")
                self.monitor_port_input.title_style = "red"
                valid = False
            else:
                self.monitor_port_input.title_style = ""

            try:
                request_port = self.request_port_input.value
            except ValueError as e:
                log(f"{self} - Invalid request_port value! - {e}")
                self.request_port_input.title_style = "red"
                valid = False
            else:
                self.request_port_input.title_style = ""

            self.address_input.render_title()
            self.monitor_port_input.render_title()
            self.request_port_input.render_title()

            if not valid:
                return
            connection = CLITool(Settings(
                bridge_addr_form=f"tcp://{address}:{'{port}'}",
                extern_bcst_port=monitor_port,
                extern_req_port=request_port
            ))
            await self.emit(AppConnected(
                self,
                connection
            ))

    async def on_mount(self, event: events.Mount):
        self.address_input = TextInput(
            "Bridge address",
            hint="localhost",
            title_align="left",
            title_style="bold",
            max_width=28
        )
        self.monitor_port_input = PortInput(
            "Monitor port",
            content=Settings.get_default('extern_bcst_port'),
            hint="5555",
            title_align="left",
            title_style="bold",
            max_width=28
        )
        self.request_port_input = PortInput(
            "Requests port",
            content=Settings.get_default('extern_req_port'),
            hint="5555",
            title_align="left",
            title_style="bold",
            max_width=28
        )
        self.submit_input = SubmitButton("connect")
        self.grid.set_align(column="center", row="center")
        self.grid.set_gap(column=0, row=1)
        self.grid.add_column("form", size=30)
        self.grid.add_row("data", repeat=3, size=3)
        self.grid.add_row("submit", size=3)
        self.grid.add_widget(self.address_input)
        self.grid.add_widget(self.monitor_port_input)
        self.grid.add_widget(self.request_port_input)
        self.grid.add_widget(self.submit_input)
