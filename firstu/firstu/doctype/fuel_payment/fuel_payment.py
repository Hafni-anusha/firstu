# -*- coding: utf-8 -*-
# Copyright (c) 2021, none and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class FuelPayment(Document):
	def before_save(self):
		customer=frappe.get_doc('Customer',self.customer)#loading doctype customer to a variable
		fuelprice=frappe.get_doc('Fuel Price') #loading doctype fuel price to a variable
		trophies=frappe.get_doc('Trophy') #loading doctype trophy to a variable
		if self.membership_type == 'status': #checking condition for true, if yes go to next step
			if self.fuel_type == 'Petrol' : #checking condition for true , if yes execute steps
				self.fuel_in_liters = self.amount / fuelprice.fuel_price # dividing values and appending it to the 'liter' field 
				self.cash_back = int (fuelprice.fuel_price - fuelprice.firstu_fuel_price) * int (self.fuel_in_liters) #doing operation to get cash back field
			elif self.fuel_type == 'Diesel': # checking next condition for true , if yes execute following
				self.fuel_in_liters = self.amount / fuelprice.diesel_price #performing operation to get 'liters'
				self.cash_back = (fuelprice.fuel_price - fuelprice.firstu_diesel_price )* self.fuel_in_liters #performing operation to get cash back
		else: #else condition for membership type
	 		if self.fuel_type == 'Petrol' : #if condition to check fuel type
	 			self.fuel_in_liters = self.amount / fuelprice.fuel_price #operations to calculate liter of petrol
	 			self.cash_back = (fuelprice.fuel_price - fuelprice.petrol_price_for_privilege) * self.fuel_in_liters #operation to calculate cashback for petrol
	 		elif self.fuel_type == 'Diesel': #else condition for fuel check 
	 			self.fuel_in_liters = self.amount / fuelprice.diesel_price #finding liters for diesel
	 			self.cash_back = (fuelprice.fuel_price - fuelprice.petrol_price_for_privilege )* self.fuel_in_liters #operation for cashback of diesel
		
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
		cash_doc.submit()

		
		
		
		


	