#!/usr/bin/python
 
""" helper script to transorm dso xml export files to png graph using Gnuplot """

import Gnuplot, Gnuplot.funcutils
from xml.dom.minidom import parse
 
g = Gnuplot.Gnuplot(debug=1)

def d(filename, skip=None):
	x = parse(filename)
	triggerIndex = x.getElementsByTagName("triggerIndex")[0].firstChild.nodeValue
	data = list(enumerate(map(lambda e :  float(e.firstChild.nodeValue), x.getElementsByTagName("val"))))
	if not skip:
		skip = int(triggerIndex)
	data = map(lambda (k,v) : [k-skip,v], data)
	data = data[skip:-1]
	return Gnuplot.Data(data,**{'title':filename,'with':"lines"})

g('set output "/tmp/dso.png"')
g('set terminal png size 3200,240 ')
g._add_to_queue([d("BUFFER/FILE002.XML"),d("BUFFER/FILE004.XML")])
g.replot()
