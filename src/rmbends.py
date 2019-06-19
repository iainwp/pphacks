import sys, os
from lxml import etree
from lxml import objectify
from copy import deepcopy

class PPenFile:
  def __init__(self, filename):
    self.doctree = objectify.parse(filename).getroot()
    self.controls = {}
    for x in self.doctree.control:
      cid = int(x.get("id"))
      if x.get("kind") == "normal":
        ccode = int(x.code.text)
        print("cc", cid, ccode)
        self.controls[cid] = ccode
        
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
    et = etree.ElementTree(self.doctree)
    et.write(fname, pretty_print=True)

  def list_courses(self):
    return [ "%s=%s" % (x.get("id"), x.name.text) for x in self.doctree.course]

  def print(self):
    return etree.tostring(self.doctree, pretty_print=True)

def main():
  fn = "hacktest.ppen"
  pp = PPenFile(fn)
  #print(pp.list_courses())
  pp.remove_bends(ex=[(32, 33)])
  pp.write("new.ppen")

main()
