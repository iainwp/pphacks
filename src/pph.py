#!/usr/bin/env python3

import sys, os, argparse, json, base64
from lxml import etree
from lxml import objectify
from copy import deepcopy

class PPenFile:
  def __init__(self, filename):
    self.doctree = etree.parse(filename)

    self.controls = {}
    self.codetoid = {}
    for x in self.doctree.iter("control"):
      cid = int(x.get("id"))
      if x.get("kind") == "normal":
        self.controls[cid] = int(x.find('code').text)
        self.codetoid[self.controls[cid]] = cid

    self.courses = {}
    for x in self.doctree.iter("course"):
      if "id" not in x.keys():
        continue
      self.courses[x.find("name").text] = int(x.get("id"))
        
  def remove_bends(self, ks=[]):
    # print(ex)
    for l in self.doctree.iter("leg"):
      o, t = int(l.get('start-control')), int(l.get('end-control'))
      if o not in self.controls: continue
      if t not in self.controls: continue
      a, b = self.controls[o], self.controls[t]
      if not ((a,b) in ks or (b,a) in ks):
        xps=".//leg[@start-control='%d' and @end-control='%d']//bends"%(o,t)
        leg=self.doctree.xpath(xps)
        leg.getparent().remove(leg)

  def getbends(self):
    bends = []
    for l in self.doctree.iter("leg"):
      o, t = int(l.get('start-control')), int(l.get('end-control'))
      if o not in self.controls: continue
      if t not in self.controls: continue
      a, b = self.controls[o], self.controls[t]
      xps=".//leg[@start-control='%d' and @end-control='%d']//bends"%(o,t)
      encoded = (etree.tostring(self.doctree.xpath(xps)[0]))
      print(type(encoded), encoded)
      bends.append((a, b, encoded))
    return bends

  def setbends(self, bs):
    for f, t, b in bs:
      idf, idt = self.codetoid[f], self.codetoid[t]
      xps=".//leg[@start-control='%d' and @end-control='%d']"%(idf, idt)
      l=self.doctree.xpath(xps)
      d=b.decode('ascii')
      be=etree.fromstring(str(b))

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
    print(fc,tcs)
    fcid = self.courses[fc]
    pa = self.doctree.xpath(".//course[@id='%d']"
                            % fcid)[0].find('print-area').attrib
    for x in tcs:
      p = self.doctree.xpath(".//course[@id='%d']" % self.courses[x])[0]
      for a, v in pa.items():
        p.find('print-area').set(a, v)

def listcourses(arg):
  fn, pp = arg[1], PPenFile(fn)
  print(pp.list_courses())

def copyprintarea(s):
  fn = s.infile[0]
  pp = PPenFile(fn)
  if not s.outfile:
    outf = outf[:-5]+"-out.ppen"
  else:
    outf = s.outfile[0]
  basepacourse = s.fromcourse[0]
  if not s.tocourses:
    cs = list(pp.list_courses().keys())
  else:
    cs = s.tocourses[0].split(',')
  print(basepacourse, cs)
  pp.cppa(basepacourse, cs)
  pp.write(outf)

def intorminus1(x):
  try:
    r = int(x)
  except ValueError:
    r = -1
  return r

def rmbends(s):
  fn = s.infile[0]
  outf = s.outfile[0]
  keeps = []
  if s.keep:
    keeps = [tuple(map(intorminus1,x.split('-'))) for x in s.keep[0].split(',')]
  pp = PPenFile(fn)
  print(keeps)
  pp.remove_bends(keeps)
  pp.write(outf)

def savebends(s):
  fn, bf = s.infile[0], s.bendsfile[0]
  pp = PPenFile(fn)
  bends = pp.getbends()
  with open(bf,"w") as f:
    json.dump(bends, f)
    
def restorebends(s):
  fn, bf, outf = s.infile[0], s.bendsfile[0], s.outfile[0]
  pp = PPenFile(fn)
  with open(bf) as f:
    bends = json.load(f)
  pp.setbends(bends)
  pp.write(outf)
    
def rmcourses(s):
  fn = s.infile[0]
  outf = s.outfile[0]
  courses = s.courses[0].split(',')
  pp = PPenFile(fn)
  for x in courses:
    pp.remove_course(x)
  pp.write(outf)
  
