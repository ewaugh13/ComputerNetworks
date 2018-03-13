from Event import Event
from Packet import Packet
from message import Message
from EventListImpl import EventListImpl
import random
import math


"""
MAXDATASIZE: This constant controls the maximum size of the buffer in a Message and in a Packet
"""

class NetworkSimulator(object):
	MAXDATASIZE=20
	#Below Constants are possible events
	TIMERINTERRUPT=0
	FROMLAYER5=1
	FROMLAYER3=2
	#These represent our sender and receiver
	A=0
	B=1
	
	def __init__(self, num_messages,loss, corrupt, avg_delay, trace, seed):
		random.seed(seed)
		self.__max_messages=num_messages
		self.__loss_prob=loss
		self.__corrupt_prob=corrupt
		self.__avg_message_delay=avg_delay
		self.__trace_level=trace
		self.__event_list=EventListImpl()
		self.__n_sim=0
		self.__n_to_layer3=0
		self.__n_lost=0
		self.__n_corrupt=0
		self.__time=float(0)
		

	def run_simulator(self):
		#Perform any student-required initialization
		self.a_init()
		self.b_init()
		#Start the whole thing off by scheduling some data arrival from layer 5
		self.generate_next_arrival()
		#Begin the main loop
		while(1):
			#Get the next event
			_next=self.__event_list.remove_next()
			if _next==None:
				break
			if self.__trace_level>=2:
				print("\n")
				print("EVENT time: %f"%(_next.get_time()))
				print(" type: %d" %(_next.get_type()))
				print(" entity: %d" %(_next.get_entity()))

			#Advance the simulator's time
			self.__time=_next.get_time()
			
			#If maximum message count is reached, exit the main loop
			if self.__n_sim>=self.__max_messages:
				print ""
				print "the number of lost packets/acks = " + str(self.loss_count)
				print "the number of corrupted packets/acks = " + str(self.corrupt_counter)
				print "the number of timeouts = " + str(self.timeout_counter)
				print "the number of packets sent = " + str(self.packet_count_sent - 1) #-1 for 
				print "the number of packets recv = " + str(self.packet_count_recv)
				print "the number of acks sent = " + str(self.ack_count_sent)
				print "the number of acks recv = " + str(self.ack_count_recv)
				print "packets recv from layer5 to A = " + str(self.layer5_recv)
				print "packets sent to layer5 from B = " + str(self.layer5_sent)

				print "packets initialized by A to be sent(non dropped/ignored) = " + str(self.packet_count)
				break

			#Perform the appropriate action based on the event
			if(_next.get_type()==NetworkSimulator.TIMERINTERRUPT):
				if _next.get_entity()==NetworkSimulator.A:
					self.a_timer_interrupt()
				else:
					print "Internal Panic: Timeout for invalid entity"

			elif(_next.get_type()==NetworkSimulator.FROMLAYER3):
				if _next.get_entity()==NetworkSimulator.A:
					self.a_input(_next.get_packet())
				elif (_next.get_entity()==NetworkSimulator.B):
					self.b_input(_next.get_packet())
				else:
					print "Internal Panic: Packet has arrived for unknown entity"

			elif _next.get_type()==NetworkSimulator.FROMLAYER5:
				#If a message has arrived from layer 5, we need to
                #schedule the arrival of the next message
				self.generate_next_arrival()
				next_message=[]
				#Let's generate the contents of this message
				j=chr((self.__n_sim%26)+97)
				next_message=j*NetworkSimulator.MAXDATASIZE
				#Increment the message counter
				self.__n_sim+=1
				#Let the student handle output message
				self.a_output(Message(next_message))

			else:
				print "Internal Panic: Unknown Event Type"
		
	#Generate the next arrival and add it to the event list
	def generate_next_arrival(self):
		if self.__trace_level>2:
			print "generate_next_arrival(): called"

		"""
		arrival time 'x' is uniform on [0, 2*avgMessageDelay]
        having mean of avgMessageDelay.  Should this be made
        into a Gaussian distribution? 
		"""
		x=2*self.__avg_message_delay*random.random()
		_next=Event((self.__time)+x, NetworkSimulator.FROMLAYER5, NetworkSimulator.A)
		self.__event_list.add(_next)

		if self.__trace_level >2:
			print "generate_next_arrival(): time is %f"%(self.__time)
			print "generate_next_arrival(): future time for event %d at entity %d will be %f"%(_next.get_type(), _next.get_entity(), _next.get_time())

	def stop_timer(self, entity):
		if self.__trace_level>2:
			print "stop_timer: stopping timer at %f"%(self.__time)

		timer=self.__event_list.remove_timer(entity)
		#Let the student know they are attempting to stop a non-existant timer
		if(timer==None):
			print "stop_timer: Warning: Unable to cancel your timer"

	def start_timer(self, entity, increment):
		if self.__trace_level>2:
			print "start_timer: starting timer at %f"%(self.__time)

		t=self.__event_list.remove_timer(entity)

		if(t!=None):
			print "start_timer: Warning: Attempting to start an already running timer"
			self.__event_list.add(t)

		else:
			timer=Event(self.__time+increment, NetworkSimulator.TIMERINTERRUPT, entity)
			self.__event_list.add(timer)


	def to_layer3(self, calling_entity, p):
		self.__n_to_layer3+=1
		packet=Packet(p)

		if self.__trace_level > 2:
			print "to_layer3: %s"%(packet)
		#Set our destination
		if calling_entity==NetworkSimulator.A:
			destination=NetworkSimulator.B
		elif calling_entity==NetworkSimulator.B:
			destination=NetworkSimulator.A
		else:
			print("to_layer3: Warning: invalid packet sender")

		#Simulate losses
		if random.random()<self.__loss_prob:
			self.__n_lost+=1
			self.loss_count += 1
			if self.__trace_level>0:
				print "to_layer3: packet being lost"
				return

		#Simulate corruption
		if random.random() < self.__corrupt_prob:
			self.corrupt_counter += 1
			self.__n_corrupt+=1
			if self.__trace_level>0:
				print "to_layer3: packet being corrupted"

			x=random.random()
			if x<0.75:
				payload=packet.get_payload()
				payload="?"+payload[len(payload)-1:]
				packet.set_payload(payload)
			elif x<0.875:
				packet.set_seqnum(abs(random.randint(0,math.pow(2,32))))

			else:
				packet.set_acknum(abs(random.randint(0,math.pow(2,32))))

		# Decide when the packet will arrive.  Since the medium cannot
        # reorder, the packet will arrive 1 to 10 time units after the
        # last packet sent by this sender
		arrival_time=self.__event_list.get_last_packet_time(destination)
		if arrival_time<=0.0:
			arrival_time=self.__time
		arrival_time=arrival_time+1.0+(random.random()*9.0)

		#Finally, create and schedule this event

		if self.__trace_level>2:
			print "to_layer3: scheduling arrival on other side"

		arrival=Event(arrival_time, NetworkSimulator.FROMLAYER3, destination, packet)
		self.__event_list.add(arrival)

	def to_layer5(self, entity, data_sent):
		if self.__trace_level>2:
			print "to_layer5: data received"
			print data_sent

	def get_time(self):
		return self.__time

	def print_event_list(self):
		print self.__event_list

	

