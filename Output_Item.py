class Output_Item:
	
	item=dict()

	def __init__(self):
		self.item={"iom":0,"report":""}
		

	def set_item(self,iom,report):
		self.item.update({"iom":iom})
		self.item.update({"report":report})
		

	def get_IOM(self):
		return self.item.get("iom")

	def get_report(self):		
		return self.item.get("report")