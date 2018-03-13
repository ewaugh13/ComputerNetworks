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

		if self.next_seqnum_A < self.base_A + self.window_size:
			self.packet_count += 1
			self.packet_count_sent += 1

			#TODO (look into this) resets time increment for new packet
			self.current_time_increment = self.time_increment

			#creates checksum and packet
			checksum = self.create_checksum(self.next_seqnum_A, 0, message.get_data())
			packet = Packet(self.next_seqnum_A, 0, checksum, str(message.get_data()))

			self.packet_list.append(packet)
			self.to_layer3(self.A, packet)
			print "sending packet A side, seq_num = " + str(packet.seqnum)

			if self.base_A == self.next_seqnum_A:
				self.start_timer(self.A, self.current_time_increment)
			self.next_seqnum_A += 1
		else:
			print "packet refused"

	# This routine will be called whenever a packet sent from the B-side 
	# (i.e. as a result of a toLayer3() being done by a B-side procedure)
	# arrives at the A-side.  "packet" is the (possibly corrupted) packet
	# sent from the B-side.
	
	def a_input(self, packet):
		self.ack_count_recv += 1
		if self.check_checksum(packet.seqnum, packet.acknum, packet.checksum, packet.payload):
			print "recv ack A side, ack_num = " + str(packet.acknum)

			self.base_A = packet.acknum + 1
			if self.base_A == self.next_seqnum_A:
				#stop timer and open up availability to send new packets
				self.stop_timer(self.A)
			else:
				self.stop_timer(self.A)
				self.current_time_increment = self.time_increment
				self.start_timer(self.A, self.current_time_increment)

		else:
			print "corrupted ack recv A side"



	# This routine will be called when A's timer expires (thus generating a 
	# timer interrupt). You'll probably want to use this routine to control 
	# the retransmission of packets. See startTimer() and stopTimer(), above,
	# for how the timer is started and stopped. 

	def a_timer_interrupt(self):
		#try to resend packet and increase timeout by multiplying by 2
		self.timeout_counter += 1
		self.current_time_increment *= 2

		base_count = self.base_A
		packet = self.packet_list[base_count]
		print "timer interrupt for packet num = " + str(packet.seqnum)
		print "resending packet A side, num = " + str(packet.seqnum)
		self.to_layer3(self.A, self.packet_list[base_count])
		self.start_timer(self.A, self.current_time_increment)

		base_count += 1
		while base_count <= self.next_seqnum_A - 1:
			self.packet_count_sent += 1
			packet = self.packet_list[base_count]
			print "resending packet A side, num = " + str(packet.seqnum)
			self.to_layer3(self.A, self.packet_list[base_count])
			base_count += 1

	# This routine will be called once, before any of your other A-side 
	# routines are called. It can be used to do any required
	# initialization (e.g. of member variables you add to control the state
	# of entity A).	

	def a_init(self):
		print "init A"
		self.base_A = 1
		self.next_seqnum_A = 1
		self.last_message_A = ''
		self.packet_list = [None]
		self.window_size = 8

	# This routine will be called whenever a packet sent from the B-side 
	# (i.e. as a result of a toLayer3() being done by an A-side procedure)
	# arrives at the B-side.  "packet" is the (possibly corrupted) packet
	# sent from the A-side.

	def b_input(self, packet):
		#if it is not corrupted and has the right seq num
		self.packet_count_recv += 1
		if self.check_checksum(packet.seqnum, packet.acknum, packet.checksum, packet.payload) and self.expected_seqnum_B == packet.seqnum:
			#doesn't really do a lot but shows message being delivered to layer5
			self.to_layer5(self.B, packet)
			self.layer5_sent += 1

			print "recv packet B side, seq_num = " + str(packet.seqnum)
			print "sending ack to A side"

			#creates new checksum and ack packet
			ack_checksum = self.create_checksum(self.expected_seqnum_B, self.current_ack_B, "")
			ack_packet = Packet(self.expected_seqnum_B, self.current_ack_B, ack_checksum)

			#increment expected seqnum
			self.expected_seqnum_B += 1
			self.current_ack_B += 1

			self.ack_count_sent += 1
			self.to_layer3(self.B, ack_packet)
		elif self.check_checksum(packet.seqnum, packet.acknum, packet.checksum, packet.payload):
			print "packet seqnum that wasn't expected = " + str(packet.seqnum)
			print "send default back"
			ack_packet = self.B_default_packet
		else:
			print "recv corrupted packet on B side"
			print "send default back"
			ack_packet = self.B_default_packet
		#self.ack_count_sent += 1
		#self.to_layer3(self.B, ack_packet)


	# This routine will be called once, before any of your other B-side 
	# routines are called. It can be used to do any required
	# initialization (e.g. of member variables you add to control the state
	# of entity B).
	def b_init(self):
		print "init B"
		self.expected_seqnum_B = 1
		self.current_ack_B = 1
		default_checksum = self.create_checksum(0, 0, "")
		self.B_default_packet = Packet(0, 0, default_checksum)
