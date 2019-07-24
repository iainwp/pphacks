#!/usr/bin/env python3

import sys, os
from lxml import etree
from lxml import objectify
from copy import deepcopy

class PPenFile:
  def __init__(self, filename):
    self.doctree = etree.parse(filename)
    #self.controls = {}
    #for x in self.doctree.control:
    #  cid = int(x.get("id"))
    #  if x.get("kind") == "normal":
    #    self.controls[cid] = int(x.code.text)
        
  def remove_bends(self, ex=[]):
    print(ex)
    for l in self.doctree.leg:
      o = self.controls[int(l.get('start-control'))]
      t = self.controls[int(l.get('end-control'))]
      f = (o, t)
      b = (t, o)
      if not (f in ex or b in ex):
        #print('deleting ', f, b)
        del(l.bends)

  def write(self, fname):
    self.doctree.write(fname, pretty_print=True)

  def list_courses(self):
    return [ "%s=%s" % (x.get("id"), x.name.text) for x in self.doctree.course]

  def __str__(self):
    return etree.tostring(self.doctree, pretty_print=True)

  def getmapfile(self):
    return (self.doctree.find('event/map').text,
            self.doctree.find('event/map').get('absolute-path'))

  def setmapfile(self, m, absmap):
    self.doctree.find('event/map').text = m
    self.doctree.find('event/map').set('absolute-path', absmap)

def main():
  fn = sys.argv[1]
  newmapf = sys.argv[2]
  pp = PPenFile(fn)
  x, y = pp.getmapfile()
  pp.setmapfile(newmapf, y[:-len(x)]+newmapf)
  pp.write('new.ppen')

main()
