from StudentNetworkSimulator import StudentNetworkSimulator
import sys
import time

def main():
	n_sim=-1
	loss=-1.0
	corrupt=-1.0
	delay=-1.0
	trace=-1
	seed=-1
	_buffer=""

	print "Network Simulator v1.0"
	while(n_sim<1):
		try:
			_buffer=raw_input("Enter number of messages to simulate (> 0):[10] ")
		except Exception:
			print "Error reading input"
			sys.exit(0)


		if(_buffer==""):
			n_sim=10
		else:
			try:
				n_sim=int(_buffer)
			except Exception:
				print "Please enter a valid value."
				n_sim=-1

	while(loss < 0.0):
		try:
			_buffer=raw_input("Enter the paceket loss probablity (0.0 for no loss): [0.0] ")
		except Exception:
			print "Error reading your input"
			sys.exit(0)

		if _buffer=="":
			loss=0.0
		else:
			try:
				loss=float(_buffer)
			except Exception:
				print "Please enter a valid value."
				loss=-1.0

	while(corrupt < 0.0):
		try:
			_buffer=raw_input("Enter the packet corruption probablity (0.0 for no corruption):[0.0] ")
		except Exception:
			print "Error reading your input"
			sys.exit(0)
		if _buffer=="":
			corrupt=0.0
		else:
			try:
				corrupt=float(_buffer)
			except Exception:
				print "Please enter a valid value."
				corrupt=-1.0

	while(delay <=0.0):
		try:
			_buffer=raw_input("Enter the average time between messages from sender's layer 5 (> 0.0): [1000] ")
		except Exception:
			print "Error reading your input"
			sys.exit(0)
		if _buffer=="":
			delay=1000.0
		else:
			try:
				delay=float(_buffer)
			except Exception:
				print "Please enter a valid value."
				delay=-1.0

	while(trace<0):
		try:
			_buffer=raw_input("Enter trace level (>=0): [0] ")
		except Exception:
			print "Error reading your input" 
			sys.exit(0)

		if _buffer=="":
			trace=0
		else:
			try:
				trace=int(_buffer)
			except Exception:
				print "Please enter a valid value."
				trace=-1

	while(seed <1):
		try:
			_buffer=raw_input("Enter random seed: [random] ")
		except Exception:
			print "Error reading your input" 
			sys.exit(0)

		if _buffer=="":
			seed=int(round(time.time() * 1000))
		else:
			try:
				seed=int(_buffer)
			except Exception:
				print "Please enter a valid value."
				seed=-1

	simulator=StudentNetworkSimulator(n_sim, loss, corrupt, delay, trace, seed)
	simulator.run_simulator()

main()