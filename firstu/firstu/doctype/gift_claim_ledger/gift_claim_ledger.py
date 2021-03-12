# -*- coding: utf-8 -*-
# Copyright (c) 2021, none and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Giftclaimledger(Document):
	
	def before_save(self):
		customer=frappe.get_doc('Customer',self.customer)
		#frappe.throw(customer.total)
		
		if int (customer.current) >= int (self.trophies_redeemed):
			if int(self.trophies_redeemed) >= int(customer.current) :
				frappe.throw('dont have enough trophy')
		
			customer.current = int (customer.current) - int (self.trophies_redeemed)
			customer.save(self)

		
		trophy_doc = frappe.get_doc({
			'doctype': 'Trophy ledger',
			'customer': self.customer,
			'status': 'Debited'
			})
		trophy_doc.insert()
