from zipfile import ZipFile
from os.path import basename, join
from shutil import copyfileobj
import construct as c

import pyflp

def flp_get_info(flpfile):
    try:
        project = pyflp.parse(flpfile)
    except ValueError:
        flp_monkeypatch_pyflp()
        project = pyflp.parse(flpfile)
    channelnames = {}
    for c in project.channels:
        i = c.insert - 1
        if i >= 0 and not channelnames.get(i):
            channelnames[i] = project.mixer[c.insert].name or c.name
    info = {"channelnames": channelnames}
    info["channelcount"] = len(info["channelnames"])
    return info

def flp_extract_stems(fruityzip, tmpdir, chan_count):
    with ZipFile(fruityzip, 'r') as zip_ref:
        for c in range(chan_count):
            for member in zip_ref.namelist():
                if member.endswith("_Insert " + str(c + 1) + ".wav"):
                    filename = basename(member)
                    source = zip_ref.open(member)
                    targetfile = join(tmpdir, str(c) + ".wav")
                    target = open(targetfile, "wb")
                    with source, target:
                        copyfileobj(source, target)

def flp_extract(fruityzip, tmpdir):
    with ZipFile(fruityzip, 'r') as zip_ref:
        for member in zip_ref.namelist():
            if member.endswith(".flp"):
                filename = basename(member)
                source = zip_ref.open(member)
                targetfile = join(tmpdir, filename)
                target = open(targetfile, "wb")
                with source, target:
                    copyfileobj(source, target)
                return targetfile

def flp_monkeypatch_pyflp():
    from pyflp.channel import StdEnum, _DelayFlags, ArpDirection, DeclickMode, List2Tuple, LinearMusical, StretchMode, Log2, LogNormal
    pyflp.channel.ParametersEvent.STRUCT = c.Struct(
        "_u1" / c.Optional(c.Bytes(9)),  # 9
        "fx.remove_dc" / c.Optional(c.Flag),  # 10
        "delay.flags" / c.Optional(StdEnum[_DelayFlags](c.Int8ul)),  # 11
        "keyboard.main_pitch" / c.Optional(c.Flag),  # 12
        "_u2" / c.Optional(c.Bytes(28)),  # 40
        "arp.direction" / c.Optional(StdEnum[ArpDirection](c.Int32ul)),  # 44
        "arp.range" / c.Optional(c.Int32ul),  # 48
        "arp.chord" / c.Optional(c.Int32ul),  # 52
        "arp.time" / c.Optional(c.Float32l),  # 56
        "arp.gate" / c.Optional(c.Float32l),  # 60
        "arp.slide" / c.Optional(c.Flag),  # 61
        "_u3" / c.Optional(c.Bytes(1)),  # 62
        "time.full_porta" / c.Optional(c.Flag),  # 63
        "keyboard.add_root" / c.Optional(c.Flag),  # 64
        "time.gate" / c.Optional(c.Int16ul),  # 66
        "_u4" / c.Optional(c.Bytes(2)),  # 68
        "keyboard.key_region" / c.Optional(List2Tuple(c.Int32ul[2])),  # 76
        "_u5" / c.Optional(c.Bytes(4)),  # 80
        "fx.normalize" / c.Optional(c.Flag),  # 81
        "fx.inverted" / c.Optional(c.Flag),  # 82
        "_u6" / c.Optional(c.Bytes(1)),  # 83
        "content.declick_mode" / c.Optional(StdEnum[DeclickMode](c.Int8ul)),  # 84
        "fx.crossfade" / c.Optional(c.Int32ul),  # 88
        "fx.trim" / c.Optional(c.Int32ul),  # 92
        "arp.repeat" / c.Optional(c.Int32ul),  # 96; FL 4.5.2+
        "stretching.time" / c.Optional(LinearMusical(c.Int32ul)),  # 100
        "stretching.pitch" / c.Optional(c.Int32sl),  # 104
        "stretching.multiplier" / c.Optional(Log2(c.Int32sl, 10000)),  # 108
        "stretching.mode" / c.Optional(StdEnum[StretchMode](c.Int32sl)),  # 112
        "_u7" / c.Optional(c.Bytes(21)),  # 133
        #"fx.start" / c.Optional(LogNormal(c.Int16ul[2], (0, 61440))),  # 137
        "fx.start" / c.Optional(c.Int32ul),  # 137
        "_u8" / c.Optional(c.Bytes(4)),  # 141
        "fx.length" / c.Optional(LogNormal(c.Int16ul[2], (0, 61440))),  # 145
        "_u9" / c.Optional(c.Bytes(3)),  # 148
        "playback.start_offset" / c.Optional(c.Int32ul),  # 152
        "_u10" / c.Optional(c.Bytes(5)),  # 157
        "fx.fix_trim" / c.Optional(c.Flag),  # 158 (FL 20.8.4 max)
        "_extra" / c.GreedyBytes,  # * 168 as of 20.9.1
    )

if __name__ == "__main__":
    from sys import argv
    from pprint import pprint
    if not argv[-1].endswith(".flp"):
        print("Usage: fruity.py FILENAME.flp")
    else:
        flpfile = argv[-1]
        print("Opening", flpfile)
        try:
            project = pyflp.parse(flpfile)
        except ValueError:
            flp_monkeypatch_pyflp()
            project = pyflp.parse(flpfile)
        #for c in project.channels:
        #    print(c)
        #    print(c.automations)
        print("Fruity loops version:", project.version)
        inserts = {}

        for c in project.channels:
            print(type(c), c.iid, c.name, c.insert)

        insertmap = {}
        channelnames = {}
        for c in project.channels:
            if not insertmap.get(c.insert):
                insertmap[c.insert] = []
            insertmap[c.insert].append(c.name)
            i = c.insert - 1
            if i >= 0 and not channelnames.get(i):
                channelnames[i] = project.mixer[c.insert].name or c.name

        #insertmap = [(c.insert, c.name) for c in project.channels]
        #insertnames = [i.name for i in project.mixer]
        #channelnames = [c.name for c in project.channels]
        #pprint(channelnames)

        #for c in sorted(insertmap.keys()):
        #    print(c, insertmap[c])

        for c in range(len(channelnames)):
            print(c, channelnames[c])

        #pprint([c.name for c in project.channels])
#         for m in project.mixer:
            # print(m)
            # for s in m:
                # try:
                    # print("\t", s)
                # except:
                    # pass
        #for c in project.channels:
        #    print(c)
        #    print(c.insert)
        #pprint([c for c in project.channels])
        #pprint([c.name for c in project.channels])
