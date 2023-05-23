#!/usr/bin/env python
# encoding: utf-8
import curses
import re
from sys import exit, argv
from os import listdir
from os.path import splitext
from time import sleep
from subprocess import check_output, STDOUT
import struct
import npyscreen
from common import MyForm, send, log, s, wavtmp, modspath
from player import make_mod_form

def run(cmd):
    return check_output(cmd, stderr=STDOUT, shell=True)

def make_mod_files(mod, channels):
    for i in range(channels):
        log(run("xmp -S " + str(i) + " " + modspath + "/" + mod + " --nocmd -m -a 1 -o " + wavtmp + "/" + str(i) + ".wav").decode("utf8"))

def get_mod_info(mod):
    info = run("xmp --load-only -C " + modspath + "/" + mod).decode("utf8")
    channels = int(re.findall("Channels\ +: (\d+)", info)[0])
    commentlines = re.findall("> (.*?)[\n$]", info)
    log(commentlines)
    comments = "\n".join(commentlines)
    return [channels, comments]

def get_mod_channel_names(mod, channels):
    data = open(modspath + "/" + mod, "rb").read()
    try:
        i = data.index(bytearray("CNAM", "utf8"))
    except:
        i = None
    if i:
        chancount = int(struct.unpack('<I',data[i+4:i+8])[0] / 20)
    else:
        chancount = channels
    return [data[i+n*20+8:i+n*20+28].decode("utf8").rstrip('\0') if i else "ch " + str(n)
            for n in range(chancount)]

def start_mod(mods, mod, F):
    # extract the notes
    info = get_mod_info(mod)
    info.append(get_mod_channel_names(mod, info[0]))
    chan_count = min(len(info[2]), 8)
    log("Loading mod:", info)
    npyscreen.blank_terminal()
    npyscreen.notify("rendering " + str(chan_count) + " channels", title='Rendering')
    make_mod_files(mod, chan_count)
    #F.editing = False
    #F.DISPLAY()
    send("reset")
    for i in range(chan_count):
        send("channel " + str(i) + " loop " + wavtmp + "/" + str(i) + ".wav")
    make_mod_form(info, mod)

def make_mod_list_form(app, selected=0):
    F = MyForm(name = "fakeboy", columns=52, lines=20)
    app.F = F

    quit = F.add(npyscreen.ButtonPress, name = "quit", when_pressed_function = lambda: app.exit_application(), relx=-12)

    F.add(npyscreen.FixedText, value="Mods:", editable=False)

    mods = []
    mods = [m for m in listdir("mods") if splitext(m)[1] in [".it", ".xm", ".mod", ".mptm"]]

    ms = F.add(npyscreen.MultiLineAction, max_height=14, value = [], name="Mod", values = mods, scroll_exit=True)
    ms.actionHighlighted=lambda item,key: start_mod(mods, item, F)

    F.edit()

class TestApp(npyscreen.NPSApp):
    def main(self):
        make_mod_list_form(self)
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

