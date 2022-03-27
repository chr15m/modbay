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
        log(run("xmp -S " + str(i) + " " + modspath + "/" + mod + " --nocmd -m -a 1 -o /tmp/fakeboy/" + str(i) + ".wav").decode("utf8"))

def exitform(F):
    F.editing = False

def makesender(el, c, key, conv):
    def x():
        send("channel " + str(c) + " " + key + " " + conv(el.value))
    return x

def makemodform(info, mod):
    F = MyForm(name=mod, minimum_columns=20, minimum_lines=20)
    play = F.add(npyscreen.Checkbox, value=False, name="play")
    play.whenToggled = lambda: send("play " + str(play.value and 1 or 0))

    s2  = F.add(npyscreen.TitleSlider, out_of=1, name = "Sync rate", value=0)
    s2.when_value_edited=lambda: send("sync-div " + str(pow(2, s2.value)))
    F.nextrely += 1

    for c in range(info[0]):
        on = F.add(npyscreen.Checkbox, value=True, name="ch " + str(c), max_width=15)
        on.whenToggled = makesender(on, c, "volume", lambda v: str(v and 4 or 0))
        F.nextrely += -1
        pan = F.add(npyscreen.Checkbox, value=True, name="left " + str(c), relx=20, max_width=20)
        pan.whenToggled = makesender(pan, c, "pan", lambda v: str(v and 1 or 0))
    F.nextrely += 1

    ml = F.add(npyscreen.MultiLineEdit, value=info[1], max_height=10, editable=False)

    quit = F.add(npyscreen.ButtonPress, name = "back", when_pressed_function = lambda: exitform(F), rely=-3, relx=-12)

    F.edit()

def start_mod(mods, mod, F):
    # extract the notes
    info = get_info(mod)
    log("Loading mod:", info)
    npyscreen.blank_terminal()
    npyscreen.notify("rendering " + str(info[0]) + " channels", title='Rendering')
    make_mod_files(mod, info)
    #F.editing = False
    #F.DISPLAY()
    send("reset")
    for i in range(info[0]):
        send("channel " + str(i) + " loop /tmp/fakeboy/" + str(i) + ".wav")
    makemodform(info, mod)

def makeform(app, selected=0):
        F = MyForm(name = "fakeboy", minimum_columns=20, minimum_lines=20)
        app.F = F

        F.add(npyscreen.FixedText, value="Mods:", editable=False)

        mods = []
        mods = [m for m in listdir("mods") if splitext(m)[1] in [".it", ".xm", ".mod"]]

        ms = F.add(npyscreen.MultiLineAction, max_height=8, value = [], name="Mod", values = mods, scroll_exit=True)
        ms.actionHighlighted=lambda item,key: start_mod(mods, item, F)

        quit = F.add(npyscreen.ButtonPress, name = "quit", when_pressed_function = lambda: app.exit_application(), rely=-3, relx=-12)

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

