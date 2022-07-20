from textual import events
from textual.reactive import Reactive
from textual.views import GridView

from deimic_pi.devices.cli.app.widgets.inputs import TextInput
from deimic_pi.devices.cli.settings import Settings


class ConnectionEstablishView(GridView):
    address: TextInput = Reactive("")
    monitor_port: TextInput = Reactive("")
    request_port: TextInput = Reactive("")

    async def on_mount(self, event: events.Mount):
        self.address = TextInput(
            "Bridge address",
            hint="localhost",
            title_align="left",
            title_style="bold",
            line_length=30
        )
        self.monitor_port = TextInput(
            "Monitor port",
            content=Settings.get_default('extern_bcst_port'),
            hint="5555",
            title_align="left",
            title_style="bold",
            line_length=30
        )
        self.request_port = TextInput(
            "Requests port",
            content=Settings.get_default('extern_req_port'),
            hint="5555",
            title_align="left",
            title_style="bold",
            line_length=30
        )
        self.grid.set_align(column="center", row="center")
        self.grid.set_gap(column=0, row=1)
        self.grid.add_column("center", size=30)
        self.grid.add_row("data", repeat=3, size=3)
        self.grid.add_widget(self.address)
        self.grid.add_widget(self.monitor_port)
        self.grid.add_widget(self.request_port)
