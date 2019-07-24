#!/usr/bin/env python3

import sys, os, argparse
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
    pa = self.doctree.xpath(".//course[@id='%d']"
                            % fcid)[0].find('print-area').attrib
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


def copyprintarea(s):
  fn = s.infile[0]
  outf = s.outfile[0]
  if outf == None:
    outf = outf[:-5]+"-out.ppen"
  basepacourse = s.fromcourse[0]
  copytocourses = s.tocourses[0].split(',')
  pp = PPenFile(fn)
  pp.cppa(basepacourse, copytocourses)
  pp.write(outf)
  
def rmbends(s):
  print(s.infile)
  print(s.outfile)
  print(s.exclude_legs)
  print("not implemented yet")
  
def rmcourses(s):
  print(s.infile)
  print(s.outfile)
  print(s.courses)
  
def leavecourses(s):
  print(s.infile)
  print(s.outfile)
  print(s.courses)
  

def chmap(s):
  print(s.infile)
  print(s.outfile)
  print(s.newmap)


def main():  
  parser = argparse.ArgumentParser(description='PurplePen hacks.')
  subparsers = parser.add_subparsers(help='sub-command help')

  parser_a = subparsers.add_parser('rmbends', help='remove bends')
  parser_a.add_argument('infile', metavar='IN', type=str, nargs=1, help='Input ppen file')
  parser_a.add_argument('--outfile', type=str, metavar='OUT', nargs=1, help='Output file')
  parser_a.add_argument('--exclude-legs', metavar='A-B,C-D', nargs=1, help='legs not to remove bends from')
  parser_a.set_defaults(func=rmbends)

  parser_b = subparsers.add_parser('rmcourses', help='Remove courses')
  parser_b.add_argument('infile', metavar='IN', type=str, nargs=1, help='Input ppen file')
  parser_b.add_argument('--outfile', type=str, metavar='OUT', nargs=1, help='Output file')
  parser_b.add_argument('--courses', type=str, metavar='C1,C2,...', nargs=1, help='Output file')
  parser_b.set_defaults(func=rmcourses)

  parser_c = subparsers.add_parser('leavecourses', help='Leave courses remove others')
  parser_c.add_argument('infile', metavar='IN', type=str, nargs=1, help='Input ppen file')
  parser_c.add_argument('--outfile', metavar='OUT', type=str, nargs=1, help='Output file')
  parser_c.set_defaults(func=leavecourses)

  parser_d = subparsers.add_parser('copyprintarea', help='Copy print area')
  parser_d.add_argument('infile', metavar='IN', type=str, nargs=1, help='Input ppen file')
  parser_d.add_argument('--outfile', type=str, nargs=1, metavar='OUT', help='Output file')
  parser_d.add_argument('--fromcourse', type=str, nargs=1, required=True, metavar='C', help='Course to copy from')
  parser_d.add_argument('--tocourses', type=str, nargs=1, default="All", metavar='C1,C2,...', help='Course(s) to copy to')
  parser_d.set_defaults(func=copyprintarea)

  parser_e = subparsers.add_parser('chmap', help='Change map')
  parser_e.add_argument('infile', metavar='IN', type=str, nargs=1, help='Input ppen file')
  parser_e.add_argument('--outfile', type=str, metavar='OUT', nargs=1, help='Output file')
  parser_e.add_argument('--newmap', metavar='MAPFILE', type=str, nargs=1, help='New map file')
  parser_e.set_defaults(func=chmap)

  args = parser.parse_args()
  args.func(args)

main()
