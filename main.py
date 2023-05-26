#!/usr/bin/env python
# encoding: utf-8
import curses
import re
from sys import exit, argv
from os import listdir, makedirs
from os.path import splitext
from time import sleep
from subprocess import check_output, STDOUT
import struct
import npyscreen
from common import MyForm, send, log, s
from player import make_mod_form
from modrender import mod_get_info, mod_make_stems

def start_mod(modspath, mods, mod, F):
    # extract the notes
    info = mod_get_info(modspath + "/" + mod)
    log("Loading mod:", info)
    chan_count = min(info["channelcount"], 8)
    npyscreen.blank_terminal()
    npyscreen.notify("rendering " + str(chan_count) + " channels", title='Rendering')
    wavtmpdir = "/tmp/fakeboy/" + mod
    makedirs(wavtmpdir, exist_ok=True)
    mod_make_stems(modspath + "/" + mod, wavtmpdir, chan_count)
    #F.editing = False
    #F.DISPLAY()
    send("reset")
    for i in range(chan_count):
        send("channel " + str(i) + " loop " + wavtmpdir + "/" + str(i) + ".wav")
    make_mod_form(info, mod)

def make_mod_list_form(app, modspath):
    F = MyForm(name = "modbay", columns=52, lines=20)
    app.F = F

    quit = F.add(npyscreen.ButtonPress, name = "quit", when_pressed_function = lambda: app.exit_application(), relx=-12)

    F.add(npyscreen.FixedText, value="Mods:", editable=False)

    mods = []
    mods = [m for m in listdir("mods") if splitext(m)[1] in [".it", ".xm", ".mod", ".mptm"]]

    ms = F.add(npyscreen.MultiLineAction, max_height=14, value = [], name="Mod", values = mods, scroll_exit=True)
    ms.actionHighlighted=lambda item,key: start_mod(modspath, mods, item, F)

    F.edit()

class TestApp(npyscreen.NPSApp):
    modspath = None

    def __init__(self, modspath, *args, **kwargs):
        self.modspath = modspath
        npyscreen.NPSApp.__init__(self, *args, **kwargs)

    def main(self):
        make_mod_list_form(self, self.modspath)
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
        App = TestApp(argv[1])
        App.run()

