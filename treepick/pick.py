import os
import cgitb
import curses
import pdb
import readline
import sys
from .paths import Paths
from .keys import parse

# Get more detailed traceback reports
cgitb.enable(format="text")  # https://pymotw.com/2/cgitb/


def draw(parent, action, curline, picked, expanded):
    line = 4  # leave space for header
    for child, depth in parent.traverse():
        if depth == 0:
            continue  # don't draw root node
        if line == curline:
            # picked line needs to be different than default
            child.color.curline(child.name)
            if action == 'expand':
                child.expand()
                expanded.append(child.name)
                child.color.default(child.name)
                curline += 1
            elif action == 'collapse':
                child.collapse()
                if child.name in expanded:
                    expanded.remove(child.name)
            elif action == 'expand_all':
                for c, d in child.traverse():
                    # only expand one level at a time
                    if d > 1:
                        continue
                    c.expand()
                    expanded.append(c.name)
            elif action == 'collapse_all':
                curline = child.collapse_all(parent, curline, depth)
            elif action == 'toggle_expand':
                if child.expanded:
                    child.collapse()
                    expanded.remove(child.name)
                else:
                    child.expand()
                    expanded.append(child.name)
            elif action == 'toggle_mark':
                if child.marked:
                    child.marked = False
                    picked.remove(child.name)
                    child.color.default(child.name)
                else:
                    child.marked = True
                    picked.append(child.name)
                    child.color.yellow_black()
                curline += 1
            elif action == 'next_parent':
                curline += child.nextparent(parent, curline, depth)
            elif action == 'prev_parent':
                curline = child.prevparent(parent, curline, depth)[0]
            elif action == 'get_size':
                child.getsize = True
                child.color.default(child.name)
                curline += 1
            elif action == 'get_size_all':
                for c, d in parent.traverse():
                    c.getsize = True
            action = None  # reset action
        else:
            child.color.default(child.name)
        child.drawlines(depth, curline, line)
        child.getsize = False  # stop computing sizes!
        line += 1  # keep scrolling!

    return picked, expanded, line, curline


def pick(stdscr, root, hidden):
    curses.curs_set(0)  # get rid of cursor
    picked = []
    expanded = []
    parent = Paths(stdscr, root, hidden, picked)
    parent.expand()
    curline = 4
    action = None

    while True:
        # to reset or toggle view of dotfiles we need to create a new Path
        # object before erasing the screen & descending into draw function.
        if action == 'reset':
            picked = []
            expanded = []
            parent = Paths(stdscr, root, hidden, picked)
            parent.expand()
            action = None
        elif action == 'resize':
            y, x = stdscr.getmaxyx()
            stdscr.erase()
            curses.resizeterm(y, x)
            stdscr.refresh()
        elif action == 'toggle_hidden':
            if hidden:
                hidden = False
            else:
                hidden = True
            parent = Paths(stdscr, root, hidden, picked)
            parent.expand()
            action = None
            # restore expanded & marked state
            for child, depth in parent.traverse():
                if child.name in expanded:
                    child.expand()
                if child.name in picked:
                    child.marked = True

        stdscr.erase()  # https://stackoverflow.com/a/24966639 - prevent flashes

        picked, expanded, line, curline = draw(
            parent, action, curline, picked, expanded)

        stdscr.refresh()

        action, curline = parse(stdscr, curline, line)

        if action == 'quit':
            return picked
