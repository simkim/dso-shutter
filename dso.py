from xml.dom.minidom import parse

class DSOWaveForm:
	domRoot = None
	profile = None
	points = None
	def __init__(self):
		self.profile = {}
		self.points = []
		self.hld = []
	def load(self, filename):
		# load dom
		self.domRoot = parse(filename)
		# load profile
		self.profile = {}
		node = self.domRoot.getElementsByTagName("Profile")
		assert len(node)>0, "Profile not found"
		for child in node[0].childNodes:
			if child.nodeType == 3:
				continue
			key   = child.nodeName
			value = child.firstChild.nodeValue
			self.profile[key] = value
		points = self.domRoot.getElementsByTagName("Point")
		self.points = []
		for point in points:
			seq = int(point.getElementsByTagName("seq")[0].firstChild.nodeValue)
			value = float(point.getElementsByTagName("val")[0].firstChild.nodeValue)
			self.points.append((seq, value))
	def computeHLDurations(self):
		assert len(self.points) > 0
		triggerIndex = int(self.profile["triggerIndex"])
		triggerKind  = self.profile["triggerKind"]

		lastState = 0 if triggerKind=="EdgeFalling" else 1
		duration = 0
		for seq, val in self.points[triggerIndex:-1]:
			state = 1 if val > 0.7 else 0
			if state != lastState:
				self.hld.append((lastState, duration))
				lastState = state
				duration = 1
			else:
				duration += 1
		self.hld.append((lastState, duration))
	def printHLD(self):
		for (state, duration) in self.hld:
			print "%d - %d" % (state, duration)
	def decodeBits(self, skip=0):
		stack = self.hld[skip:]
		stack.reverse()
		state1, duration1 = stack.pop()
		if state1 != 0:
			state1, duration1 = stack.pop()	
		state2, duration2 = stack.pop()
		bitCount = 0
		while True:
			if state1 == 0 and state2 == 1 and abs(duration1+duration2-40) < 2:
				if abs(duration1-30) < 3 and abs(duration2-10) < 3:
					bitCount += 1
					print 0,
					if bitCount % 8 == 0:
						print
				elif abs(duration2-30) < 3 and abs(duration1-10) < 3:
					bitCount += 1
					print 1,
					if bitCount % 8 == 0:
						print
				else:
					print "can't decode bit"
					break
			elif state1 == 0 and state2 == 1 and abs(duration1-25) < 2 and abs(duration2-25) < 2:
				print "end (transmittion succeed)"
				break
			else:
				print "invalid transition (%d %d %d %d)" % (state1, state2, duration1, duration2)
				break
			if len(stack) > 2:
				state1, duration1 = stack.pop()
				state2, duration2 = stack.pop()
			else:
				print "stack empty (transmittion truncated ?)"
				break
if __name__ == "__main__":
	import sys
	d = DSOWaveForm()
	d.load(sys.argv[1])
	d.computeHLDurations()
	d.printHLD()
	d.decodeBits(2)
