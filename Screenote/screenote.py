import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Pango', '1.0')

from gi.repository import (
        GLib, Gtk, Gdk, GdkPixbuf,
        Pango, GObject, AyatanaAppIndicator3
)
import cairo

from screeninfo import get_monitors
from Screenote.svg import SVG
from Screenote.color import Color


APP_NAME = "Screenote"
CENTER = Gtk.Align.CENTER
FPS = 12


class Screenote(Gtk.Window):
    def __init__(self, parent) -> None:
        super().__init__(Gtk.WindowType.POPUP)
        self.systray = parent
        self.set_type_hint(Gdk.WindowTypeHint.SPLASHSCREEN)

        self.set_keep_above(True)
        self.set_accept_focus(False)
        self.set_focus_on_map(False)
        self.set_app_paintable(True)

        self.set_size_request(0, 0)
        self.set_gravity(Gdk.Gravity.CENTER)
        self.connect("configure-event", self.on_configure)
        self.connect("draw", self.on_draw)

        self.bg_color = Gdk.RGBA(0., 0., 0., 0.0)

        #IMAGE
        self.svg = SVG(1600, 900, "gtk_svg_test", "./images")

        self.image: Gtk.Image
        self.update_image(new=True)
        self.add(self.image)

        #WIDGET
        self.menu: Gtk.Menu

        # self.make_menu()
        # self.make_appindicator()

        #Transparent
        self.monitor = 0
        scr = self.get_screen()
        visual = scr.get_rgba_visual()
        if visual is not None:
            self.set_visual(visual)

        self.update_window()

        #MOUSE
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK)
        self.connect("button-press-event", self.on_mouse_click)
        self.connect("button-release-event", self.on_mouse_release)
        self.connect("motion-notify-event", self.on_mouse_motion)

        self.mouse_left_pressed = False
        self.mouse_middle_pressed = False
        self.mouse_right_pressed = False

        self.mouse_position_old = (0, 0)
        self.mouse_position = (0, 0)
        self.mouse_motion_timeout = None
        self.mouse_available = True


    def quit(self, widget=None, data=None, exit_status=os.EX_OK):
        self.exit_status = exit_status
        Gtk.main_quit()

    def on_draw(self, widget, cr):
        print("on draw")
        cr.set_source_rgba(
                self.bg_color.red,
                self.bg_color.green,
                self.bg_color.blue,
                self.bg_color.alpha
        )
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        return False

    def on_configure(self, event, data):
        print("on configure")
        self.configure_click_through()

    def configure_click_through(self):
        # set event mask for click-through
        if self.systray.draw_mode_item.get_active():
            self.input_shape_combine_region(None)
        else:
            self.input_shape_combine_region(cairo.Region(cairo.RectangleInt(0, 0, 0, 0)))

    def on_draw_mode(self, widget):
        if widget.get_active():
            self.systray.show_draw_item.set_active(True)
            self.bg_color = Gdk.RGBA(0., 0., 0., 0.2)
            self.present()
        else:
            self.bg_color = Gdk.RGBA(0., 0., 0., 0.0)
            self.present()

        self.update_window()
        self.configure_click_through()

    def on_show_draw(self, widget):
        if self.systray.show_draw_item.get_active():
            print("Showing Draws")
            self.image.show()
            self.present()
        else:
            print("Hidden Draws")
            self.image.hide()


    def on_mouse_click(self, widget, event):
        x, y = event.x, event.y
        button = event.button

        self.update_mouse_position(old_pos=(x, y),new_pos=(x,y))

        if button == 1:
            self.mouse_left_pressed = True
            self.svg.create_stroke(
                    "polyline",#polyline-circle-line
                    x= self.mouse_position[0],
                    y=self.mouse_position[1],
                    fill=Color(None),
                    stroke=Color((255,0,0)),
                    stroke_width=4
            )
        elif button == 2:
            self.mouse_middle_pressed = True
        elif button == 3:
            self.mouse_right_pressed = True
            self.systray.draw_mode_item.set_active(False) #Right Click Cancel Draw

        self.mouse_motion_timeout = GLib.timeout_add(1000/FPS, self.set_mouse_available)
        print(f"Click on: ({x}, {y}), Button: {button}")

    def on_mouse_release(self, widget, event):
        x, y = event.x, event.y
        button = event.button

        self.update_mouse_position(old_pos=self.mouse_position,new_pos=(x,y))
        self.svg.add_stroke()
        # self.update_svg()
        self.update_image(update_window=True)

        if button == 1:
            self.mouse_left_pressed = False
        elif button == 2:
            self.mouse_middle_pressed = False
        elif button == 3:
            self.mouse_right_pressed = False

        GLib.source_remove(self.mouse_motion_timeout)
        print(f"Free on: ({x}, {y}), Button: {button}")

    def on_mouse_motion(self, widget, event):
        if self.mouse_left_pressed:
            if not self.mouse_available:
                return
            print("Drawing")
            x, y = event.x, event.y
            self.update_mouse_position(old_pos=self.mouse_position,new_pos=(x,y))
            self.svg.add_point(self.mouse_position[0], self.mouse_position[1])
            # self.update_svg()
            self.update_image(update_window=True)

            self.mouse_available = False
            self.mouse_motion_timeout = GLib.timeout_add(1000/FPS, self.set_mouse_available)

    def set_mouse_available(self):
        self.mouse_available = True


    def update_window(self):
        print("update window")
        monitors = get_monitors()

        self.width = monitors[0].width + 2
        self.height = monitors[0].height + 2
        self.move(-1, -1)
        self.resize(self.width, self.height )

        self.queue_draw()
        self.show_all()
    
    def update_image(self, new = False, update_window = False):
        print("update img")
        loader = GdkPixbuf.PixbufLoader()
        loader.write(self.svg.to_bytes())
        loader.close()
        pixbuf = loader.get_pixbuf()

        if new:
            self.image = Gtk.Image.new_from_pixbuf(pixbuf)
        else:
            self.image.set_from_pixbuf(pixbuf)

        if update_window:
            self.update_window()

    def update_mouse_position(self, old_pos, new_pos):
        self.mouse_position_old = old_pos
        self.mouse_position = new_pos

    def update_svg(self):
        self.svg.add_line(
                x1=self.mouse_position_old[0],
                x2=self.mouse_position[0],
                y1=self.mouse_position_old[1],
                y2=self.mouse_position[1],
                color=(255,0,0),
                stroke_width=4
        )
        self.update_image(update_window=True)

