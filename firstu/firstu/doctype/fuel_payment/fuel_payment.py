# -*- coding: utf-8 -*-
# Copyright (c) 2021, none and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from requests.auth import HTTPBasicAuth
import requests
import hmac
import hashlib
import sys
import frappe

 

class FuelPayment(Document):
	def before_save(self):
		customer=frappe.get_doc('Customer',self.customer)#loading doctype customer to a variable
		fuelprice=frappe.get_doc('Fuel Price') #loading doctype fuel price to a variable
		trophies=frappe.get_doc('Trophy') #loading doctype trophy to a variable
		if self.membership_type == 'status': #checking condition for true, if yes go to next step
			if self.fuel_type == 'Petrol' : #checking condition for true , if yes execute steps
				self.fuel_in_liters = int(self.amount) / int(fuelprice.fuel_price) # dividing values and appending it to the 'liter' field 
				self.cash_back = (int (fuelprice.fuel_price) - int(fuelprice.firstu_fuel_price)) * int (self.fuel_in_liters) #doing operation to get cash back field
			elif self.fuel_type == 'Diesel': # checking next condition for true , if yes execute following
				self.fuel_in_liters = int(self.amount) / int(fuelprice.diesel_price) #performing operation to get 'liters'
				self.cash_back = (int(fuelprice.fuel_price) - int (fuelprice.firstu_diesel_price ))* (self.fuel_in_liters )#performing operation to get cash back
		else: #else condition for membership type
	 		if self.fuel_type == 'Petrol' : #if condition to check fuel type
	 			self.fuel_in_liters = int(self.amount) / int(fuelprice.fuel_price) #operations to calculate liter of petrol
	 			self.cash_back = (int(fuelprice.fuel_price) - int(fuelprice.petrol_price_for_privilege)) * (self.fuel_in_liters) #operation to calculate cashback for petrol
	 		elif self.fuel_type == 'Diesel': #else condition for fuel check 
	 			self.fuel_in_liters = int(self.amount) / int(fuelprice.diesel_price) #finding liters for diesel
	 			self.cash_back = (int(fuelprice.fuel_price) - int(fuelprice.petrol_price_for_privilege) )* (self.fuel_in_liters) #operation for cashback of diesel
		
		customer.total_cash_back=int(customer.total_cash_back) + int(self.cash_back) #operation to find total cash back
		customer.current_cash_back=int(customer.current_cash_back) + int(self.cash_back) #operation to find current cash back
		customer.save(self) #saving Results

		if customer.refuel == '0': #checking refuel condition
			customer.refuel = int(customer.refuel) + int(trophies.refuel_frequency) #value for refuel  
			customer.total =  int(customer.total) + int(trophies.no_of_trophies) #operations to calculate total trophy
			customer.current = int(customer.current) + int(trophies.no_of_trophies) #operations to find current trophy
			customer.save(self) #save
		else : #above condition fails execute this statement

			customer.refuel  = int(customer.refuel) - 1 #compute customer refuel
		
			customer.save(self) #save document


		trophy_doc = frappe.get_doc({
			'doctype': 'Trophy ledger',
			'customer': self.customer,
			'status': 'Credited',
			'no_of_trophies': trophies.no_of_trophies
			})
		trophy_doc.insert()
		trophy_doc.submit()


		cash_doc = frappe.get_doc({
			'doctype': 'Cash Back ledger',
			'customer_name': self.customer,
			'status': 'Received',
			'amount':self.cash_back
			})
		cash_doc.insert()
		cash_doc.save()

		# fund=fund_account(self)
		# frappe.throw(Customer.name)
		# @frappe.whitelist()
		# def fund_account(self):

	def before_submit(self):
		url ="https://api.razorpay.com/v1/contacts"
		headers={"Content-Type": "application/json"}
		auth=HTTPBasicAuth('rzp_test_BNRLROGFnxu3NQ', 'RjCCeIapanWPIgT95oUFQeJ8')
		body={
			"name":"Gaurav Kumar",
			"email":"gaurav.kumar@example.com",
			"contact":"9123456789",
			"type":"employee",
			"reference_id":"Acme Contact ID 12345",
			"notes":{
				"notes_key_1":"Tea, Earl Grey, Hot",
				"notes_key_2":"Tea, Earl Grey… decaf."
				}
			}
		req= requests.post(url,headers=headers,auth=auth,json=body)
		request= req.json()
		cid = request["id"]
		amount = self.amount
		fund=fund_account(self,cid)
		# return fund
    	
	# @frappe.whitelist()
def fund_account(self,cid):
		
	url ="https://api.razorpay.com/v1/fund_accounts"
	headers = {"Content-Type": "application/json"} 
	auth = HTTPBasicAuth('rzp_test_BNRLROGFnxu3NQ', 'RjCCeIapanWPIgT95oUFQeJ8')
	body = {
		"contact_id":cid,
		"account_type":"bank_account",
		"bank_account":{
		"name":"Gaurav Kumar" ,
		"ifsc":"HDFC0000053",
		"account_number":"765432123456789"
	}
	}
	fundrequst = requests.post (url,headers=headers,auth=auth,json=body)
	request = fundrequst.json()
	payid = request["id"]
	pay=payout(self,payid)
		
def payout(self,payid):
	url="https://api.razorpay.com/v1/payouts"
	headers={"Content-Type": "application/json"}
	auth = HTTPBasicAuth('rzp_test_BNRLROGFnxu3NQ', 'RjCCeIapanWPIgT95oUFQeJ8')
	body ={
		"account_number": "2323230011738168",
		"fund_account_id":payid,                                                                    
		"amount": self.amount*100,
		"currency": "INR",
		"mode": "IMPS",
		"purpose": "refund",
		"queue_if_low_balance": True,
		"reference_id": "Acme Transaction ID 12345",
		"narration": "Acme Corp Fund Transfer",
		"notes": {
			"notes_key_1":"Tea, Earl Grey, Hot",
			"notes_key_2":"Tea, Earl Grey… decaf."
			}
		}
	payrequest= requests.post(url, headers=headers , auth=auth , json=body)
	request=payrequest.json()
	status=request["status"]
	rid=request["id"]
	# frappe.throw(frappe.as_json(request))
	cash_doc = frappe.get_doc({
		'doctype': 'Cash Back ledger',
		'customer_name': self.customer,
		'status': 'Received',
		'pay_id':rid,
		'pay_status': status,
		'amount':self.amount
	})
	cash_doc.insert()
	cash_doc.submit()
	



	