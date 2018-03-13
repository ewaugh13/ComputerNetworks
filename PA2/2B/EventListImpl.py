from Event import Event
from Packet import Packet
class EventListImpl(object):
	TIMERINTERRUPT=0
	FROMLAYER3=2

	def __init__(self):
		self.data=[]

	def add(self, e):
		if type(e)==type(Event()):
			self.data.append(e)
			return bool(1)
		else:
			print "Object of type Event() can only be added"
			return bool(0)

	def remove_next(self):
		if(len(self.data)==0):
			return None
		first_index=0
		first=self.data[first_index].get_time()
		for i in range(0, len(self.data)):
			if(self.data[i].get_time() < first):
				first=self.data[i].get_time()
				first_index=i

		_next= self.data[first_index]
		del self.data[first_index]
		return _next

	def __str__(self):
		for i in self.data:
			print i
		return ""

	def remove_timer(self, entity):
		timer_index=-1
		timer = None
		for i in range(len(self.data)):
			if self.data[i].get_type()==EventListImpl.TIMERINTERRUPT and self.data[i].get_entity()==entity:
				timer_index=i
				break

		if timer_index!=-1:
			timer=self.data[timer_index]
			del self.data[timer_index]

		return timer

	def get_last_packet_time(self, entity_to):
		time=float(0)
		for i in range(0,len(self.data)):
			if self.data[i].get_type()==EventListImpl.FROMLAYER3 and self.data[i].get_entity()==entity_to:
				time = self.data[i].get_time()

		return time
