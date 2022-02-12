#!/usr/bin/env python
# encoding: utf-8
import curses
from sys import exit
from os import listdir
from time import sleep

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
s.connect(("127.0.0.1", 1232))

logfile = open("log", "a")

def log(*msg):
    logfile.write(" ".join([str(i) for i in msg]) + "\n")
    logfile.flush()

import npyscreen

class MyForm(npyscreen.FormBaseNew):
    def while_editing(form, thing):
        log("while_editing", thing)

    def adjust_widgets(x):
        log("adjust", x)

def rebuild(F, app):
    #F._clear_all_widgets()
    #F.add(npyscreen.TitleText, name = "Changed:",)
    #F.add(npyscreen.TitleFilename, name = "Filename:")
    #F.DISPLAY()
    F.editing = False
    makeform(app)

def test_func(k, ml):
    #log("key test_func", args)
    ml.value += " " + str(k)
    ml.display()
    return False

def callback(*args):
    print("callback", args)

def send(msg):
    msg = msg + ";\n"
    log(msg)
    s.send(msg.encode("utf8"))

def loop_selected(loops, values):
    msg = "loop " + "loops/" + loops[values[0]] + ";\n"
    log(msg)
    s.send(msg.encode("utf8"))

def makeform(app, selected=0):
        # These lines create the form and populate it with widgets.
        # A fairly complex screen in only 8 or so lines of code - a line for each control.
        F = MyForm(name = "cf-fakeboy", minimum_columns=20, minimum_lines=20)
        app.F = F

        #F.add_handlers({curses.ascii.ESC: self.exit_application})
        #F.add_handlers({curses.ascii.TAB: self.exit_application})
        #F.add_handlers({"   ": self.exit_application})
        #F.add_handlers({27: self.exit_application})
        #F.add_handlers({"KEY_F(2)": self.exit_application})
        #F.add_handlers({"^Y": self.exit_application})
        #log(F.handlers)
        #F.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE]  = self.exit_application

        #b  = F.add(npyscreen.ButtonPress, name = "COOL", when_pressed_function = lambda: app.exit_application())

        #t  = F.add(npyscreen.TitleText, name = "Text:",)
        #fn = F.add(npyscreen.TitleFilename, name = "Filename:")
        #fn2 = F.add(npyscreen.TitleFilenameCombo, name="Filename2:")
        #dt = F.add(npyscreen.TitleDateCombo, name = "Date:")
        s  = F.add(npyscreen.TitleSlider, out_of=4, name = "Volume", value=2)
        s.when_value_edited=lambda: send("volume " + str(s.value))

        #ml = F.add(npyscreen.MultiLineEdit, value="", max_height=5)

        loops = [l for l in listdir("loops") if l.endswith(".wav")]

        ms = F.add(npyscreen.TitleSelectOne, max_height=8, value = [0,], name="Loop", values = loops, scroll_exit=True)
        ms.when_value_edited=lambda: loop_selected(loops, ms.value)

        quit = F.add(npyscreen.ButtonPress, name = "quit", when_pressed_function = lambda: app.exit_application())

        #ms2= F.add(npyscreen.TitleMultiSelect, max_height =-2, value = [1,], name="Pick Several",
        #        values = ["Option1","Option2","Option3"], scroll_exit=True)

        #F.add_handlers({"^Y": lambda x: rebuild(F, app)})
        #F.add_complex_handlers([[lambda k: test_func(k, ml), callback]])

        # This lets the user interact with the Form.
        F.edit()

class TestApp(npyscreen.NPSApp):
    def main(self):
        makeform(self)
        #print(ms.get_selected_objects())

    def exit_application(self):
        log("EXIT APPLICATION")
        #curses.beep()
        #self.setNextForm(None)
        #self.NEXT_ACTIVE_FORM = None
        #self.editing = False
        s.close()
        exit()

if __name__ == "__main__":
    App = TestApp()
    App.run()

