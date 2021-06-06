# playoeis

Python script to play an OEIS sequence as a MIDI sequence.

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
--pmod n         OEIS entries are reduced modulo n (default 88)
--poff n         Notes are offset by n (default 24)
                 (Note results of modulo and offset are then reduced modulo 128)
--rest xx        Interpret data values as rests: xx = n negatives, z zeros, 
                 p positives, nz nonnegatives, etc.
--verbose        Print diagnostics

Uses libraries: mido, oeispy, requests, re, sys
