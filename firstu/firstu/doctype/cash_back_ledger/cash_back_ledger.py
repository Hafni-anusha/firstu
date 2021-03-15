# -*- coding: utf-8 -*-
# Copyright (c) 2021, none and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CashBackledger(Document):
	#cashback
	def before_save(self):
		customer=frappe.get_doc('Customer',self.customer_name)
		if self.status == 'Redeemed':
			if int(self.amount) >= int(customer.current_cash_back):
				frappe.throw('Insufficient amount')
			customer.used_cash_back= int (customer.used_cash_back) + int (self.amount)
			customer.current_cash_back= int (customer.current_cash_back) - int(self.amount)
			customer.save(self)

		