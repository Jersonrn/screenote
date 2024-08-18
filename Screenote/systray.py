import os
import asyncio
import threading
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

from Screenote.screenote import Screenote
from Screenote.server import EventServer


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

        self.exit_item = Gtk.MenuItem(label="Quit")
        self.exit_item.connect("activate", self.on_exit)
        self.menu.append(self.exit_item)

        self.menu.show_all()
        self.menu.popup_at_pointer(None)

    def on_draw_mode(self, widget):
        print("on draw mode")
        self.draw_mode_state = widget.get_active()
        self.screenote.on_draw_mode(widget)

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
        self.screenote.present()

