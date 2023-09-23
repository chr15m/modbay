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
