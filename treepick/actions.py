# Copyright (c) 2018, Toby Slight. All rights reserved.
# ISC License (ISCL) - see LICENSE file for details.

import os
import fnmatch

from .draw import Draw


class Actions(Draw):
    def __init__(self,
                 screen,
                 name,
                 hidden,
                 picked=[],
                 expanded=set(),
                 sized=dict()):
        Draw.__init__(self, screen, picked, expanded, sized)
        self.name = name
        self.hidden = hidden
        self.globs, self.matches = (None,)*2
        self.lastpath, self.lasthidden = (None,)*2

    def quit(self):
        return True

    def reset_all(self):
        self.picked = []
        self.expanded = set([self.name])
        self.sized = {}

    def reset_picked(self):
        self.picked = []

    def dn(self):
        self.curline += 1

    def up(self):
        self.curline -= 1

    def pgdn(self):
        self.curline += self.y
        if self.curline >= self.line:
            self.curline = self.line - 1

    def pgup(self):
        self.curline -= self.y
        if self.curline < 0:
            self.curline = 0

    def top(self):
        self.curline = 0

    def bottom(self):
        self.curline = self.line - 1

    def toggle_hidden(self):
        self.paths = None

        if self.hidden:
            # keep two copies of record so we can restore from state when
            # re-hiding
            self.lastpath = self.children[self.curline]
            self.hidden = False
        else:
            # keep two copies of record so we can restore from state
            self.lasthidden = self.children[self.curline]
            self.hidden = True

        self.drawtree()

        if self.lasthidden in self.children:
            self.curline = self.children.index(self.lasthidden)
        elif self.lastpath in self.children:
            self.curline = self.children.index(self.lastpath)

    def expand(self, recurse=False, toggle=False):
        if os.path.isdir(self.name) and self.children and recurse:
            self.expanded.add(self.name)
            for c, d in self.traverse():
                if d < 2 and os.path.isdir(c.name) and c.children:
                    self.expanded.add(c.name)
            self.curline += 1
        elif os.path.isdir(self.name) and self.children:
            if toggle:
                if self.name in self.expanded:
                    self.expanded.remove(self.name)
                else:
                    self.expanded.add(self.name)
            else:
                self.expanded.add(self.name)
                self.curline += 1

    def collapse(self, parent, depth, recurse=False):
        if depth > 1 and recurse:
            p = self.prevparent(parent, depth)
            self.expanded.remove(p)
            for x in list(self.expanded):  # iterate over copy
                par = os.path.abspath(p)
                path = os.path.abspath(x)
                if path.startswith(par):
                    self.expanded.remove(x)
        elif self.name in self.expanded:
            self.expanded.remove(self.name)
        elif depth > 1 and not os.path.isdir(self.name):
            p = self.prevparent(depth)
            self.expanded.remove(p)

    def pick(self, pickall=False, globs=False):
        if pickall:
            for c, d in self.traverse():
                if d == 0:
                    continue
                if c.name in self.picked:
                    self.picked.remove(c.name)
                else:
                    self.picked.append(c.name)
        elif globs:
            self.globs = self.mktb("Pick: ").strip().split()
            if self.globs:
                for c, d in self.traverse():
                    for g in self.globs:
                        if (fnmatch.fnmatch(c.name, g) or
                                fnmatch.fnmatch(os.path.basename(c.name), g)):
                            if c.name in self.picked:
                                self.picked.remove(c.name)
                            else:
                                self.picked.append(c.name)
        else:
            if self.name in self.picked:
                self.picked.remove(self.name)
            else:
                self.picked.append(self.name)
            self.curline += 1

    def nextparent(self, parent, depth):
        '''
        Add lines to current line by traversing the grandparent object again
        and once we reach our current line counting every line that is prefixed
        with the parent directory.
        '''
        pdir = os.path.dirname(self.name)
        if depth > 1:  # can't jump to parent of root node!
            line = 0
            for c, d in parent.traverse():
                if line > self.curline and c.name.startswith(pdir + os.sep):
                    self.curline += 1
                line += 1
        else:  # otherwise just skip to next directory
            line = -1  # skip hidden parent node
            for c, d in parent.traverse():
                if line > self.curline:
                    self.curline += 1
                    if os.path.isdir(c.name) and c.name in parent.children[self.curline:]:
                        break
                line += 1

    def prevparent(self, parent, depth):
        '''
        Subtract lines from our curline if the name of a node is prefixed with
        the parent directory when traversing the grandparent object.
        '''
        pdir = os.path.dirname(self.name)
        if depth > 1:  # can't jump to parent of root node!
            for c, d in parent.traverse():
                if c.name == self.name:
                    break
                if c.name.startswith(pdir):
                    self.curline -= 1
        else:  # otherwise jus skip to previous directory
            pdir = self.name
            # - 1 otherwise hidden parent node throws count off & our
            # self.curline doesn't change!
            line = -1
            for c, d in parent.traverse():
                if c.name == self.name:
                    break
                if os.path.isdir(c.name) and c.name in parent.children[0:]:
                    self.curline = line
                line += 1
        return pdir

    def find(self):
        string = self.mktb("Find: ").strip()
        if string:
            self.matches = []
            line = -1
            for c, d in self.traverse():
                if string in os.path.basename(c.name):
                    self.matches.append(line)
                line += 1
            if self.matches:
                self.findnext()

    def findnext(self):
        for m in range(len(self.matches)):
            if self.curline == self.matches[len(self.matches) - 1]:
                self.curline = self.matches[0]
                break
            elif self.curline < self.matches[m]:
                self.curline = self.matches[m]
                break

    def findprev(self):
        for m in range(len(self.matches)):
            if self.curline <= self.matches[m]:
                self.curline = self.matches[m-1]
                break

    def getsize(self, sizeall=False):
        if sizeall:
            for c, d in self.traverse():
                self.sized[os.path.abspath(c.name)] = None
        else:
            self.sized[os.path.abspath(self.name)] = None
            self.curline += 1
