
class Address:
	def __init__(self,address):
		self.id = address[0]
		self.address_name = address[1]
		self.country = address[2]
		self.city = address[3]
		self.district = address[4]
		self.neighborhood = address[5]
		self.avenue = address[6]
		self.street = address[7]
		self.addr_number = address[8]
		self.zipcode = address[9]
		self.explanation = address[10]

	def get():
		return (self.address_name,self.country,self.city,self.district,self.neighborhood,self.avenue,self.street,self.addr_number,self.zipcode,self.explanation)

class WebUser:
	def __init__(self,webuser):
		self.id = webuser[0]
		self.password_hash = webuser[1]
		self.email = webuser[2]
		self.name = webuser[3]
		self.surname = webuser[4]
		self.is_active = webuser[5]
		self.created_date = webuser[6]

	def get():
		return (self.id,self.password_hash,self.email,self.name,self.surname,self.is_active,self.created_date)

class Admin:
	def __init__(self,admin,webuser_obj,address_obj=None):
		self.id = admin[0]
		self.phone_num = admin[1]
		self.admin_password = admin[2]
		self.address_ref = address_obj
		self.webuser_ref = webuser_obj

	def get():
		return (self.id,self.phone_num,self.admin_password,self.address_ref,self.webuser_ref)

class Member:
	def __init__(self,member):
		from db import get_admin,get_webuser
		self.id = member[0]
		self.confirm_date = member[1]
		self.confirmed_by = get_admin(admin_id=member[2]) 
		self.webuser_ref = get_webuser(id=member[3])

	def get():
		return (self.id,self.confirm_date,self.confirmed_by,self.webuser_ref)

class Transaction:
	def __init__(self,transaction):
		from db import get_admin,get_webuser
		self.id = transaction[0]
		self.created_date = transaction[1]
		self.amount = transaction[2]
		self.created_by = get_webuser(id=transaction[3])
		self.confirmed_by = get_admin(admin_id=transaction[4]) if transaction[4] else None
		self.deleted_by = get_admin(admin_id=transaction[5]) if transaction[5] else None
		self.is_del = transaction[6]

class Debt:
	def __init__(self,debt):
		from db import get_transaction
		self.id = debt[0]
		self.tr_ref = get_transaction(debt[1])
		self.start_period = debt[2]
		self.due_period = debt[3]
		self.number_pay = debt[4]   #taksit sayısı
		self.amount_pay = debt[5]	#toplam ödenen meblağ
		self.paid = debt[6]			#ödenen taksit saysi
		try:
			self.count = debt[7]
		except:
			pass

class Payment:
	def __init__(self,payement):
		from db import get_transaction, get_debts
		self.id = payement[0]
		self.debt_ref = get_debts(id=payement[1])
		self.pay_num = payement[2]
		self.tr_ref = get_transaction(payement[3])