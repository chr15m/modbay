#!/usr/bin/env python
# encoding: utf-8
import curses
import re
from sys import exit, argv
from os import listdir, makedirs
from os.path import splitext, exists, isdir, join, abspath
from time import sleep
from datetime import datetime
from subprocess import check_output, STDOUT
import struct
import npyscreen
import hashlib
from common import MyForm, notify, send, log, s
from player import make_mod_form
from modrender import mod_get_info, mod_make_stems
from fruity import flp_extract, flp_get_info, flp_extract_stems

MAX_CHANNELS = 16

def get_file_hash(filepath):
    """Generate a hash for a file to use as a cache key"""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read(65536)  # Read in 64k chunks
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()[:8]

def start_mod(modspath, mods, mod, F):
    # Create the base rendered directory if it doesn't exist
    makedirs("./tmp/rendered", exist_ok=True)

    # Get the full path to the mod file
    mod_path = join(modspath, mod)

    # Generate a hash of the mod file to use as the cache key
    file_hash = get_file_hash(mod_path)
    log("File hash for " + mod + ": " + file_hash)

    # Create a slug from the filename to avoid issues with spaces and special chars
    slug = re.sub(r'[^a-zA-Z0-9.-]', '_', splitext(mod)[0])

    # Set the output directory based on the hash
    tmpdir = join("./tmp/rendered/", slug + "-" + file_hash)

    # Check if we already have rendered this mod
    already_rendered = exists(tmpdir) and isdir(tmpdir)

    if not already_rendered:
        log("Rendering " + mod + " to " + tmpdir)
        makedirs(tmpdir, exist_ok=True)

        if mod.endswith(".zip"):
            fruityzip = mod_path
            notify("extracting flp", title='Extract')
            flpfile = flp_extract(fruityzip, tmpdir)
            log("Loading flp:", flpfile)
            notify("loading flp", title='Load')
            info = flp_get_info(flpfile)
            log("Flp info:", info)
            notify("unpack stems", title='Unpack')
            chan_count = min(info["channelcount"], MAX_CHANNELS)
            flp_extract_stems(fruityzip, tmpdir, chan_count)
        else:
            # extract the notes
            info = mod_get_info(mod_path)
            log("Loading mod:", info)
            chan_count = min(info["channelcount"], MAX_CHANNELS)
            npyscreen.blank_terminal()
            notify("rendering " + str(chan_count) + " channels", title='Rendering')
            mod_make_stems(mod_path, tmpdir, chan_count)
    else:
        log("Using cached render for " + mod + " at " + tmpdir)
        if mod.endswith(".zip"):
            flpfile = join(tmpdir, "project.flp")  # Assuming this is where flp_extract puts it
            info = flp_get_info(flpfile)
        else:
            info = mod_get_info(mod_path)

        chan_count = min(info["channelcount"], MAX_CHANNELS)

    send("reset")
    for i in range(chan_count):
        send("channel " + str(i) + " loop " + join(tmpdir, str(i) + ".wav"))
    make_mod_form(info, mod, join(modspath, mod + "-modbay-state.json"))

def make_mod_list_form(app, modspath):
    F = MyForm(name = "modbay", columns=52, lines=20)
    app.F = F

    quit = F.add(npyscreen.ButtonPress, name = "quit", when_pressed_function = lambda: app.exit_application(), relx=-12)

    F.add(npyscreen.FixedText, value="Mods:", editable=False)

    ms = F.add(npyscreen.MultiLineAction, max_height=14, value = [], name="Mod", values = [], scroll_exit=True)

    current_path = abspath(modspath)

    def get_listings(cpath):
        items = listdir(cpath)
        dirs = sorted([d for d in items if isdir(join(cpath, d)) and not d.startswith('.')])
        mods = sorted([m for m in items if splitext(m)[1] in [".it", ".xm", ".mod", ".mptm", ".zip"]])

        listings = []
        # Note: app.modspath is the root mods directory.
        if abspath(cpath) != abspath(app.modspath):
             listings.append("[..]")

        listings.extend(["[" + d + "]" for d in dirs])
        listings.extend(mods)
        return listings

    def on_select(item, key):
        nonlocal current_path

        if item.startswith('[') and item.endswith(']'):
            dirname = item[1:-1]
            current_path = abspath(join(current_path, dirname))
            ms.values = get_listings(current_path)
            ms.display()
        else:
            # It's a mod file
            start_mod(current_path, None, item, F)

    ms.values = get_listings(current_path)
    ms.actionHighlighted=on_select

    F.edit()

class ModbayApp(npyscreen.NPSApp):
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
        log("Starting modbay.")
        log(str(datetime.now()))
        # Create tmp directory if it doesn't exist
        makedirs("./tmp", exist_ok=True)
        App = ModbayApp(argv[1])
        App.run()

