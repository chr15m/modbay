#!/usr/bin/env python
# encoding: utf-8
import curses
import re
from sys import exit, argv
from os import listdir, mkdir
from os.path import splitext
from time import sleep
from subprocess import check_output, STDOUT
import npyscreen
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
s.connect(("127.0.0.1", 1232))

logfile = open("log", "a")

wavtmp = "/tmp/fakeboy"
try:
    mkdir(wavtmp)
except FileExistsError:
    pass

modspath = None

def log(*msg):
    logfile.write(" ".join([str(i) for i in msg]) + "\n")
    logfile.flush()

def run(cmd):
    return check_output(cmd, stderr=STDOUT, shell=True)

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
    msg = "loop " + "loops/" + loops[values[0]]
    send(msg)

def get_info(mod):
    info = run("xmp --load-only -C " + modspath + "/" + mod).decode("utf8")
    channels = int(re.findall("Channels\ +: (\d+)", info)[0])
    commentlines = re.findall("> (.*?)[\n$]", info)
    log(commentlines)
    comments = "\n".join(commentlines)
    return [channels, comments]

def make_mod_files(mod, info):
    for i in range(info[0]):
        log(run("xmp -S " + str(i) + " " + modspath + "/" + mod + " --nocmd -a 1 -o /tmp/fakeboy/" + str(i) + ".wav").decode("utf8"))

def exitform(F):
    F.editing = False

def makemodform(info, mod):
    F = MyForm(name=mod, minimum_columns=20, minimum_lines=20)
    #app.F = F
    c = F.add(npyscreen.Checkbox, value=False, name="play")
    c.whenToggled = lambda: send("play " + str(c.value and 1 or 0))
    ml = F.add(npyscreen.MultiLineEdit, value=info[1], max_height=10)
    quit = F.add(npyscreen.ButtonPress, name = "back", when_pressed_function = lambda: exitform(F))
    F.edit()

def start_mod(mods, mod, F):
    # extract the notes
    info = get_info(mod)
    log("Loading mod:", info)
    make_mod_files(mod, info)
    #F.editing = False
    #F.DISPLAY()
    send("reset")
    for i in range(info[0]):
        send("channel " + str(i) + " loop /tmp/fakeboy/" + str(i) + ".wav")
    makemodform(info, mod)

def makeform(app, selected=0):
        # These lines create the form and populate it with widgets.
        # A fairly complex screen in only 8 or so lines of code - a line for each control.
        F = MyForm(name = "fakeboy", minimum_columns=20, minimum_lines=20)
        app.F = F

        #F.add_handlers({curses.ascii.ESC: self.exit_application})
        #F.add_handlers({curses.ascii.TAB: self.exit_application})
        #F.add_handlers({"   ": self.exit_application})
        #F.add_handlers({27: self.exit_application})
        #F.add_handlers({"KEY_F(2)": self.exit_application})
        #F.add_handlers({"^Y": self.exit_application})
        #F.add_handlers({88: lambda: log("pressed X")})
        #F.add_handlers({89: lambda: log("pressed Y")})
        #log(F.handlers)
        #F.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE]  = self.exit_application

        #b  = F.add(npyscreen.ButtonPress, name = "COOL", when_pressed_function = lambda: app.exit_application())

        #t  = F.add(npyscreen.TitleText, name = "Text:",)
        #fn = F.add(npyscreen.TitleFilename, name = "Filename:")
        #fn2 = F.add(npyscreen.TitleFilenameCombo, name="Filename2:")
        #dt = F.add(npyscreen.TitleDateCombo, name = "Date:")
        #ml = F.add(npyscreen.MultiLineEdit, value="", max_height=5)

        F.add(npyscreen.FixedText, value="Mods:")

        mods = []
        mods = [m for m in listdir("mods") if splitext(m)[1] in [".it", ".xm", ".mod"]]

        ms = F.add(npyscreen.MultiLineAction, max_height=8, value = [], name="Mod", values = mods, scroll_exit=True)
        #ms.when_value_edited=lambda: start_mod(mods, ms.value, F)
        ms.actionHighlighted=lambda item,key: start_mod(mods, item, F)

        #s  = F.add(npyscreen.TitleSlider, out_of=4, name = "Volume", value=2)
        #s.when_value_edited=lambda: send("volume " + str(s.value))

        #s2  = F.add(npyscreen.TitleSlider, out_of=4, name = "Ticks", value=1)
        #s2.when_value_edited=lambda: send("divider " + str(pow(2, s2.value)))

        #ms1 = F.add(npyscreen.TitleMultiSelect, max_height =-2, value = [], name="Stick", values=["<-"], scroll_exit=True)
        #ms1.when_value_edited=lambda: send("sticky " + str(0 in ms1.value and 1 or 0))
        
        # skip a line
        #F.nextrely += 1

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
        log("after make form")
        #print(ms.get_selected_objects())

    def exit_application(self):
        log("EXIT APPLICATION")
        #curses.beep()
        #self.setNextForm(None)
        #self.NEXT_ACTIVE_FORM = None
        #self.editing = False
        send("reset")
        sleep(0.1)
        s.close()
        exit()

if __name__ == "__main__":
    if len(argv) != 2:
        print("Usage: main.py " + "path-to-mods")
    else:
        modspath = argv[1]
        App = TestApp()
        App.run()

