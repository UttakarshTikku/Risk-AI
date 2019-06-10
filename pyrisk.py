#!/usr/bin/env python3

import logging
import random
import importlib
import re
import collections
import curses
from game import Game
import csv

import configuration as conf
from world import CONNECT, MAP, KEY, AREAS

LOG = logging.getLogger("pyrisk")
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--nocurses", dest="curses", action="store_false", default=True, help="Disable the ncurses map display")
parser.add_argument("--nocolor", dest="color", action="store_false", default=True, help="Display the map without colors")
parser.add_argument("-l", "--log", action="store_true", default=False, help="Write game events to a logfile")
parser.add_argument("-d", "--delay", type=float, default=0.1, help="Delay in seconds after each action is displayed")
parser.add_argument("-s", "--seed", type=int, default=None, help="Random number generator seed")
parser.add_argument("-g", "--games", type=int, default=1, help="Number of rounds to play")
parser.add_argument("-w", "--wait", action="store_true", default=False, help="Pause and wait for a keypress after each action")
parser.add_argument("players", nargs="+", help="Names of the AI classes to use. May use 'ExampleAI*3' syntax.")
parser.add_argument("--deal", action="store_true", default=False, help="Deal territories rather than letting players choose")
parser.add_argument("-gs", "--gridsearch", type=bool, default=False, help="Grid Search Or Not")
parser.add_argument("-rec", "--recorder", type=bool, default=False, help="Turn Recording CSV Data On Or Off")

args = parser.parse_args()

NAMES_DEFAULT = ["ALPHA", "BRAVO","CHARLIE", "DELTA","ECHO", "FOXTROT"]
NAMES = []

conf.gridSearch = args.gridsearch
conf.recorder_ON = args.recorder

LOG.setLevel(logging.DEBUG)
if args.log:
    logging.basicConfig(filename="pyrisk.log", filemode="w")
elif not args.curses:
    logging.basicConfig()

if args.seed is not None:
    random.seed(args.seed)
player_name_dict = {}
player_classes = []
for p in args.players:
    match = re.match(r"(\w+)?(\*\d+)?", p)
    if match:
        #import mechanism
        #we expect a particular filename->classname mapping such that
        #ExampleAI resides in ai/example.py, FooAI in ai/foo.py etc.
        name = match.group(1)
        deception_mode = 0
        if 'Deceptive' in name:
            name = name.replace('Deceptive','')
            name = name.replace('AI','')
            if not name == '':
                deception_mode = int(name)
            name = 'DeceptiveAI'
        player_name = p.split(':')
        if len(player_name) > 1:
            NAMES.append(player_name[1])
            conf.deception_modes.append((player_name[1], deception_mode))
            player_name_dict[player_name[1]] = match.group(1)
        package = name[:-2].lower()
        if match.group(2):
            count = int(match.group(2)[1:])
        else:
            count = 1
        try:
            klass = getattr(importlib.import_module("ai."+package), name)
            for i in range(count):
                player_classes.append(klass)
        except:
            print("Unable to import AI %s from ai/%s.py" % (name, package))
            raise

if len(NAMES) == 0:
    NAMES = NAMES_DEFAULT

kwargs = dict(curses=args.curses, color=args.color, delay=args.delay,
              connect=CONNECT, cmap=MAP, ckey=KEY, areas=AREAS, wait=args.wait, deal=args.deal)
def wrapper(stdscr, **kwargs):
    g = Game(screen=stdscr, **kwargs)
    for i, klass in enumerate(player_classes):
        g.add_player(NAMES[i], klass)
    return g.play()
        
wins = collections.defaultdict(int)
wins_player_name = collections.defaultdict(int)
filename = ""
for p in args.players:
    wins_player_name[p.split(':')[0]+"_"+p.split(':')[1]] = 0
    if filename == "":
        filename += p.split(':')[0]
    else:
        filename = filename + "vs" + p.split(':')[0]
recorder = open('./'+filename+'.csv','a')
with recorder:
    od=collections.OrderedDict(sorted(wins_player_name.items()))
    writer = csv.DictWriter(recorder,od.keys())
    writer.writerow({k:k for k,v in od.items()})
    writer.writerow(od)
for j in range(args.games):
    kwargs['round'] = (j+1, args.games)
    kwargs['history'] = wins
    if args.curses:
        victor = curses.wrapper(wrapper, **kwargs)
    else:
        victor = wrapper(None, **kwargs)
    wins[victor] += 1
    # wins_player_name[player_classes[NAMES.index(victor)].__name__+"_"+victor] += 1
    print(player_name_dict[victor]+"_"+victor)
    wins_player_name[player_name_dict[victor]+"_"+victor] += 1
    recorder = open('./'+filename+'.csv','a')
    with recorder:
        od=collections.OrderedDict(sorted(wins_player_name.items()))
        writer = csv.DictWriter(recorder,od.keys())
        writer.writerow(od)
print("Outcome of %s games" % args.games)
for k in sorted(wins, key=lambda x: wins[x]):
    print("%s [%s]:\t%s" % (k, player_classes[NAMES.index(k)].__name__, wins[k]))

