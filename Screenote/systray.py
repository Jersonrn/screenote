import os
import threading
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

from Screenote.screenote import Screenote
from Screenote.server import EventServer
from Screenote.tools import Tool


TOOLS = {
        "brush_tool": {"tooltip": "brush tool", "tool_name": "polyline", "icon_name": "draw-brush"},
        "draw_circle": {"tooltip": "draw circle", "tool_name": "circle", "icon_name": "draw-circle"},
        "draw_line": {"tooltip": "draw line", "tool_name": "line", "icon_name": "tool_line"},
        "draw_ellipse": {"tooltip": "draw ellipse", "tool_name": "ellipse", "icon_name": "tool_ellipse"},
        }

class SystemTrayIcon:
    def __init__(self):
        #ICON
        self.icon = Gio.Icon.new_for_string("draw-brush")
        self.tray_icon = Gtk.StatusIcon.new_from_gicon(self.icon)

        self.tray_icon.connect("popup-menu", self.on_right_click)
        self.tray_icon.connect("activate", self.on_left_click)

        self.tray_icon.set_visible(True)

        #MENU
        self.menu: Gtk.Menu
        self.show_draw_item: Gtk.CheckMenuItem
        self.show_draw_state = True
        self.draw_mode_item: Gtk.CheckMenuItem
        self.draw_mode_state = False
        self.make_menu()

        #POPUP
        self.screenote = Screenote(self)

        #TOOLS
        self.tools = None
        self.draw_mode_tool: Gtk.ToggleToolButton

        #SERVER
        self.server = EventServer(parent=self)
        self.server_thread = threading.Thread(target=self.server.start)
        self.server_thread.start()


    def on_right_click(self, icon, button, time):
        self.make_menu()

    def make_menu(self):
        self.menu = Gtk.Menu()

        self.show_draw_item = Gtk.CheckMenuItem.new_with_label("Show Draw")
        self.show_draw_item.set_active(self.show_draw_state)
        self.show_draw_item.connect("toggled",self.on_show_draw)
        self.menu.append(self.show_draw_item)

        self.draw_mode_item = Gtk.CheckMenuItem.new_with_label("Draw Mode")
        self.draw_mode_item.set_active(self.draw_mode_state)
        self.draw_mode_item.connect("toggled", self.on_draw_mode)
        self.menu.append(self.draw_mode_item)

        self.tools_item = Gtk.MenuItem(label="Tools")
        self.tools_item.connect("activate", self.on_tools_dialog)
        self.make_tools_dialog()
        self.menu.append(self.tools_item)

        self.exit_item = Gtk.MenuItem(label="Quit")
        self.exit_item.connect("activate", self.on_exit)
        self.menu.append(self.exit_item)

        self.menu.show_all()
        self.menu.popup_at_pointer(None)

    #Show tools dialog
    def on_tools_dialog(self, widget=None):
        print("On tools dialog")
        self.tools.show_all()

        self.screenote.present()

    def make_tools_dialog(self):
        print("make_tools_dialog")
        self.tools = Gtk.Dialog(
                "TOOLS",
                None,
                Gtk.DialogFlags.DESTROY_WITH_PARENT,
                (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE),
                # use_header_bar=True,
                destroy_with_parent=True,
                resizable=False
        )
        # self.tools.add_button("CLOSE", Gtk.ResponseType.CLOSE)
        # self.tools.connect("response", self.on_tools_close)
        # self.tools.connect("delete-event", self.on_tools_close)
        self.tools.connect(
                "response",
                lambda d, response: d.destroy()
                if response == Gtk.ResponseType.CLOSE else None
        )

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        toolbar = Gtk.Toolbar(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(toolbar, False, False, 0)

        #TOOLS
        for params in TOOLS.values():
            tool = Tool(
                    tooltip=params["tooltip"],
                    tool_name=params["tool_name"],
                    icon_name=params["icon_name"]
            )
            tool.connect("clicked", self.on_tool_clicked)
            toolbar.insert(tool, -1)

        separator = Gtk.SeparatorToolItem()
        separator.set_draw(True)
        toolbar.insert(separator, -1)

        self.draw_mode_tool = Gtk.ToggleToolButton.new()
        self.draw_mode_tool.set_active(self.draw_mode_state)
        self.draw_mode_tool.set_icon_name("key-enter")
        self.draw_mode_tool.set_tooltip_text("draw mode")
        self.draw_mode_tool.connect("clicked", self.on_draw_mode_tool_clicked)
        toolbar.insert(self.draw_mode_tool, -1)

        #Add vbox to dialog
        self.tools.get_content_area().pack_start(vbox, True, True, 0)

    #Called when clicking on a drawing tool (brush, line, circle, etc)
    def on_tool_clicked(self, widget):
        print(f"{widget.tool_name} selected")
        self.screenote.selected_tool = widget.tool_name

    #Called when the 'draw_mode_tool' is clicked
    def on_draw_mode_tool_clicked(self, button):
        print("on draw mode clicked")
        status = button.get_active()
        self.draw_mode_item.set_active(status) #Emit signal

    #Enable/disable draw mode
    def on_draw_mode(self, widget):
        print("on draw mode")
        self.draw_mode_state = widget.get_active()
        self.draw_mode_tool.set_active(self.draw_mode_state)
        self.screenote.on_draw_mode()

    def on_show_draw(self, widget):
        print("on show draw")
        self.show_draw_state = widget.get_active()
        self.screenote.on_show_draw(widget)

    def on_left_click(self, icon):
        print("Click!")

    def on_exit(self, widget=None, data=None, exit_status=os.EX_OK):
        print("Exit!")
        self.server.stop()
        self.server_thread.join()
        print("Server stopped. Exiting...")

        self.exit_status = exit_status
        Gtk.main_quit()


    def bring_to_front(self):
        print("bring_to_front")
        self.screenote.present()

