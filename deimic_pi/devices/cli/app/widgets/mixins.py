from textual import log
from textual.reactive import Reactive
from rich.console import StyleType
from rich.box import Box, ROUNDED as ROUNDED_BOX


class TitleMixin:
    _title: str = Reactive("")
    title_style: StyleType = Reactive("bold")

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value: str | None):
        self._title = (
            str(value)
            if value is not None
            else ""
        )
        log(f"{self} - Title changed to: {value}")

    _styled_title: str = ""

    @property
    def styled_title(self):
        return (
            f"[{self.title_style}]{self.title}[/{self.title_style}]"
            if self.title_style and self.title
            else self.title
        )

    def __init__(
        self,
        title: str | None,
        *,
        title_style: StyleType = "bold",
    ):
        self.title = title
        self.title_style = title_style


class SubtitleMixin(TitleMixin):
    _subtitle: str = Reactive("")
    subtitle_style: StyleType = Reactive("")

    @property
    def subtitle(self):
        return self._title

    @subtitle.setter
    def subtitle(self, value: str | None):
        self._subtitle = (
            str(value)
            if value is not None
            else ""
        )
        log(f"{self} - Title changed to: {value}")

    @property
    def styled_subtitle(self):
        return (
            f"[{self.subtitle_style}]{self.subtitle}[/{self.subtitle_style}]"
            if self.subtitle_style and self.subtitle
            else self.subtitle
        )

    full_title_style: StyleType = Reactive("")

    @property
    def full_title(self) -> str:
        return (
            f"{self.title} - {self.subtitle}"
            if self.subtitle
            else self.title
        )

    @property
    def styled_full_title(self):
        styled_full_title = (
            f"{self.styled_title} - {self.styled_subtitle}"
            if self.subtitle
            else self.title
        )
        if self.full_title_style and self.full_title:
            styled_full_title = f"[{self.full_title_style}]{styled_full_title}[/{self.full_title_style}]"
        return styled_full_title

    def __init__(
        self,
        title: str | None,
        subtitle: str | None,
        *,
        title_style: StyleType = "bold",
        subtitle_style: StyleType = "",
        full_title_style: StyleType = ""
    ):
        TitleMixin.__init__(
            self,
            title,
            title_style=title_style
        )

        self.subtitle = subtitle
        self.subtitle_style = subtitle_style

        self.full_title_style = full_title_style


class BorderMixin:
    border_style: StyleType = Reactive("")
    box: Box = Reactive(ROUNDED_BOX)

    def __init__(
        self,
        box: Box = ROUNDED_BOX,
        *,
        border_style: StyleType = ""
    ):
        self.box = box
        self.border_style = border_style
