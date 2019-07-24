#!/usr/bin/env python3

import sys, os
from lxml import etree
from lxml import objectify
from copy import deepcopy

class PPenFile:
  def __init__(self, filename):
    self.doctree = etree.parse(filename)

    self.controls = {}
    for x in self.doctree.iter("control"):
      cid = int(x.get("id"))
      if x.get("kind") == "normal":
        self.controls[cid] = int(x.find('code').text)

    self.courses = {}
    for x in self.doctree.iter("course"):
      if "id" not in x.keys():
        continue
      self.courses[x.find("name").text] = int(x.get("id"))
        
  def remove_bends(self, ex=[]):
    # print(ex)
    for l in self.doctree.iter("leg"):
      o = l.get('start-control')
      t = l.get('end-control')
      if o not in self.controls:
        continue
      if t not in self.controls:
        continue
      o = self.controls[int(l.get('start-control'))]
      t = self.controls[int(l.get('end-control'))]
      print(o,t)
      f, b = (o, t), (t, o)
      if not (f in ex or b in ex):
        #print('deleting ', f, b)
        del(l.bends)

  def write(self, fname):
    self.doctree.write(fname, pretty_print=True)

  def list_courses(self):
    return self.courses

  def remove_course(self, name):
    i = self.courses[name]
    c = self.doctree.xpath(".//course[@id='%d']"%i)[0]
    c.getparent().remove(c)

  def __str__(self):
    return etree.tostring(self.doctree, pretty_print=True)

  def getmapfile(self):
    return (self.doctree.find('event/map').text,
            self.doctree.find('event/map').get('absolute-path'))

  def setmapfile(self, m, absmap):
    self.doctree.find('event/map').text = m
    self.doctree.find('event/map').set('absolute-path', absmap)

  def cppa(self, fc, tcs):
    fcid = self.courses[fc]
    pa = self.doctree.xpath(".//course[@id='%d']"%fcid)[0].find('print-area').attrib
    print(pa)
    for x in tcs:
      p = self.doctree.xpath(".//course[@id='%d']" % self.courses[x])[0]
      for a, v in pa.items():
        p.find('print-area').set(a, v)
    


#def rmbends():
#  fn = sys.argv[1]
#  pp = PPenFile(fn)
#  pp.remove_bends()
#  pp.write('new.ppen')
  
def chmap(arg):
  fn = arg[1]
  newmapf = arg[2]
  outputppen = arg[3]
  pp = PPenFile(fn)
  x, y = pp.getmapfile()
  pp.setmapfile(newmapf, y[:-len(x)]+newmapf)
  pp.write(outputppen)

def leavecourses(arg):
  fn = arg[1]
  outf = arg[2]
  courses = arg[3].split(',')
  
  pp = PPenFile(fn)
  for x in pp.list_courses():
    if x not in courses:
      pp.remove_course(x)
  pp.write(outf)

def listcourses(arg):
  fn = arg[1]
  pp = PPenFile(fn)
  print(pp.list_courses())


def cppa(arg):
  fn = arg[1]
  outf = arg[2]
  basepacourse = arg[3]
  pp = PPenFile(fn)
  x = list(pp.list_courses().keys())
  x.remove(basepacourse)
  pp.cppa(basepacourse, x)
  pp.write(outf)
  
  
  
def main():
  if sys.argv[1] == "chmap":
    chmap(sys.argv[1:])
  elif sys.argv[1] == "leavecourses":
    leavecourses(sys.argv[1:])
  elif sys.argv[1] == "listcourses":
    listcourses(sys.argv[1:])
  elif sys.argv[1] == "cppa":
    cppa(sys.argv[1:])
  else:
    print("What?")
main()
