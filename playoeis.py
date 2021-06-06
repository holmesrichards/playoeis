#!/usr/bin/python3

"""Python script to play an OEIS sequence as a MIDI sequence.

Takes MIDI note messages from an input device (e.g. Keystep), substitutes
new note values based on an OEIS entry, and sends result to an output device
(e.g. synth).

Usage:

playoeis.py [args] [entry]

entry is OEIS entry ID, e.g. A123456. Omittable and ignored if --search arg 
is used.

args are:

--loop           Loop through sequence forever (until terminated)
--noloop         Play sequence once (default)
--search string  Search OEIS with the given string as search term and use
                 first result returned, ignore entry if given
--iport string   Use input port with this name, else use system default
--oport string   Use output port with this name, else use system default
--nstep n        In --loop mode reset loop index every n steps. In --noloop
                 mode play maximum of n steps. Default is length of data file.
--pmod n         OEIS entries are reduced modulo n (default 88)
--poff n         Notes are offset by n (default 0)
                 (Note results of modulo and offset are then reduced modulo 128)
--rest xx        Interpret data values as rests: xx = n negatives, z zeros, 
                 p positives, nz nonnegatives, etc.
--verbose        Print diagnostics

Author: Rich Holmes
Repo: https://github.com/holmesrichards/playoeis
License: Creative Commons Zero v1.0 Universal
"""

import mido
import oeispy as op
import requests
import re
from sys import argv

def playdata (dataa, pmod=88, poff=0, loop=False, inportname="", outportname="", nstep="999", rest=""):
    """Play the data in the list dataa.
    Note played is list entry mod pmod offset by poff.
    These notes are substituted for notes coming from input port
    named inportname, and are sent to output port named outportname.
    (Specifically, when a noteon is seen, noteoffs for any on notes are
    sent, and then noteon with dataa value. When a noteoff is seen,
    noteoffs for any on notes are sent. This seems the best way to handle
    multiple input notes mapping to same output note.)
    If loop is True, loop forever until terminated; reset loop index every 
    nstep steps. If loop is False, play up to n steps and return.
    If rest contains n, p, and/or z, then negative, positive, and/or zero
    data values are interpreted as rests.
    """
    
    if inportname=="":
        inport = mido.open_input()
    else:
        inport = mido.open_input(inportname)
    if outportname=="":
        outport = mido.open_output()
    else:
        outport = mido.open_output(outportname)

    index = 0
    if not loop and nstep > len(dataa):
        nstep = len(dataa)
        
    noteson = {}
    nnn = 0
    try:
        for msg in inport:
            if msg.type == 'note_on':
                for n in noteson:
                    outport.send (mido.Message('note_off', note=noteson[n]))
                noteson.clear()
                n = msg.note
                if not ((dataa[index] < 0 and 'n' in rest) or \
                        (dataa[index] == 0 and 'z' in rest) or \
                        (dataa[index] > 0 and 'p' in rest)):
                    nn = (dataa[index]%pmod+poff)%128
                    outport.send (msg.copy(note=nn))
                    noteson[n] = nn

                if nnn == nstep-1:
                    if loop:
                        index = len(dataa)-1
                        nnn = 0
                    else:
                        break
                else:
                    nnn += 1

                if index == len(dataa)-1:
                    index = 0
                else:
                    index += 1                    
            elif msg.type == 'note_off':
                for n in noteson:
                    outport.send (mido.Message('note_off', note=noteson[n]))
                noteson.clear()
            else:
                outport.send (msg)
    except:
        pass
    
    for n in noteson:
        outport.send (mido.Message('note_off', note=noteson[n]))
    inport.close()
    outport.close()
    
def main():

    entry = ""
    vloop = False
    sstring = ""
    vinportname = ""
    voutportname = ""
    vrest = ""
    vnstep = 0
    vpmod = 88
    vpoff = 24
    verbose = False
    i = 1
    try:
        while i < len(argv):
            if argv[i] == '--loop':
                vloop = True
            elif argv[i] == '--noloop':
                vloop = False
            elif argv[i] == '--search':
                i += 1
                sstring = argv[i]
            elif argv[i] == '--iport':
                i += 1
                vinportname = argv[i]
            elif argv[i] == '--oport':
                i += 1
                voutportname = argv[i]
            elif argv[i] == '--nstep':
                i += 1
                vnstep = int(argv[i])
            elif argv[i] == '--pmod':
                i += 1
                vpmod = int(argv[i])
            elif argv[i] == '--poff':
                i += 1
                vpoff = int(argv[i])
            elif argv[i] == '--rest':
                i += 1
                vrest = argv[i]
            elif argv[i] == '--verbose':
                verbose = True
            elif i == len(argv)-1:
                entry = argv[i]
            else:
                print ("Usage... at", argv[i:])
                return
            i += 1
    except:
        print ("Usage... exception")
        return

    if sstring == "" and entry == "":
        print ("Usage... need --search or entry id")
        return
    
    if not sstring:
        sstring = "id:"+entry
    try:
        if verbose:
            print ("Search for:", sstring)
        res = op.resultEois(sstring)
    except:
        print ("Search failed for", sstring)
        return

    if verbose:
        print ("Results (first one used):")
        for r in res:
            print ("A{:06d}".format(op.getNumber(r)), op.getName(r))

    no = op.getNumber(res[0])
    url = 'https://oeis.org/A{:06d}/b{:06d}.txt'.format (no, no)
    try:
        if verbose:
            print ("Getting data from", url)
        data = requests.get(url).text
    except:
        print ("Failed to get", url)
        return

    dataa = []
    for line in data.splitlines():
        if line and not re.match('#', line):
            dataa.append(int(line.split()[1]))

    if verbose:
        print ("Data starts with", dataa[0:10])

    if vnstep == 0:
        vnstep = len(dataa)
        
    playdata (dataa,
              loop=vloop,
              inportname=vinportname,
              outportname=voutportname,
              nstep=vnstep,
              pmod=vpmod,
              poff=vpoff,
              rest=vrest)

if __name__ == "__main__":
    main()
