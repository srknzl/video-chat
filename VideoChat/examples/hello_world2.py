import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")
        self.counter = 0
        self.button = Gtk.Button(label="Click Here")
        self.handler_id = self.button.connect("clicked", self.on_button_clicked, 10)
        self.add(self.button)
        #self.label = Gtk.Label(label="Hello sdasd", angle=25, halign=Gtk.Align.END)
        #self.add(self.label)
        print(dir(self.button.props))

    def on_button_clicked(self, widget, data):
        self.counter += 1
        print("Click count", self.counter,"/",data)
        if self.counter == data:
            print("Disabled button after reaching ", data, "clicks.")
            self.button.disconnect(self.handler_id)

win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()