def leavecourses(s):
  fn, outf, courses = s.infile[0], s.outfile[0], s.courses[0].split(',')
  pp = PPenFile(fn)
  for x in pp.list_courses():
    if x not in courses:
      pp.remove_course(x)
  pp.write(outf)

def listcourses(s):
  pp = PPenFile(s.infile[0])
  c = pp.list_courses()
  print(" ".join(c.keys()))
  
def chmap(s):
  outputppen = s.outfile
  newmapf = s.newmap
  pp = PPenFile(s.infile)
  x, y = pp.getmapfile()
  pp.setmapfile(newmapf, y[:-len(x)]+newmapf)
  pp.write(outputppen)

def main():  
  parser = argparse.ArgumentParser(description='PurplePen hacks.')
  subparsers = parser.add_subparsers(help='sub-command help')

  parser_a = subparsers.add_parser('rmbends', help='remove bends')
  parser_a.add_argument('infile', metavar='IN', type=str, nargs=1, help='Input ppen file')
  parser_a.add_argument('--outfile', type=str, metavar='OUT', nargs=1, required=True, help='Output ppen file')
  parser_a.add_argument('--keep', metavar='A-B,C-D', nargs=1, help='legs not to remove bends from')
  parser_a.set_defaults(func=rmbends)

  parser_sb = subparsers.add_parser('savebends', help='save bends')
  parser_sb.add_argument('infile', metavar='IN', type=str, nargs=1, help='Input ppen file')
  parser_sb.add_argument('--bendsfile', type=str, metavar='BENDS', nargs=1, required=True, help='File to save bends in')
  parser_sb.set_defaults(func=savebends)

  
  parser_rb = subparsers.add_parser('restorebends', help='restore bends')
  parser_rb.add_argument('infile', metavar='IN', type=str, nargs=1, help='Input ppen file')
  parser_rb.add_argument('--outfile', type=str, metavar='OUT', nargs=1, required=True, help='Output ppen file')
  parser_rb.add_argument('--bendsfile', type=str, metavar='BENDS', nargs=1, required=True, help='File to read bends from')
  parser_rb.set_defaults(func=restorebends)

  parser_b = subparsers.add_parser('rmcourses', help='Remove courses')
  parser_b.add_argument('infile', metavar='IN', type=str, nargs=1, help='Input ppen file')
  parser_b.add_argument('--outfile', type=str, metavar='OUT', nargs=1, help='Output ppen file')
  parser_b.add_argument('--courses', type=str, metavar='C1,C2,...',
                        nargs=1, help='Courses to remove')
  parser_b.set_defaults(func=rmcourses)

  parser_c = subparsers.add_parser('leavecourses', help='Leave courses remove others')
  parser_c.add_argument('infile', metavar='IN', type=str, nargs=1, help='Input ppen file')
  parser_c.add_argument('--outfile', metavar='OUT', type=str, nargs=1, help='Output ppen file')
  parser_c.add_argument('--courses', type=str, metavar='C1,C2,...', nargs=1, help='Courses to leave')
  parser_c.set_defaults(func=leavecourses)

  parser_d = subparsers.add_parser('copyprintarea', help='Copy print area')
  parser_d.add_argument('infile', metavar='IN', type=str, nargs=1, help='Input ppen file')
  parser_d.add_argument('--outfile', type=str, nargs=1, metavar='OUT', help='Output ppen file')
  parser_d.add_argument('--fromcourse', type=str, nargs=1, required=True, metavar='C', help='Course to copy from')
  parser_d.add_argument('--tocourses', type=str, nargs=1, metavar='C1,C2,...', help='Course(s) to copy to')
  parser_d.set_defaults(func=copyprintarea)

  parser_e = subparsers.add_parser('chmap', help='Change map')
  parser_e.add_argument('infile', metavar='IN', type=str, nargs=1, help='Input ppen file')
  parser_e.add_argument('--outfile', type=str, metavar='OUT', nargs=1, help='Output ppen file')
  parser_e.add_argument('--newmap', metavar='MAPFILE', type=str, nargs=1, help='New map file')
  parser_e.set_defaults(func=chmap)

  parser_f = subparsers.add_parser('listcourses', help='List courses in a ppen file')
  parser_f.add_argument('infile', metavar='IN', type=str, nargs=1, help='Input ppen file')
  parser_f.set_defaults(func=listcourses)

  args = parser.parse_args()
  args.func(args)

main()
