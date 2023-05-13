import random
import curses
import npyscreen

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

def exit_form(F):
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

def grid_interact(k, edit_cell, values):
    value = values[edit_cell[0]][edit_cell[1]]
    channel = edit_cell[0]
    # handle on/off
    if edit_cell[1] == 1:
        new_value = "off" if value == "on" else "on"
        update_value(values, edit_cell, new_value)
        send("channel " + str(channel) + " volume " + str(4 if new_value == "on" else 0))
    # handle pan
    if edit_cell[1] == 2:
        new_value = "left" if value == "right" else "right"
        update_value(values, edit_cell, new_value)
        send("channel " + str(channel) + " pan " + str(1 if new_value == "right" else 0))

def make_mod_form(info, mod):
    channel_names = info[2]
    F = MyForm(name=mod, minimum_columns=20, minimum_lines=20)

    quit = F.add(npyscreen.ButtonPress, name = "back", when_pressed_function = lambda: exit_form(F), relx=-12)

    play = F.add(npyscreen.Checkbox, value=False, name="play")
    play.whenToggled = lambda: send("play " + str(play.value and 1 or 0))

    #s2  = F.add(npyscreen.TitleSlider, out_of=1, name = "Sync rate", value=0)
    #s2.when_value_edited=lambda: send("sync-div " + str(pow(2, s2.value)))
    F.nextrely += 1

    # channels grid

    gd = F.add(MyGrid, col_titles=["", "on", "pan"])
    #gd.when_value_edited = lambda: log("value edited", gd.edit_cell)
    #gd.when_cursor_moved = lambda: log("cursor moved", gd.edit_cell)
    gd.handlers.update({curses.ascii.SP: lambda k: grid_interact(k, gd.edit_cell, gd.values)})
    # rebind up down keys to check if they go out of range
    handler_259 = gd.handlers[259]
    gd.handlers[259] = lambda k: handle_edges(handler_259, k, gd.edit_cell, 0, gd.handlers[353]) # up
    handler_258 = gd.handlers[258]
    gd.handlers[258] = lambda k: handle_edges(handler_258, k, gd.edit_cell, len(channel_names) - 1, gd.handlers[9]) # down
    log(gd.handlers)

    gd.values = []
    for y in range(len(channel_names)):
        row = []
        row.append(channel_names[y])
        row.append("off")
        row.append("right")
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
