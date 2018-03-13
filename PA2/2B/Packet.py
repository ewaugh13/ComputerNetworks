""" Working fine """
import copy
class MyException(Exception):
    pass

class Packet(object):
	"""
	args[0]=sequence number
	args[1]=acknowledgement number
	args[2]=checksum
	args[3]=payload string
	"""
	MAXDATASIZE=20
	def __init__(self, *args):
		#copies object
		if len(args)==1 and type(args[0])==type(Packet()):
			self.seqnum=args[0].seqnum
			self.acknum=args[0].acknum
			self.checksum=args[0].checksum
			self.payload=args[0].payload

		if len(args)==3:
			self.seqnum=args[0]
			self.acknum=args[1]
			self.checksum=args[2]
			self.payload=""

		if len(args)==4:
			self.seqnum=args[0]
			self.acknum=args[1]
			self.checksum=args[2]
			if type(args[3])==type("string"):
				self.payload=args[3]
			else:
				payload=""
				raise MyException("Payload has to be a string.")
				


	def set_seqnum(self, seq=None):
		if seq==None:
			print "Sequence number needs to be specified in order to set it."
			return bool(0)
		else:
			self.seqnum=seq
			return bool(1)

	def set_acknum(self, ack=None):
		if ack==None:
			print "Acknowledgement number needs to be specified in order to set it."
			return bool(0)
		else:
			self.acknum=ack
			return bool(1)

	def set_checksum(self, chk=None):
		if chk==None:
			print "Checksum needs to be specified in order to set it."
			return bool(0)
		else:
			self.checksum=chk
			return bool(1)

	def set_payload(self, pld=None):
		if pld is None:
			print "Warning: Payload needs to be specified in order to set it"
			self.payload=""
			return bool(0)
		elif len(pld) > Packet.MAXDATASIZE:
			print "Payload length greater than MAXDATASIZE. Setting payload to None"
			self.payload=None
			return bool(0)
		else:
			if type(pld)==type("string"):
				self.payload=pld
				return bool(1)
			else:
				raise MyException("Payload has to be a string.")

	def get_seqnum(self):
		try:
			return self.seqnum
		except Exception:
			print "Exception caught in method get_seqnum()"
			return None

	def get_acknum(self):
		try:
			return self.acknum
		except Exception:
			print "Exception caught in method get_acknum()"
			return None

	def get_checksum(self):
		try:
			return self.checksum
		except Exception:
			print "Exception caught in method get_checksum()"
			return 0

	def get_payload(self):
		try:
			return self.payload
		except Exception:
			print "Exception caught in method get_payload()"
			return 0

	def __str__(self):
		try:
			return 'seqnum: %d acknum: %d checksum: %d payload: %s' % (self.seqnum, self.acknum, self.checksum, self.payload)
		except Exception:
			print "Error: sequence number, acknowledgement number, and checksum should be integer type. Payload must be a string."
			return None


"""def main():
	pac=Packet(123,23,21)
	pac12=Packet(123,23,21,"jkl")
	pac13=Packet(pac12)
	print pac13
	pac13.get_payload()
	pac13.get_checksum()
	pac13.get_acknum()
	pac13.get_seqnum()
	pac13.set_acknum(123)
	pac13.set_checksum(234)
	pac13.set_payload("jau")
	pac13.set_seqnum(12)
	#print pac13
	pac14=Packet(1,2,3)
	pac14.set_payload()
	print pac14

main()"""