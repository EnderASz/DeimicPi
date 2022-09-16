from rich import align
from rich.console import RenderableType, StyleType
from rich.panel import Panel
from rich.box import Box, ROUNDED as ROUNDED_BOX
from textual import events, log
from textual.message import Message
from textual.message_pump import MessagePump
from textual.reactive import Reactive
from textual.widget import Widget
from textual import widgets as base

from deimic_pi.devices.cli.app.widgets import mixins
from deimic_pi.types import Port


class Submitted(Message):
    pass


class Submittable(MessagePump):
    async def submit(self):
        await self.emit(Submitted(self))


class TextInput(
    Widget,
    Submittable,
    mixins.TitleMixin,
    mixins.BorderMixin,
    mixins.TextContentCursorMixin,
    mixins.TextHintMixin
):
    _content_boundaries: tuple[int, int] = Reactive((0, 0))

    @mixins.TextContentCursorMixin.content.setter
    def content(self, value: str | None):
        mixins.TextContentMixin.content.fset(self, value)

        if self._content_boundaries[0] > 0:
            if len(self.content) < self._content_boundaries[1]:
                self._move_boundaries(-1)
                return
        log(f"{self} - Content boundaries changed to: {self._content_boundaries}")

    @mixins.TextContentCursorMixin.cursor.setter
    def cursor(self, value: int):
        mixins.TextContentCursorMixin.cursor.fset(self, value)

        if self._content_boundaries[0] > self.cursor:
            self._move_boundaries(self.cursor - self._content_boundaries[0])
        elif self._content_boundaries[1] < self.cursor:
            self._move_boundaries(self.cursor - self._content_boundaries[1])
        elif self._content_boundaries[1] == self.cursor:
            self._move_boundaries(1)

    @property
    def before_cursor_in_boundaries(self) -> str:
        return self.content[self._content_boundaries[0]:self.cursor]

    @property
    def after_cursor_in_boundaries(self) -> str:
        return self.content[self.cursor+1:self._content_boundaries[1]]

    @property
    def value(self) -> str:
        """
        Returns value contained in text input content.
        """
        if self.trim_whitespaces:
            return self.content.strip()
        return self.content

    def __init__(
        self,
        name: str,
        *,
        title: str | None = None,
        content: str = "",
        cursor: int = 0,
        hint: str = "",
        title_align: align.AlignMethod = "center",
        content_align: align.AlignMethod = "left",
        title_style: StyleType = "bold",
        content_style: StyleType = "",
        cursor_style: StyleType = "underline",
        border_style: StyleType = "",
        box: Box = ROUNDED_BOX,
        hint_style: StyleType = "italic bright_black",
        max_width: int | None = None,
        # lines: int = 1,
        trim_whitespaces: bool = True
    ):
        Widget.__init__(self, name)
        mixins.TitleMixin.__init__(
            self,
            title if title is not None else name,
            title_style=title_style
        )
        mixins.BorderMixin.__init__(
            self,
            box=box,
            border_style=border_style
        )
        mixins.TextContentCursorMixin.__init__(
            self,
            content,
            cursor,
            content_style=content_style,
            cursor_style=cursor_style
        )
        mixins.TextHintMixin.__init__(
            self,
            hint,
            hint_style=hint_style
        )

        self.max_width = max_width
        # self.lines = lines
        self.lines = 1

        self.title_align = title_align
        self.content_align = content_align

        self.trim_whitespaces = trim_whitespaces

    def on_show(self, event: events.Show):
        self._content_boundaries = (0, self.size.width-4)

    async def on_key(self, event: events.Key):
        if len(event.key) == 1 and 32 <= ord(event.key) <= 126:
            self.write(event.key)
        else:
            match event.key:
                case "ctrl+h":
                    if self.cursor > 0:
                        self.backspace()
                case "delete":
                    if self.cursor < len(self.content):
                        self.delete()
                case "left":
                    try:
                        self.move_cursor(-1)
                    except ValueError:
                        pass
                case "right":
                    try:
                        self.move_cursor(1)
                    except ValueError:
                        pass
                case "enter":
                    await self.submit()

    def on_focus(self, event: events.Focus):
        self.show_cursor()

    def on_blur(self, event: events.Blur):
        self.hide_cursor()

    def _move_boundaries(self, move: int):
        self._content_boundaries = (
            self._content_boundaries[0] + move,
            self._content_boundaries[1] + move
        )
        log(f"{self} - Content boundaries moved to: {self._content_boundaries}")

    @property
    def styled_content(self) -> str:
        if self.cursor_visibility or self.content:
            content = [self.at_cursor or " "]
            if self.cursor_visibility and self.cursor_style:
                content = [
                    f"[{self.cursor_style}]",
                    *content,
                    f"[/{self.cursor_style}]",
                ]
            content = [
                self.before_cursor_in_boundaries,
                *content,
                self.after_cursor_in_boundaries
            ]
            if self.content_style:
                content = [
                    f"[{self.content_style}]",
                    *content,
                    f"[/{self.content_style}]"
                ]
            return "".join(content)
        return self.styled_hint

    def render(self) -> RenderableType:
        return Panel(
            align.Align(
                self.styled_content,
                align=self.content_align,
            ),
            title=self.styled_title,
            title_align=self.title_align,
            width=self.max_width,
            height=self.lines+2,
            border_style=self.border_style,
            box=self.box
        )


class PortInput(TextInput):
    @property
    def value(self) -> Port:
        return Port(super().value)


class SubmitButton(base.Button, Submittable):
    async def on_key(self, event: events.Key):
        if event.key == "enter":
            await self.submit()

    async def on_click(self, event: events.Click) -> None:
        event.prevent_default().stop()
        await self.submit()
