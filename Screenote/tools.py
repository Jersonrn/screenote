import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class Tool(Gtk.ToolButton):
    def __init__(
            self,
            tooltip: str,
            tool_name: str,
            icon_name: str,
            label: str | None = None
    ) -> None:
        super().__init__()

        self.tool_name = tool_name
        self.set_tooltip_text(tooltip)
        self.set_icon_name(icon_name)

        if label is not None:
            self.set_label(label)

