import socket
from os import mkdir
import npyscreen

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
s.connect(("127.0.0.1", 1232))

logfile = open("log", "a")

def log(*msg):
    logfile.write(" ".join([str(i) for i in msg]) + "\n")
    logfile.flush()

class MyForm(npyscreen.FormBaseNew):
    def while_editing(form, thing):
        log("while_editing", thing)

    def adjust_widgets(x):
        log("adjust", x)

# notify code is from npyscreen original but tweaked:
# https://github.com/npcole/npyscreen/blob/master/npyscreen/utilNotify.py#L30

class Popup(npyscreen.fmForm.Form):
    DEFAULT_LINES      = 12
    DEFAULT_COLUMNS    = 40
    SHOW_ATX           = 6
    SHOW_ATY           = 3

def notify(message, title="Message", form_color='STANDOUT', wrap=True):
    message = npyscreen.utilNotify._prepare_message(message)
    F   = Popup(name=title, color=form_color)
    F.preserve_selected_widget = True
    mlw = F.add(npyscreen.wgmultiline.Pager,)
    mlw_width = mlw.width-1
    if wrap:
        message = npyscreen.utilNotify._wrap_message_lines(message, mlw_width)
    mlw.values = message
    F.display()

def test_func(k, ml):
    #log("key test_func", args)
    ml.value += " " + str(k)
    ml.display()
    return False

def send(msg):
    msg = msg + ";\n"
    log(msg)
    try:
        s.send(msg.encode("utf8"))
    except ConnectionRefusedError:
        log("Failed to send UDP packet.")
