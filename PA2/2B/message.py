class Message(object):
	MAXDATASIZE=20
	def __init__(self, input_data=None):
		if(input_data==None):
			self.data=""
		elif len(input_data) > Message.MAXDATASIZE:
			print "Message length exceeding max size. Initializing blank message."
			self.data=""
		else:
			self.data=input_data

	def set_data(self, input_data=None):
		if input_data==None:
			self.data=""
			return bool(0)

		elif len(input_data)>Message.MAXDATASIZE:
			self.data=""
			return bool(0)

		else:
			self.data=input_data
			return bool(1)

	def get_data(self):
		return self.data

