from Packet import Packet

class Event():
	TIMERINTERRUPT=0
	FROMLAYER5=1
	FROMLAYER3=2
	A=0
	B=1

	def __init__(self,*args):
		if len(args)==3:
			self.time=args[0]
			self.type=args[1]
			self.entity=args[2]
			self.packet=None
		
		if len(args)==4 and type(args[3])==type(Packet()):
			self.time=args[0]
			self.type=args[1]
			self.entity=args[2]
			self.packet=Packet(args[3])

	def set_time(self, time):
		if type(time)==type("string"):
			self.time=-1
			print "Warning: Time has to be numeric value"
			return 0
		else:
			self.time=time
			return bool(1)

	def set_type(self, n):
		if(n!= Event.TIMERINTERRUPT and n!=Event.FROMLAYER5 and n!=Event.FROMLAYER3):
			print "Invalid input to set_type()."
			self.type=-1
			return bool(0)
		else:
			if(type(n)==type(1)):
				self.type=n
				return bool(1)
			else:
				self.type="ERROR"
				print "Type has to be an int"
				return 0

	def set_entity(self, n):
		if(n!=Event.A and n!=Event.B):
			print "Invalid input to set_entity()."
			self.entity=-1
			return bool(0)
		else:
			if(type(n)==type(1)):
				self.entity=n
				return bool(1)
			else:
				self.entity=-1
				print "Entity has to be an int"
				return 0

	def set_packet(self, packet=None): 
		if packet==None:
			print "Packet cant be set to none."
			self.packet=None
		else: 
			if type(packet)==type(Packet()):
				self.packet=Packet(packet.get_seqnum(), packet.get_acknum(), packet.get_checksum(), packet.get_payload())
				return bool(1)
			else:
				self.packet=None
				print "Invalid type in set_packet() argument."
				return 0

		

	def get_time(self):
		return self.time

	def get_type(self):
		return self.type

	def get_entity(self):
		return self.entity

	def get_packet(self):
		return self.packet

	def __str__(self):
		try:
			return 'time: %f type: %d entity: %d packet: [%s]' %(self.time, self.type, self.entity, self.packet)
		except Exception:
			return "time, type and entity should be numeric and packet must be of type class Packet. "

