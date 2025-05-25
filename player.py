import random
import curses
import npyscreen
import json
import os

from common import MyForm, send, log

class MyGrid(npyscreen.GridColTitles):
    #def custom_print_cell(self, actual_cell, cell_display_value):
    #    if cell_display_value == 'FAIL':
    #       actual_cell.color = 'DANGER'
    #    elif cell_display_value == 'PASS':
    #       actual_cell.color = 'GOOD'
    #    else:
    #       actual_cell.color = 'DEFAULT'

    def set_up_handlers(self):
        log("MyGrid.set_up_handlers")
        npyscreen.GridColTitles.set_up_handlers(self)

def exit_form(F, statefilepath):
    F.editing = False

def make_sender(el, c, key, conv):
    def x():
        send("channel " + str(c) + " " + key + " " + conv(el.value))
    return x

def handle_edges(original_handler, k, edit_cell, limit, alt_handler):
    log("pressed", k, edit_cell, limit)
    if edit_cell[0] == limit:
        alt_handler(k)
    else:
        original_handler(k)

def update_value(values, edit_cell, value):
    values[edit_cell[0]][edit_cell[1]] = value

def grid_interact(k, edit_cell, values, statefile, channel_names):
    value = values[edit_cell[0]][edit_cell[1]]
    channel = edit_cell[0]
    channel_name = channel_names.get(channel, "ch " + str(channel))

    # Create state dictionary if it doesn't exist
    if not hasattr(grid_interact, 'state_dict'):
        grid_interact.state_dict = {}

    # Initialize channel in state dict if needed
    if channel_name not in grid_interact.state_dict:
        grid_interact.state_dict[channel_name] = {"on": "off", "pan": "left"}

    # handle on/off
    if edit_cell[1] == 1:
        new_value = "off" if value == "on" else "on"
        update_value(values, edit_cell, new_value)
        grid_interact.state_dict[channel_name]["on"] = new_value
        send("channel " + str(channel) + " volume " + str(4 if new_value == "on" else 0))
    # handle pan
    if edit_cell[1] == 2:
        new_value = "left" if value == "right" else "right"
        update_value(values, edit_cell, new_value)
        grid_interact.state_dict[channel_name]["pan"] = new_value
        send("channel " + str(channel) + " pan " + str(1 if new_value == "right" else 0))

    # update the statefile - rewrite the entire file
    with open(statefile, 'w') as f:
        json.dump(grid_interact.state_dict, f)

def make_mod_form(info, mod, statefilepath):
    channel_names = info["channelnames"]
    channel_count = info["channelcount"]
    F = MyForm(name=mod, minimum_columns=20, minimum_lines=20)

    # Reset the state dictionary
    if hasattr(grid_interact, 'state_dict'):
        delattr(grid_interact, 'state_dict')

    # Load existing state if available
    saved_state = {}
    if os.path.exists(statefilepath):
        try:
            with open(statefilepath, 'r') as f:
                saved_state = json.load(f)
            log("Loaded saved state from " + statefilepath)
        except Exception as e:
            log("Error loading state: " + str(e))

    quit = F.add(npyscreen.ButtonPress, name = "back", when_pressed_function = lambda: exit_form(F, statefilepath), relx=-12)

    play = F.add(npyscreen.Checkbox, value=False, name="play")
    play.whenToggled = lambda: send("play " + str(play.value and 1 or 0))

    #s2  = F.add(npyscreen.TitleSlider, out_of=1, name = "Sync rate", value=0)
    #s2.when_value_edited=lambda: send("sync-div " + str(pow(2, s2.value)))
    F.nextrely += 1

    # channels grid
    gd = F.add(MyGrid, col_titles=["", "on", "pan"])
    #gd.when_value_edited = lambda: log("value edited", gd.edit_cell)
    #gd.when_cursor_moved = lambda: log("cursor moved", gd.edit_cell)
    gd.handlers.update({curses.ascii.SP: lambda k: grid_interact(k, gd.edit_cell, gd.values, statefilepath, channel_names)})
    # rebind up down keys to check if they go out of range
    handler_259 = gd.handlers[259]
    gd.handlers[259] = lambda k: handle_edges(handler_259, k, gd.edit_cell, 0, gd.handlers[353]) # up
    handler_258 = gd.handlers[258]
    gd.handlers[258] = lambda k: handle_edges(handler_258, k, gd.edit_cell, channel_count - 1, gd.handlers[9]) # down
    log(gd.handlers)

    gd.values = []
    for y in range(channel_count):
        row = []
        channel_name = channel_names.get(y, "ch " + str(y))
        row.append(channel_name)

        # Apply saved state if available for this channel
        if channel_name in saved_state:
            on_state = saved_state[channel_name].get("on", "off")
            pan_state = saved_state[channel_name].get("pan", "left")
            row.append(on_state)
            row.append(pan_state)

            # Apply the saved state to the actual audio
            if on_state == "on":
                send("channel " + str(y) + " volume 4")
            if pan_state == "right":
                send("channel " + str(y) + " pan 1")
        else:
            row.append("off")
            row.append("left")

        gd.values.append(row)

    #for c in range(info[0]):
    #    on = F.add(npyscreen.Checkbox, value=True, name="ch " + str(c), max_width=15)
    #    on.whenToggled = make_sender(on, c, "volume", lambda v: str((v and 4 or 0) / 4.0))
    #    F.nextrely += -1
    #    pan = F.add(npyscreen.Checkbox, value=True, name="left " + str(c), relx=20, max_width=20)
    #    pan.whenToggled = make_sender(pan, c, "pan", lambda v: str(v and 1 or 0))
    #F.nextrely += 1

    #ml = F.add(npyscreen.MultiLineEdit, value=info[1], max_height=10, editable=False)

    F.edit()
