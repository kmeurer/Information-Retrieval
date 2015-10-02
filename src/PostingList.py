
class PostingListEntry:
	def __init__(self, term):
		self.head = Node(term)

	def insertPostingDocument(docDataNode):
		if self.head.next = None:
			self.head.next = docDataNode
		else:
			current = self.head
			while current.next != None and current.next.value[id] < docDataNode.value[id]:
				current = current.next
			current.next = docDataNode

class Node:
	def __init__(self, value):
		self.value = value
		self.next = None