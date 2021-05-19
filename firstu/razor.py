# from __future__ import unicode_literals
import frappe
# from frappe.model.document import Document
from requests.auth import HTTPBasicAuth
import requests
import hmac
import hashlib
import sys
import frappe

@frappe.whitelist()
def webhook(payload):
    
    # req= requests.json()
    # request= req.json() 
    fuel=frappe.db.get_all('Fuel Payment',filters=['amount'])
    
    payment=payload['payment']
    entity=payment['entity']
    status = entity['status']
    wid= entity['id']
    # return wid  
    cash=frappe.db.get_all('Cash Back ledger',filters={'pay_id':wid},fields=['name','pay_id','amount','customer_name'])
    # frappe.throw(frappe.as_json(cash.pay_id))
    if wid :
        for i in cash:
            if wid == i['pay_id']:
                cash_update = frappe.get_doc('Cash Back ledger', i['name'])
                cash_update.pay_status= status
                cash_update.save()
                # cash_update.submit()
                if status == "success":
                    # customer=frappe.db.get_all('Customer',filters={'name':i['name']},fields=['total_cash_back','current_cash_back'])
                    customer=frappe.get_doc('Customer',cash_update.customer_name)  
                    customer.total_cash_back =int(customer.total_cash_back) + int(cash_update.amount)
                    customer.current_cash_back=int(customer.current_cash_back) + int(cash_update.amount)
                    # cash_update.insert()
                    customer.save() 
                # cash_update.insert()
                    cash_update.submit()   
    # frappe.throw(frappe.as_json((wid))
# @frappe.whitelist()
# def create_funds(amount):
#     # return "hai"
#     url =  "https://api.razorpay.com/v1/contacts"
#     headers = {"Content-Type": "application/json"} 
#     auth = HTTPBasicAuth('rzp_test_BNRLROGFnxu3NQ', 'RjCCeIapanWPIgT95oUFQeJ8')
#     body={
#         "name":"Gaurav Kumar",
#         "email":"gaurav.kumar@example.com",
#         "contact":"9123456789",
#         "type":"employee",
#         "reference_id":"Acme Contact ID 12345",
#         "notes":{
#             "notes_key_1":"Tea, Earl Grey, Hot",
#             "notes_key_2":"Tea, Earl Grey… decaf."
#             }
#         }
#     req= requests.post(url,headers=headers,auth=auth,json=body)
#     request= req.json()
#     cid = request["id"]
#     amount = amount
#     fund = fund_account(cid,amount)
#     return fund

# @frappe.whitelist()
# def fund_account(cid,amount):
        
#     url = "https://api.razorpay.com/v1/fund_accounts"
#     headers = {"Content-Type": "application/json"} 
#     auth = HTTPBasicAuth('rzp_test_BNRLROGFnxu3NQ', 'RjCCeIapanWPIgT95oUFQeJ8')
#     body = {
#         "contact_id":cid,
#         "account_type":"bank_account",
#         "bank_account":{
#         "name":"Gaurav Kumar",
#         "ifsc":"HDFC0000053",
#         "account_number":"765432123456789"
#         }
#     }
#     fundrequst = requests.post (url,headers=headers,auth=auth,json=body)
#     request = fundrequst.json()
#     payid = request["id"]
#     amount = amount
#     pay= payout(payid,amount)
#     return pay

# @frappe.whitelist()
# def payout(payid,amount):

#     url="https://api.razorpay.com/v1/payouts"
#     headers={"Content-Type": "application/json"}
#     auth = HTTPBasicAuth('rzp_test_BNRLROGFnxu3NQ', 'RjCCeIapanWPIgT95oUFQeJ8')
#     body ={
#         "account_number": "2323230011738168",
#         "fund_account_id":payid,                                                                    
#         "amount": amount,
#         "currency": "INR",
#         "mode": "IMPS",
#         "purpose": "refund",
#         "queue_if_low_balance": True,
#         "reference_id": "Acme Transaction ID 12345",
#         "narration": "Acme Corp Fund Transfer",
#         "notes": {
#             "notes_key_1":"Tea, Earl Grey, Hot",
#             "notes_key_2":"Tea, Earl Grey… decaf."
#             }
#         }
#     payrequest= requests.post(url, headers=headers , auth=auth , json=body)
#     request=payrequest.json()
#     return request


        