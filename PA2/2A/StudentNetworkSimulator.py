from NetworkSimulator import NetworkSimulator
from Queue import Queue
import random
from Event import Event
from Packet import Packet
from message import Message
from EventListImpl import EventListImpl
import random
import math

class StudentNetworkSimulator(NetworkSimulator, object):


	"""
	* Predefined Constants (static member variables):
	 *
	 *   int MAXDATASIZE : the maximum size of the Message data and
	 *                     Packet payload
	 *
	 *   int A           : a predefined integer that represents entity A
	 *   int B           : a predefined integer that represents entity B
	 *
	 *
	 * Predefined Member Methods:
	 *
	 *  stopTimer(int entity): 
	 *       Stops the timer running at "entity" [A or B]
	 *  startTimer(int entity, double increment): 
	 *       Starts a timer running at "entity" [A or B], which will expire in
	 *       "increment" time units, causing the interrupt handler to be
	 *       called.  You should only call this with A.
	 *  toLayer3(int callingEntity, Packet p)
	 *       Puts the packet "p" into the network from "callingEntity" [A or B]
	 *  toLayer5(int entity, String dataSent)
	 *       Passes "dataSent" up to layer 5 from "entity" [A or B]
	 *  getTime()
	 *       Returns the current time in the simulator.  Might be useful for
	 *       debugging.
	 *  printEventList()
	 *       Prints the current event list to stdout.  Might be useful for
	 *       debugging, but probably not.
	 *
	 *
	 *  Predefined Classes:
	 *
	 *  Message: Used to encapsulate a message coming from layer 5
	 *    Constructor:
	 *      Message(String inputData): 
	 *          creates a new Message containing "inputData"
	 *    Methods:
	 *      boolean setData(String inputData):
	 *          sets an existing Message's data to "inputData"
	 *          returns true on success, false otherwise
	 *      String getData():
	 *          returns the data contained in the message
	 *  Packet: Used to encapsulate a packet
	 *    Constructors:
	 *      Packet (Packet p):
	 *          creates a new Packet that is a copy of "p"
	 *      Packet (int seq, int ack, int check, String newPayload)
	 *          creates a new Packet with a sequence field of "seq", an
	 *          ack field of "ack", a checksum field of "check", and a
	 *          payload of "newPayload"
	 *      Packet (int seq, int ack, int check)
	 *          chreate a new Packet with a sequence field of "seq", an
	 *          ack field of "ack", a checksum field of "check", and
	 *          an empty payload
	 *    Methods:
	 *      boolean setSeqnum(int n)
	 *          sets the Packet's sequence field to "n"
	 *          returns true on success, false otherwise
	 *      boolean setAcknum(int n)
	 *          sets the Packet's ack field to "n"
	 *          returns true on success, false otherwise
	 *      boolean setChecksum(int n)
	 *          sets the Packet's checksum to "n"
	 *          returns true on success, false otherwise
	 *      boolean setPayload(String newPayload)
	 *          sets the Packet's payload to "newPayload"
	 *          returns true on success, false otherwise
	 *      int getSeqnum()
	 *          returns the contents of the Packet's sequence field
	 *      int getAcknum()
	 *          returns the contents of the Packet's ack field
	 *      int getChecksum()
	 *          returns the checksum of the Packet
	 *      int getPayload()
	 *          returns the Packet's payload
	 *

	"""



	
	# Add any necessary class/static variables here.  Remember, you cannot use
	# these variables to send messages error free!  They can only hold
	# state information for A or B.
	# Also add any necessary methods (e.g. checksum of a String)

	time_increment = 10
	current_time_increment = time_increment


	packet_count = 0
	timeout_counter = 0

	packet_count_sent = 0
	packet_count_recv = 0

	ack_count_sent = 0
	ack_count_recv = 0

	layer5_sent = 0
	layer5_recv = 0

	loss_count = 0
	corrupt_counter = 0

	#creates checksum using seq num and ack num plus all the data of the payload
	def create_checksum(self, seq, ack, payload):
		checksum = seq + ack
		for i in range(0, len(payload)-1):
			checksum += ord(payload[i])
		#flipping the bits
		return ~checksum

	#compares the calculated checksum to the old checksum (-1 means all 1's in binary)
	def check_checksum(self, seq, ack, checksum, payload):
		new_checksum = seq + ack
		for i in range(0, len(payload)-1):
			new_checksum += ord(payload[i])

		if new_checksum + checksum == -1:
			return True
		return False

	# Resends the packet that had a timeout occur
	def resend_packet(self):
		self.packet_count_sent += 1
		print "resending packet A side, num = " + str(self.packet_count)
		checksum = self.create_checksum(self.current_seq_A, self.current_ack_A, self.last_message_A)
		packet = Packet(self.current_seq_A, self.current_ack_A, checksum, self.last_message_A)
		self.message_being_sent = True
		self.to_layer3(self.A, packet)
		self.start_timer(self.A, self.current_time_increment)
	
	# This is the constructor.  Don't touch!
	def __init__(self, num_messages, loss, corrupt, avg_delay, trace, seed):
		super(StudentNetworkSimulator,self).__init__(num_messages, loss, corrupt, avg_delay, trace, seed)
	
	# This routine will be called whenever the upper layer at the sender [A]
	# has a message to send.  It is the job of your protocol to insure that
	# the data in such a message is delivered in-order, and correctly, to
	# the receiving upper layer.
	
	def a_output(self, message):
		#only sends message if one is not being set already
		self.layer5_recv += 1
		if not self.message_being_sent:
			self.packet_count += 1
			self.packet_count_sent += 1
			#grabs data for resending if needed
			self.last_message_A = message.get_data()
			#resets time increment for new packet
			self.current_time_increment = self.time_increment

			#creates checksum and packet
			checksum = self.create_checksum(self.current_seq_A, self.current_ack_A, message.get_data())
			packet = Packet(self.current_seq_A, self.current_ack_A, checksum, str(message.get_data()))

			self.message_being_sent = True
			print "sending packet A side, num = " + str(self.packet_count)
			self.to_layer3(self.A, packet)
			self.start_timer(self.A, self.current_time_increment)

	# This routine will be called whenever a packet sent from the B-side 
	# (i.e. as a result of a toLayer3() being done by a B-side procedure)
	# arrives at the A-side.  "packet" is the (possibly corrupted) packet
	# sent from the B-side.
	
	def a_input(self, packet):
		self.ack_count_recv += 1
		if packet.acknum == self.current_ack_A and self.check_checksum(packet.seqnum, packet.acknum, packet.checksum, packet.payload):
			print "recv ack A side, num = " + str(self.packet_count)
			#stop timer and open up availability to send new packets
			self.message_being_sent = False
			self.stop_timer(self.A)

			#alterate next seq num needed
			if self.current_seq_A == 0:
				self.current_seq_A = 1
				self.current_ack_A = 1
			else:
				self.current_seq_A = 0
				self.current_ack_A = 0
		else:
			if self.check_checksum(packet.seqnum, packet.acknum, packet.checksum, packet.payload) and (packet.acknum == 0 or packet.acknum == 1):
				print "wrong ack recv A side"
			else:
				print "corrupted ack recv A side"



	# This routine will be called when A's timer expires (thus generating a 
	# timer interrupt). You'll probably want to use this routine to control 
	# the retransmission of packets. See startTimer() and stopTimer(), above,
	# for how the timer is started and stopped. 

	def a_timer_interrupt(self):
		#try to resend packet and increase timeout by multiplying by 2
		print "timer interrupt for packet num = " + str(self.packet_count)
		self.timeout_counter += 1
		self.current_time_increment *= 2
		self.message_being_sent = False
		self.resend_packet()

	# This routine will be called once, before any of your other A-side 
	# routines are called. It can be used to do any required
	# initialization (e.g. of member variables you add to control the state
	# of entity A).	

	def a_init(self):
		print "init A"
		self.current_seq_A = 0
		self.current_ack_A = 0
		self.last_message_A = ''
		self.message_being_sent = False

	# This routine will be called whenever a packet sent from the B-side 
	# (i.e. as a result of a toLayer3() being done by an A-side procedure)
	# arrives at the B-side.  "packet" is the (possibly corrupted) packet
	# sent from the A-side.

	def b_input(self, packet):
		#if it is not corrupted and has the right seq num
		self.packet_count_recv += 1
		if self.check_checksum(packet.seqnum, packet.acknum, packet.checksum, packet.payload) and self.current_seq_B == packet.seqnum:
			#doesn't really do a lot but shows message being delivered to layer5
			self.to_layer5(self.B, packet)
			self.layer5_sent += 1

			print "recv packet B side, num = " + str(self.packet_count)
			print "sending ack to A side"

			#creates new checksum and ack packet
			ack_checksum = self.create_checksum(packet.seqnum, packet.acknum, "")
			ack_packet = Packet(packet.seqnum, packet.acknum, ack_checksum)

			#alternate what seq num B is expecting
			if self.current_seq_B == 0:
				self.current_seq_B = 1
				self.current_ack_B = 1
			else:
				self.current_seq_B = 0
				self.current_ack_B = 0
		elif self.check_checksum(packet.seqnum, packet.acknum, packet.checksum, packet.payload) and (packet.seqnum == 0 or packet.seqnum == 1):
			print "recv duplicate packet B side, num = " + str(self.packet_count)
			print "send correct ACK back"
			ack_checksum = self.create_checksum(packet.seqnum, packet.acknum, "")
			ack_packet = Packet(packet.seqnum, packet.acknum, ack_checksum)
		else:
			print "recv corrupted packet on B side"
			print "send wrong ack back"
			if self.current_ack_B == 0:
				wrong_ack_num = 1
			else:
				wrong_ack_num = 0
			ack_packet = Packet(packet.seqnum, wrong_ack_num, packet.checksum)
		self.ack_count_sent += 1
		self.to_layer3(self.B, ack_packet)


	# This routine will be called once, before any of your other B-side 
	# routines are called. It can be used to do any required
	# initialization (e.g. of member variables you add to control the state
	# of entity B).
	def b_init(self):
		print "init B"
		self.current_seq_B = 0
		self.current_ack_B = 0
