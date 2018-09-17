class Automate:
	Q = []
	A = []
	q = ""
	F = []
	D = []

	def transformToAutomate(self, sa):
		if not sa.startswith("Q={") :
			raise Exception('Syntax Error')
		self.Q = sa[3:sa.find('}')].split(',')
		for s in self.Q:
			if s.startswith('$'):
				raise Exception('Syntax Error')
		sa = sa[sa.find('}') + 1:]
		if not sa.startswith(",A={") :
			raise Exception('Syntax Error')
		self.A = sa[4:sa.find('}')].split(',')

		sa = sa[sa.find('},') + 2:]
		if not sa.startswith("q=") :
			raise Exception('Syntax Error')
		self.q = sa[2:sa.find(',')]

		sa = sa[sa.find(',') + 1:]
		if not sa.startswith("F={") :
			raise Exception('Syntax Error')
		self.F = sa[3:sa.find('}')].split(',')

		sa = sa[sa.find('},') + 2:]
		if not sa.startswith("D={") :
			raise Exception('Syntax Error')
		self.D = sa[3:sa.find('}')].split(',')

	def getEdges(self, node):
		listOfEdges = []
		for d in self.D:
			if d[2:d.find(';')] == node:
				listOfEdges.append(d)
		return listOfEdges

	def getEnterEdges(self, node, a):
		listOfEdges = []
		for d in self.D:
			if d[d.find('=') + 1:] == node and d[d.find(';')+1:d.find(')')] == a:
				listOfEdges.append(d)
		return listOfEdges

	def delUnrichableNodes(self):

		visitedNodes = {i : False for i in self.Q}
		nodes = []
		nodes.append(self.q)
		while len(nodes) > 0:
			node = nodes.pop(0)
			visitedNodes[node] = True
			edges = self.getEdges(node)
			for edge in edges:
				v = edge[edge.find('=') + 1:]
				if visitedNodes[v] == False:
					nodes.append(v)
		for node in visitedNodes.keys():
			if not visitedNodes[node]:
				self.Q.remove(node)
				edges = self.getEdges(node)
				for edge in edges:
					self.D.remove(edge)

	def makeAutomateFull(self):
		devilNode = '$1'
		devilNodeIsPresent = False
		for node in self.Q:
			presentEdges = {i : False for i in self.A}

			edges = self.getEdges(node)
			for edge in edges:
				presentEdges[edge[edge.find(';') + 1 : edge.find(')')]] = True

			for a in presentEdges.keys():
				if not presentEdges[a]:
					devilNodeIsPresent = True
					self.D.append('d('+ node +';'+ a +')=$1')
		if devilNodeIsPresent:
			self.Q.append(devilNode)
				
	def createDelta(self):
		delta = []
		for i in self.Q:
			row = []
			for a in self.A:
				nodes = []
				enterEdges = self.getEnterEdges(i, a)
				for edge in enterEdges :
					nodes.append(edge[2:edge.find(';')])
				row.append(nodes)
			delta.append(row)
		return delta

	def getEquivalents(self, delta):
		matrix = []
		for n in range(len(self.Q)):
			matrix.append([False for x in range(n)])
		queue = []
		for f in self.F:
			for q in self.Q:
				if q not in self.F:
					queue.append('('+ q + ',' + f +')')
					i = self.Q.index(q)
					j = self.Q.index(f)
					matrix[max(i,j)][min(i,j)] = True
		while len(queue) > 0:
			pair = queue.pop(0)
			first = pair[1:pair.find(',')]
			second = pair[pair.find(',') + 1 : pair.find(')')]
			mx = max(self.Q.index(first), self.Q.index(second))
			mn = min(self.Q.index(first), self.Q.index(second))
			for collumn in range(len(delta[0])):
				l1 = delta[mn][collumn]
				l2 = delta[mx][collumn]
				for el1 in l1:
					for el2 in l2:
						i = self.Q.index(el1)
						j = self.Q.index(el2)
						if matrix[max(i,j)][min(i,j)] == False:
							matrix[max(i,j)][min(i,j)] = True
							queue.append('('+ el1 + ',' + el2 +')')
		equivalents = []
		for n in range(len(self.Q)):
			for m in range(n):
				if matrix[n][m] == False:
					equivalents.append('('+ self.Q[n] +','+ self.Q[m] +')')
		return equivalents

	def unionEquivalents(self, equivalents):
		for e in equivalents:
			first = e[1:e.find(',')]
			second = e[e.find(',') + 1 : e.find(')')]
			self.Q.remove(first)
			self.Q.remove(second)
			fedges = self.getEdges(first)
			sedges = self.getEdges(second)
			finedges = []
			sinedges = []
			for a in self.A:
				for edge in self.getEnterEdges(first, a) :
					finedges.append(edge)
				for edge in self.getEnterEdges(second, a) :
					sinedges.append(edge)
			edges = []
			v = first + "&" + second
			fedges.extend(sedges)
			for edge in fedges:
				if edge in self.D:
					self.D.remove(edge)

				newEdge = 'd(' + v + ';' + edge[edge.find(';') + 1 : edge.find(')')] + ')='
				target = edge[edge.find('=') + 1 :]
				if target == first or target == second:
					newEdge += v
				else:
					newEdge += target 
				if newEdge not in edges:
					
					edges.append(newEdge)
			finedges.extend(sinedges)
			for edge in finedges:
				if edge in self.D:
					self.D.remove(edge)
				if edge[2: edge.find(';')] == first or edge[2: edge.find(';')] == second:
					continue
				newEdge = edge[: edge.find('=') + 1] + first + "&" + second
				if newEdge not in edges:
					edges.append(newEdge)
			if first in self.F:
				self.F.remove(first)
				self.F.remove(second)
				self.F.append(v)
			self.D.extend(edges)
			self.Q.append(v)


path = input("Enter file path:")
with open(path, 'r') as fin:
	strautomate = ""
	for s in fin.readlines():
		strautomate += s
	strautomate = strautomate.replace(" ", "")
	strautomate = strautomate.replace("\n", "")
	automate = Automate()
	automate.transformToAutomate(strautomate)
	automate.delUnrichableNodes()
	automate.makeAutomateFull()
	delta = automate.createDelta()
	equivalents = automate.getEquivalents(delta)
	automate.unionEquivalents(equivalents)
	with open('result.txt', 'w') as result:
		result.write('Q={' + ", ".join(str(x) for x in automate.Q) + '}, A={' + ", ".join(str(x) for x in automate.A) + '}, q=' + automate.q + ', D={' +", ".join(str(x) for x in automate.D) + '}')


