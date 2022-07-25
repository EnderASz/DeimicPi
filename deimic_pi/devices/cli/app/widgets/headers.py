from datetime import datetime

import rich.repr
from rich.box import Box, ROUNDED as ROUNDED_BOX
from rich.style import StyleType
from rich.console import RenderableType
from rich.panel import Panel
from rich.align import Align, VerticalCenter
from rich.table import Table
from textual.widget import Widget
from textual import events
from textual.reactive import Reactive, watch


class Header(Widget):
    title: str = Reactive("")
    subtitle: str = Reactive("")

    content_style: StyleType = Reactive("")
    border_style: StyleType = Reactive("")
    box: Box = Reactive("")

    def __init__(
        self,
        title: str | None = None,
        subtitle: str | None = None,
        *,
        content_style: StyleType = "white on dark_green",
        border_style: StyleType = "white on dark_green",
        box: Box = ROUNDED_BOX
    ):
        super().__init__()
        self.title = title or self.app.title
        self.subtitle = subtitle
        self.content_style = content_style
        self.border_style = border_style
        self.box = box

    @property
    def full_title(self) -> str:
        return (
            f"{self.title} - {self.subtitle}"
            if self.subtitle
            else self.title
        )

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.full_title

    async def on_mount(self, event: events.Mount) -> None:
        self.set_interval(1.0, callback=self.refresh)

        async def set_title(title: str) -> None:
            if not self.title:
                self.title = title

        watch(self.app, 'title', set_title)

    def render(self) -> RenderableType:
        return Panel(
            VerticalCenter(Align(self.full_title, 'center')),
            style=self.content_style,
            border_style=self.border_style
        )


class ClockHeader(Header):
    def __init__(
        self,
        title: str | None = None,
        subtitle: str | None = None,
        *,
        content_style: StyleType = "white on dark_green",
        border_style: StyleType = "white on dark_green",
        box: Box = ROUNDED_BOX
    ):
        super().__init__(
            title=title,
            subtitle=subtitle,
            content_style=content_style,
            border_style=border_style,
            box=box
        )

    def get_clock(self) -> str:
        return datetime.now().time().strftime("%X")

    def render(self) -> RenderableType:
        header_table = Table.grid(expand=True, padding=(0, 0))
        header_table.style = self.content_style
        if self.size.width > 22 + len(self.full_title):
            header_table.add_column(justify='left', width=8)
            header_table.add_column('title', justify='center', ratio=1)
            header_table.add_column('clock', justify='right', width=8)
            header_table.add_row('', self.full_title, self.get_clock())
        else:
            header_table.add_column('title', justify='left', ratio=1)
            header_table.add_column('clock', justify='right', width=8)
            header_table.add_row(self.full_title, self.get_clock())
        return Panel(VerticalCenter(header_table), style=self.content_style, border_style=self.border_style)
