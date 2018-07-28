import curses
from os import environ
environ.setdefault('ESCDELAY', '12')  # otherwise it takes an age!
ESC = 27


def show(stdscr):
    from textwrap import dedent
    msg = '''
        KEYBINDINGS:

        +-------------+-----------------------------------------------------+
        | KEY         | ACTION                                              |
        +-------------+-----------------------------------------------------+
        | UP, k, p    | Go up one line.                                     |
        | DOWN, j, n  | Go down one line.                                   |
        | RIGHT, l, f | Expand directory, and move down one line.           |
        | LEFT, h, b  | Collapse directory.                                 |
        | TAB, RET    | Toggle expansion/collapse of directory.             |
        | PGDN, d, v  | Move down a page of lines.                          |
        | PGUP, u, V  | Move up a page of lines.                            |
        | J, N        | Move to next parent directory.                      |
        | K, P        | Move to parent parent directory.                    |
        | g, <        | Move to first line.                                 |
        | G, >        | Move to last line.                                  |
        | m, SPC      | Toggle marking of paths.                            |
        | .           | Toggle display of dotfiles.                         |
        | s           | Display total size of path, recursively             |
        | S           | Display totol size of all currently expanded paths. |
        | r           | Reset marking and expansion.                        |
        | q, ESC      | Quit and display all marked paths.                  |
        +-------------+-----------------------------------------------------+

        ENTER ANY KEY TO RETURN.
        '''
    msg = dedent(msg).strip()
    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()
    keys = stdscr.subwin(max_y, max_x, 0, 0)
    keys.attrset(curses.color_pair(0))
    keys.addstr(0, 0, msg)
    keys.getch()


def parse(stdscr, curline, line):
    action = None
    ch = stdscr.getch()
    if ch == ord('q') or ch == ESC:
        return
    elif ch == ord('r'):
        action = 'reset'
    elif ch == ord('.'):
        action = 'toggle_hidden'
    elif ch == curses.KEY_RIGHT or ch == ord('l') or ch == ord('f'):
        action = 'expand'
    elif ch == curses.KEY_LEFT or ch == ord('h') or ch == ord('b'):
        action = 'collapse'
    elif ch == ord('L') or ch == ord('F'):
        action = 'expand_all'
    elif ch == ord('H') or ch == ord('B'):
        action = 'collapse_all'
    elif ch == ord('\t') or ch == ord('\n'):
        action = 'toggle_expand'
    elif ch == ord('m') or ch == ord(' '):
        action = 'toggle_mark'
    elif ch == ord('J') or ch == ord('N'):
        action = 'next_parent'
    elif ch == ord('K') or ch == ord('P'):
        action = 'prev_parent'
    elif ch == ord('s'):
        action = 'get_size'
    elif ch == ord('S'):
        action = 'get_size_all'
    elif ch == ord('?'):
        show(stdscr)
    elif ch == curses.KEY_UP or ch == ord('k') or ch == ord('p'):
        curline -= 1
    elif ch == curses.KEY_DOWN or ch == ord('j') or ch == ord('n'):
        curline += 1
        if curline >= line:
            curline = 4
    elif ch == curses.KEY_UP or ch == ord('k') or ch == ord('p'):
        curline -= 1
        if curline < 4:
            curline = line - 1
    elif ch == curses.KEY_PPAGE or ch == ord('u') or ch == ord('V'):
        curline -= curses.LINES
        if curline < 4:
            curline = line - 1
    elif ch == curses.KEY_NPAGE or ch == ord('d') or ch == ord('v'):
        curline += curses.LINES
        if curline >= line:
            curline = line - 1
    elif ch == curses.KEY_HOME or ch == ord('g') or ch == ord('<'):
        curline = 4
    elif ch == curses.KEY_END or ch == ord('G') or ch == ord('>'):
        curline = line - 1
    curline %= line
    return action, curline
