# libraries
# import matplotlib.pyplot as plt
# import matplotlib
# import numpy as np
# import pandas as pd
# import csv
# import seaborn as sns
# from matplotlib import colors
# from collections import OrderedDict 
# from matplotlib.ticker import MaxNLocator
# from matplotlib import gridspec
# from time import sleep
# import sys
# import scipy.stats
# import json

import time
# import os
# from datetime import datetime
# import psutil
from math import floor, ceil, log, sqrt
from statistics import mean, stdev, median
# from queue import Queue as QU
import argparse


# Parsing command line arguments
parser = argparse.ArgumentParser(description="Project 2")
parser.add_argument('-l', '--Lambda', 		type=float, metavar='', required=True, help='the parameter λ of the distribution of interarrival times')
parser.add_argument('-Kc', '--CPU_Queue', 		type=int, 	metavar='', required=True, help='the number K of customers that the CPU queue may hold')
parser.add_argument('-Ki', '--IO_Queue', 		type=int, 	metavar='', required=True, help='the number K of customers that the I/O queue may hold')
parser.add_argument('-C', '--Customers', 	type=int, 	metavar='', required=True, help='the number C of customers served before the program terminates')
parser.add_argument('-L', '--L', 			type=int,   metavar='', required=True, help='an integer L such that L = 0 (runs service disciplines), L>0 (runs web server)')
parser.add_argument('-M', '--mode', 			type=int,   metavar='', required=True, help='1 – FCFS, 2 – LCFS-NP, 3 – SJF-NP, 4 – Prio-NP, 5 – Prio-P')
# parser.add_argument('-i', '--iteration', 			type=int,   metavar='', required=True, help='iteration i')
args = parser.parse_args()

### INPUT GLOBAL PARAMS ####
global LAMBDA
global K
global Kc
global Ki
global C
global L
global M
# global i 


LAMBDA = args.Lambda
Kc = args.CPU_Queue
K = Kc
Ki = args.IO_Queue
C = args.Customers
L = args.L
M = args.mode
# i = args.iteration


global LOG
LOG = 0

global LISTTYPEP
LISTTYPEP = 0

print("*************************\nInput Parameters:\n")
print(" Lambda: {}\n Kcpu: {}\n Ki/o: {}\n C: {}\n".format(LAMBDA, Kc, Ki, C))

# DEFINED variables for ran0 function
IA = 16807
IM = 2147483647
AM = (1.0/IM)
IQ = 127773
IR = 2836
MASK = 123459876 

def ran0(idum):
	k = 0
	ans = 0.0
	idum = idum ^ MASK 
	k= int(idum/IQ)
	idum=IA*(idum-k*IQ)-IR*k
	if idum < 0:
		idum+=IM
	ans= AM*idum
	idum = idum ^ MASK

	return idum, ans;

def expdev(idum, alpha):
	idum, dummy = ran0(idum)
	idum, dummy = ran0(idum) 
	while dummy == 0.0:
		idum, dummy=ran0(idum)
	return idum, -log(dummy)/alpha


def serialize_dictionary(in_resd):
	tmpd = {}

	for k in list(in_resd.keys()):
		if k in [-10, -20, -30, -40]:
			tmpd[k] = in_resd[k]
		else:
			resd = in_resd[k]
			tmp = {"event_type": resd.event_type,
			       "ID": resd.customer_ID,
			       "inter_arrival": resd.inter_arrival,
			       "arrival_time": resd.arrival_time,
			       "service_time": resd.service_time,
			       "departure_time": resd.departure_time,
			       "clock": resd.clock,
			       "served": resd.served,
			       "inqueue": resd.inqueue,
			       "queue_type": resd.queue_type,
			       "departure_generated": resd.departure_generated,
			       "vc": resd.visit_c,
			       "v1": resd.visit_1,
			       "v2": resd.visit_2,
			       "v3": resd.visit_3,
			       "wtc": resd.wt_c,
			       "wt1": resd.wt_1,
			       "wt2": resd.wt_2,
			       "wt3": resd.wt_3,
			       "in_system": resd.in_system,
			       "priority": resd.priority}

			tmpd[k] = tmp

	return tmpd

class NodeCustomer(object):

    def __init__(self, event_type=None, customer_ID=None, inter_arrival=None, next_node=None):
        self.event_type = event_type
        self.customer_ID = customer_ID
        self.inter_arrival = inter_arrival
        self.arrival_time = 0
        self.service_time = 0
        self.departure_time = 0
        self.clock = 0
        self.served = 0
        self.inqueue = False
        self.queue_type = -1
        self.departure_generated = -1
        self.visit_c = 0
        self.visit_1 = 0
        self.visit_2 = 0
        self.visit_3 = 0
        self.wt_c = []
        self.wt_1 = []
        self.wt_2 = []
        self.wt_3 = []
        self.in_system = 0
        self.priority = 0
        self.next_node = next_node

    def get_data(self):
        return self.customer_ID

    def get_id(self):
        return self.customer_ID

    def get_etype(self):
        return self.event_type

    def get_next(self):
        return self.next_node

    def set_next(self, new_next):
        self.next_node = new_next



class LinkedList(object):
	def __init__(self, head=None, event_type=None, clock=None):
		self.head = head
		self.list_size = 0
		self.clock = clock
		self.list_size = 0

	def insert(self, new_node):
		new_node.set_next(self.head)
		self.head = new_node   
		self.list_size += 1
	
	def get_time(self):
		return self.head.clock

	def get_size(self):
		return self.list_size

	def search(self, data):
		current = self.head
		found = False
		while current and found is False:
			if current.get_data() == data:
				found = True
			else:
				current = current.get_next()
		if current is None:
			raise ValueError("Data not in list")
		return current

	def delete(self, data):
		current = self.head
		previous = None
		found = False
		while current and found is False:
			if current.get_data() == data:
				found = True
			else:
				previous = current
				current = current.get_next()
		if current is None:
			raise ValueError("Data not in list")
		
		if previous is None:
			self.head = current.get_next()
			self.list_size -= 1
		else:
			previous.set_next(current.get_next())
			self.list_size -= 1

	def print_list(self):
		current = self.head
		i = 0 
		print("PRINTING LIST OF SIZE:", self.list_size)
		if current != None:
			while 1:
				print("{} PRINTLIST - ID: {}, Type: {}, Priority:{}, CLK:{}, AT: {}, ST: {}, DT: {}, CL: {}".format(\
					i,current.customer_ID, current.event_type, current.priority, current.clock,\
					 current.arrival_time, current.service_time, current.departure_time, current.clock))
				current = current.get_next()
				if current == None:
					break
				i += 1
				if i == self.list_size:
					break


class LinkedList_P(object):
	# global log 
	def __init__(self, head=None, event_type=None, clock=None):
		self.head = NodeCustomer()
		self.list_size = 0
		self.clock = clock
		self.list_size = 0

	def insert(self, new_node):
		# print(self.list_size, new_node.customer_ID)
		if self.list_size == 0:
			self.head.set_next(new_node)
			new_node.set_next(None)
		else:
			if new_node.clock == 17.284573016828233:
				print("FOUND:", new_node.customer_ID, new_node.event_type)
				self.print_list()
			new_node.set_next(self.head.get_next())
			self.head.set_next(new_node)
		
		self.list_size += 1
		if LOG:
			print("IN INSERT:", self.list_size)
		self.print_list()

	def get_time(self):
		return self.head.clock

	def get_size(self):
		return self.list_size

	def search(self, data):
		current = self.head
		found = False
		while current and found is False:
			if current.get_data() == data:
				found = True
			else:
				current = current.get_next()
		if current is None:
			raise ValueError("Data not in list")
		return current

	def delete(self, cust):
		current = self.head.get_next()
		previous = None
		found = False
		while current != None:
			if LOG:
				print("del:" , current.get_id(), current.get_etype(), cust.customer_ID, cust.event_type)
			if current.get_id() == cust.customer_ID and current.get_etype() == cust.event_type:
				found = True
				break
			else:
				previous = current
				current = current.get_next()

		
		
		if found == True:
			if current != None and previous == None:
				if LOG:
					print("del 1")
				self.head.set_next(current.get_next())
				self.list_size -= 1
			elif current != None and previous != None:
				if LOG:
					print("del 2")
				previous.set_next(current.get_next())
				self.list_size -= 1
			elif current == None and previous != None:
				if LOG:
					print("del 3")
				previous.set_next(None)
				self.list_size -= 1
			elif current == None and previous == None:
				if LOG:
					print("del 4 funny")
				# previous.set_next(None)
				# self.list_size -= 1


		elif current is None and found == False:
			print("RASISE")
			raise ValueError("Data not in list")
		# else:

		# 	print("Fell Out")




	def print_list(self):
		if LOG:
			current = self.head.get_next()
			i = 0 
			if current == None:
				print("PRINTLIST- LIST EMPTY")
			if current != None:
				while current != None:
					print("{} PRINTLIST - ID: {}, Type: {}, Priority:{}, QType: {}, CLK:{}, AT: {}, ST: {}, DT: {}, CL: {}".format(\
						i,current.customer_ID, current.event_type, current.priority, current.queue_type, current.clock,\
						 current.arrival_time, current.service_time, current.departure_time, current.clock))
					current = current.get_next()
					# if current == None:
					# 	break
					i += 1
					# if i > 5:
					# 	break


# Other Global Variables
global master_clock
global seed
global event_list
global task
global priority_seed
global seedIO

priority_seed = 500
seed = 5555
seedIO = 6666
# if M == 5:
	# event_list = LinkedList_P()
# else:
	# event_list = LinkedList()
event_list = LinkedList_P()

def assign_priority():
	global priority_seed
	priority_seed, rand_num = ran0(priority_seed)

	if rand_num >= 0 and rand_num < 0.25:
		return 1
	if rand_num >= 0.25 and rand_num < 0.5:
		return 2
	if rand_num >= 0.5 and rand_num < 0.75:
		return 3
	if rand_num >= 0.75 and rand_num < 1.0:
		return 4

def generate_arrival(customer_created, master_clock, mode=None):
	global seed 

	customer_created += 1
	seed, new_arrival_time = expdev(seed, LAMBDA)
	new_customer = NodeCustomer("A", customer_created, new_arrival_time)
	new_customer.inter_arrival = new_arrival_time
	new_customer.arrival_time = master_clock + new_arrival_time
	new_customer.clock = master_clock + new_arrival_time
	if mode == 4 or mode == 5:
		new_customer.priority =  assign_priority()
	return customer_created, new_customer


def generate_departure_time(customer, master_clock, M=None):
	global seed

	if customer.event_type == "D":
		return customer

	seed, new_serive_time = expdev(seed, 1)
	customer.service_time = new_serive_time
	customer.departure_time = new_serive_time + master_clock
	customer.clock = new_serive_time + master_clock
	customer.event_type = "D"
	return customer


def sanatize_event_list():
	global event_list
	print("###SANITIZE:")

	if event_list.list_size > 2:
		current = event_list.head
		sz = 1
		while current != None:
			tmp = current.get_next()
			while tmp != None:
				if tmp.customer_ID == current.customer_ID and tmp.event_type == current.event_type and tmp.clock == current.clock:
					event_list.delete(tmp.customer_ID)
					tmp = current.get_next()
				else:
					tmp = tmp.get_next()
			current = current.get_next()


def add_event_to_list(customer):
	global event_list
	# print("---Insert")
	event_list.insert(customer)
	# event_list.print_list()
	# sanatize_event_list()

def get_next_event_time():
	global event_list

	customer = event_list.head
	if event_list.list_size == 1:
		return customer.clock
	if event_list.list_size > 1:
		next_customer = customer.get_next()
		if customer.clock < next_customer.clock:
			return(customer.clock)
		elif customer.clock >= next_customer.clock:
			return next_customer.clock


def pop_event_from_list():
	global event_list
	global M

	if LISTTYPEP == 0:
		customer = event_list.head
	else:
		customer = event_list.head.get_next()

	if event_list.list_size == 1:
		if LISTTYPEP == 0:
			event_list.delete(customer.customer_ID)
		else:
			event_list.delete(customer)
	if event_list.list_size > 1:
		next_customer = customer.get_next()
		if customer.clock < next_customer.clock:
			if LISTTYPEP == 0:
				event_list.delete(customer.customer_ID)
			else:
				event_list.delete(customer)
			return(customer)
		elif customer.clock >= next_customer.clock:
			if LISTTYPEP == 0:
				event_list.delete(next_customer.customer_ID)
			else:
				event_list.delete(customer)
			return next_customer
	return customer


def pop_event_from_list_P():
	global event_list
	global M

	if LISTTYPEP == 0:
		customer = event_list.head
	else:
		customer = event_list.head.get_next()

	if event_list.list_size == 1:
		if LISTTYPEP == 0:
			event_list.delete(customer.customer_ID)
		else:
			event_list.delete(customer)
	if event_list.list_size > 1:
		next_customer = customer.get_next()
		if customer.clock < next_customer.clock:
			if LISTTYPEP == 0:
				event_list.delete(customer.customer_ID)
			else:
				event_list.delete(customer)
			return(customer)
		elif customer.clock >= next_customer.clock:
			if LISTTYPEP == 0:
				event_list.delete(next_customer.customer_ID)
			else:
				event_list.delete(customer)
			return next_customer
	return customer




  
def printDictionary(pDict):
	keys = list(pDict.keys())
	print("\n\nPrinting Dictionary. Total keys: ", len(keys))
	for k in keys:
		print("CID: {}, Type: {}, INA: {}, SERT: {}, DEPT: {}, CK: {}, INQ:{}, Served: {}".format(\
			k, pDict[k].event_type, pDict[k].inter_arrival, pDict[k].service_time, \
			pDict[k].departure_time, pDict[k].clock, pDict[k].inqueue, pDict[k].served))


def average_service_time_priority_NP(result_dict, C, priority):
	service_time_list = []
	for ID in list(result_dict.keys()):
		if ID <= C:
			if result_dict[ID].served == 1 and result_dict[ID].priority == priority:
				service_time_list.append(result_dict[ID].service_time)
	return round(mean(service_time_list), 3)

def average_waiting_time_priority_NP(result_dict, C, priority):
	waiting_time_list = []
	for ID in list(result_dict.keys()):
		if ID <= C:
			if result_dict[ID].served == 1 and result_dict[ID].priority == priority:
				arrival_mcl = result_dict[ID].arrival_time - result_dict[ID].inter_arrival
				service_mcl = result_dict[ID].departure_time #- result_dict[ID].service_time
				tmp_waiting_time = service_mcl - result_dict[ID].arrival_time 
				waiting_time_list.append(tmp_waiting_time)
	return round(mean(waiting_time_list), 3)


def average_waiting_time_priority_P(result_dict, C, priority):
	waiting_time_list = []
	for ID in list(result_dict.keys()):
		if ID <= C:
			if result_dict[ID].served == 1 and result_dict[ID].priority == priority:
				arrival_mcl = result_dict[ID].arrival_time - result_dict[ID].inter_arrival
				service_mcl = result_dict[ID].departure_time #- result_dict[ID].service_time
				tmp_waiting_time = service_mcl - result_dict[ID].arrival_time 
				waiting_time_list.append(tmp_waiting_time)
	return round(mean(waiting_time_list), 3)


		
def average_service_time(result_dict, C):
	service_time_list = []
	for ID in list(result_dict.keys()):
		if ID <= C:
			if result_dict[ID].served == 1:
				service_time_list.append(result_dict[ID].service_time)
	return round(mean(service_time_list), 3)

def average_waiting_time(result_dict, C):
	waiting_time_list = []
	for ID in list(result_dict.keys()):
		if ID <= C:
			if result_dict[ID].served == 1:
				arrival_mcl = result_dict[ID].arrival_time - result_dict[ID].inter_arrival
				service_mcl = result_dict[ID].departure_time #- result_dict[ID].service_time
				tmp_waiting_time = service_mcl - result_dict[ID].arrival_time 
				waiting_time_list.append(tmp_waiting_time)
	return round(mean(waiting_time_list), 3)



def average_service_time_ci(result_dict, C):
	service_time_list = []
	for ID in list(result_dict.keys()):
		if ID <= C:
			if result_dict[ID].served == 1:
				service_time_list.append(result_dict[ID].service_time)
	return mean_confidence_interval_self(service_time_list)

def average_waiting_time_ci(result_dict, C):
	waiting_time_list = []
	for ID in list(result_dict.keys()):
		if ID <= C:
			if result_dict[ID].served == 1:
				arrival_mcl = result_dict[ID].arrival_time - result_dict[ID].inter_arrival
				service_mcl = result_dict[ID].departure_time #- result_dict[ID].service_time
				tmp_waiting_time = service_mcl - result_dict[ID].arrival_time 
				waiting_time_list.append(tmp_waiting_time)
	
	return mean_confidence_interval_self(waiting_time_list)



def average_waiting_time_sjf(result_dict, C):
	print("\n\n")
	waiting_time_list = []
	for ID in list(result_dict.keys()):
		if ID <= C:
			if result_dict[ID].served == 1:
				# arrival_mcl = result_dict[ID].arrival_time - result_dict[ID].inter_arrival
				service_mcl = result_dict[ID].departure_time #- result_dict[ID].service_time
				tmp_waiting_time = service_mcl - result_dict[ID].arrival_time 
				waiting_time_list.append(tmp_waiting_time)

				customer_event = result_dict[ID]
				# print("CLK: {}\t, ID: {}, Type: {}, IA: {}\t, AT: {}\t, ST: {}\t, DT: {}\t, DIFF: {}".format(\
				# 	customer_event.clock, customer_event.customer_ID, customer_event.event_type,\
				# 	customer_event.inter_arrival, customer_event.arrival_time, \
				#  	customer_event.service_time, customer_event.departure_time, tmp_waiting_time) )


	return round(mean(waiting_time_list), 3)

def average_waiting_time_lcfs(result_dict, C):
	waiting_time_list = []
	ID_list = list(result_dict.keys())
	for i in range(0,len(ID_list)):
		ID = ID_list[i]
		if ID <= C:
			if result_dict[ID].served == 1:
				arrival_mcl = result_dict[ID].arrival_time - result_dict[ID].inter_arrival
				service_mcl = result_dict[ID].departure_time #- result_dict[ID].service_time
				tmp_waiting_time = service_mcl - result_dict[ID].arrival_time 
				# arrival_mcl = result_dict[ID].inter_arrival 
				# service_mcl = result_dict[ID].departure_time 
				# tmp_waiting_time = service_mcl - arrival_mcl - result_dict[ID].service_time
				if tmp_waiting_time > 0:
				# if 1:
					waiting_time_list.append(tmp_waiting_time)

	# print(waiting_time_list)
	return round(mean(waiting_time_list), 3)


def print_stats_for_L_param(result_dict, C, L):
	L = int(L)
	ID_list = [L, L+1, L+10, L+11]
	print("Values of L param:-")
	for ID in ID_list:
		if result_dict[ID].served == 1:
			print("L = {}, Arrival Time: {}, Service Time: {}, Departure Time: {}, Customers in System: {}".format(\
				ID, result_dict[ID].arrival_time, result_dict[ID].service_time, result_dict[ID].departure_time, result_dict[ID].in_system))
		if result_dict[ID].served == -1:
			print("L = {}, Arrival Time: {}, Service Time: {}, Departure Time: {}, Customers in System: {}".format(\
				ID, result_dict[ID].arrival_time, result_dict[ID].service_time, result_dict[ID].arrival_time, result_dict[ID].in_system))








def get_sj_cid(queue):
	ind = -1
	if len(queue) == 0:
		return ind
	elif len(queue) == 1:
		return 0

	for i in range(1, len(queue)):
		if queue[i].service_time > 0:
			if queue[i].service_time >= queue[i-1].service_time:
				ind = i-1
			else:
				ind = i
	return ind

def get_cid_index(queue, customer):
	ind = -1
	if len(queue) == 0:
		return ind
	elif len(queue) == 1 and queue[0].customer_ID == customer.customer_ID:
		return 0

	for i in range(1, len(queue)):
		if queue[i].customer_ID == customer.customer_ID:
			return i
	return ind






global queue_c
global queue_1
global queue_2
global queue_3
global queue_4

global customer_dropped_c
global customer_dropped_1
global customer_dropped_2
global customer_dropped_3
global customer_dropped_4

global customer_inqueue_c
global customer_inqueue_1
global customer_inqueue_2
global customer_inqueue_3
global customer_inqueue_4

global customer_sent_to_c
global customer_sent_to_1
global customer_sent_to_2
global customer_sent_to_3



global result_dictionary


def add_to_queue_priority_NP(customer_event, K):

	global queue_1
	global queue_2
	global queue_3
	global queue_4

	global customer_dropped_1
	global customer_dropped_2
	global customer_dropped_3
	global customer_dropped_4

	global customer_inqueue_1
	global customer_inqueue_2
	global customer_inqueue_3
	global customer_inqueue_4

	global result_dictionary

	K = floor(K/4)



	if customer_event.priority == 1 and customer_inqueue_1 < K:
		queue_1.append(customer_event)	
		customer_inqueue_1 += 1
	elif customer_event.priority == 1 and customer_inqueue_1 >= K:
		customer_dropped_1 += 1
		customer_event.served = -1
		result_dictionary[customer_event.customer_ID] = customer_event



	if customer_event.priority == 2 and customer_inqueue_2 < K:
		queue_2.append(customer_event)	
		customer_inqueue_2 += 1
	elif customer_event.priority == 2 and customer_inqueue_2 >= K:
		customer_dropped_2 += 1
		customer_event.served = -1
		result_dictionary[customer_event.customer_ID] = customer_event
	
	if customer_event.priority == 3 and customer_inqueue_3 < K:
		queue_3.append(customer_event)	
		customer_inqueue_3 += 1
	elif customer_event.priority == 3 and customer_inqueue_3 >= K:
		customer_dropped_3 += 1
		customer_event.served = -1
		result_dictionary[customer_event.customer_ID] = customer_event
	

	if customer_event.priority == 4 and customer_inqueue_4 < K:
		queue_4.append(customer_event)	
		customer_inqueue_4 += 1
	elif customer_event.priority == 4 and customer_inqueue_4 >= K:
		customer_dropped_4 += 1
		customer_event.served = -1
		result_dictionary[customer_event.customer_ID] = customer_event


def pop_from_queue_P(cust):
	global queue_1
	global queue_2
	global queue_3
	global queue_4

	global customer_inqueue_1
	global customer_inqueue_2
	global customer_inqueue_3
	global customer_inqueue_4

	priority = cust.priority

	# print(">> POPING Q: ID: {}, TYPE: {}, Priority:{}".format(cust.customer_ID, cust.event_type, priority))
	# print("> {}, {}, {}, {}".format(customer_inqueue_1, customer_inqueue_2, customer_inqueue_3, customer_inqueue_4))

	# if cust.event_type == "D":
	# 	print("* Q EVENT type D. Nothing to pop.")
	# 	return None

	if priority == 1 and len(queue_1) > 0:
		tmp_customer = queue_1.pop(0)
		tmp_customer.service_time = cust.service_time
		tmp_customer.departure_time = cust.departure_time
		customer_inqueue_1 -= 1
		# print("> {}, {}, {}, {}".format(customer_inqueue_1, customer_inqueue_2, customer_inqueue_3, customer_inqueue_4))
		return tmp_customer

	if priority == 2 and len(queue_2) > 0:
		tmp_customer = queue_2.pop(0)
		tmp_customer.service_time = cust.service_time
		tmp_customer.departure_time = cust.departure_time
		customer_inqueue_2 -= 1
		# print("> {}, {}, {}, {}".format(customer_inqueue_1, customer_inqueue_2, customer_inqueue_3, customer_inqueue_4))
		return tmp_customer

	if priority == 3 and len(queue_3) > 0:
		tmp_customer = queue_3.pop(0)
		tmp_customer.service_time = cust.service_time
		tmp_customer.departure_time = cust.departure_time
		customer_inqueue_3 -= 1
		# print("> {}, {}, {}, {}".format(customer_inqueue_1, customer_inqueue_2, customer_inqueue_3, customer_inqueue_4))
		return tmp_customer

	if priority == 4 and len(queue_4) > 0:
		tmp_customer = queue_4.pop(0)
		tmp_customer.service_time = cust.service_time
		tmp_customer.departure_time = cust.departure_time
		customer_inqueue_4 -= 1
		# print("> {}, {}, {}, {}".format(customer_inqueue_1, customer_inqueue_2, customer_inqueue_3, customer_inqueue_4))
		return tmp_customer
	# print(">< {}, {}, {}, {}".format(customer_inqueue_1, customer_inqueue_2, customer_inqueue_3, customer_inqueue_4))


	# if customer_inqueue_1 > 0:
	# 	tmp_customer = queue_1.pop(0)
	# 	customer_inqueue_1 -= 1
	# 	return tmp_customer
	# elif customer_inqueue_2 > 0:
	# 	tmp_customer = queue_2.pop(0)
	# 	customer_inqueue_2 -= 1
	# 	return tmp_customer
	# elif customer_inqueue_3 > 0:
	# 	tmp_customer = queue_3.pop(0)
	# 	customer_inqueue_3 -= 1
	# 	return tmp_customer
	# elif customer_inqueue_4 > 0:
	# 	tmp_customer = queue_4.pop(0)
	# 	customer_inqueue_4 -= 1
	# 	return tmp_customer






def stop_service_and_enqueue(stop_cust, mcl, K):

	global queue_1
	global queue_2
	global queue_3
	global queue_4

	global customer_dropped_1
	global customer_dropped_2
	global customer_dropped_3
	global customer_dropped_4

	global customer_inqueue_1
	global customer_inqueue_2
	global customer_inqueue_3
	global customer_inqueue_4

	global result_dictionary

	K = floor(K/4)

	stop_cust.service_time = stop_cust.departure_time - mcl
	stop_cust.departure_time = mcl + stop_cust.service_time
	stop_cust.clock = stop_cust.departure_time
	stop_cust.event_type = "P"


	if stop_cust.priority == 1 and customer_inqueue_1 < K:
		queue_1.insert(0, stop_cust)	
		customer_inqueue_1 += 1
	elif stop_cust.priority == 1 and customer_inqueue_1 >= K:
		customer_dropped_1 += 1
		stop_cust.served = -1
		result_dictionary[stop_cust.customer_ID] = stop_cust

	if stop_cust.priority == 2 and customer_inqueue_2 < K:
		queue_2.insert(0, stop_cust)	
		customer_inqueue_2 += 1
	elif stop_cust.priority == 2 and customer_inqueue_2 >= K:
		customer_dropped_2 += 1
		stop_cust.served = -1
		result_dictionary[stop_cust.customer_ID] = stop_cust
	
	if stop_cust.priority == 3 and customer_inqueue_3 < K:
		queue_3.insert(0, stop_cust)	
		customer_inqueue_3 += 1
	elif stop_cust.priority == 3 and customer_inqueue_3 >= K:
		customer_dropped_3 += 1
		stop_cust.served = -1
		result_dictionary[stop_cust.customer_ID] = stop_cust
	

	if stop_cust.priority == 4 and customer_inqueue_4 < K:
		queue_4.insert(0, stop_cust)	
		customer_inqueue_4 += 1
	elif stop_cust.priority == 4 and customer_inqueue_4 >= K:
		customer_dropped_4 += 1
		stop_cust.served = -1
		result_dictionary[stop_cust.customer_ID] = stop_cust




def io_or_exit(cust):
	global priority_seed
	priority_seed, rand_num = ran0(priority_seed)

	global Ki

	global queue_1
	global queue_2
	global queue_3

	global customer_dropped_1
	global customer_dropped_2
	global customer_dropped_3
	
	global customer_inqueue_1
	global customer_inqueue_2
	global customer_inqueue_3

	global customer_sent_to_1
	global customer_sent_to_2
	global customer_sent_to_3

	global result_dictionary

	io_e = 0
	if rand_num >= 0 and rand_num < 0.7:
		io_e = 0
	if rand_num >= 0.7 and rand_num < 0.8:
		io_e = 1
	if rand_num >= 0.8 and rand_num < 0.9:
		io_e = 2
	if rand_num >= 0.9 and rand_num < 1.0:
		io_e = 3

	if LOG:
		print("ro: {}, cid: {}, etype: {}".format(io_e, cust.customer_ID, cust.event_type))

	if io_e == 1 and len(queue_1) < Ki:
		cust.inqueue = True
		cust.queue_type = 1
		cust.event_type = "A1"
		cust.visit_1 += 1
		cust.arrival_time = cust.departure_time
		cust.departure_generated = 0
		customer_sent_to_1 += 1
		queue_1.append(cust)
		customer_inqueue_1 += 1
		add_event_to_list(cust)
		result_dictionary[cust.customer_ID] = cust
	elif io_e == 1 and len(queue_1) >= Ki:
		cust.inqueue = False
		cust.queue_type = 1
		cust.served = -1
		cust.departure_time = 0
		customer_dropped_1 += 1
		result_dictionary[cust.customer_ID] = cust

	if io_e == 2 and len(queue_2) < Ki:
		cust.inqueue = True
		cust.queue_type = 2
		cust.event_type = "A2"
		cust.visit_2 += 1
		cust.arrival_time = cust.departure_time
		cust.departure_generated = 0
		customer_sent_to_2 += 1
		queue_2.append(cust)
		customer_inqueue_2 += 1
		add_event_to_list(cust)
		result_dictionary[cust.customer_ID] = cust
	elif io_e == 2 and len(queue_2) >= Ki:
		cust.inqueue = False
		cust.queue_type = 2
		cust.served = -1
		cust.departure_time = 0
		customer_dropped_2 += 1
		result_dictionary[cust.customer_ID] = cust

	if io_e == 3 and len(queue_3) < Ki:
		cust.inqueue = True
		cust.queue_type = 3
		cust.event_type = "A3"
		cust.visit_3 += 1
		cust.arrival_time = cust.departure_time
		cust.departure_generated = 0
		customer_sent_to_3 += 1
		queue_3.append(cust)
		customer_inqueue_3 += 1
		add_event_to_list(cust)
		result_dictionary[cust.customer_ID] = cust
	elif io_e == 3 and len(queue_3) >= Ki:
		cust.inqueue = False
		cust.queue_type = 3
		cust.served = -1
		cust.departure_time = 0
		customer_dropped_3 += 1
		result_dictionary[cust.customer_ID] = cust


	return io_e

		



# cpu = 0, io 1,2,3
def update_waiting_time(cust,cio):
	wt = cust.departure_time - cust.service_time - cust.arrival_time
	if cio == 0:
		cust.wt_c.append(wt)
	if cio == 1:
		cust.wt_1.append(wt)
	if cio == 2:
		cust.wt_2.append(wt)
	if cio == 3:
		cust.wt_3.append(wt)

	return cust



def generate_departure_time_ws(customer, master_clock, cio):
	global seed
	global seedIO
	global LAMBDA

	
	if cio == 0:
		seed, new_serive_time = expdev(seed, 1)
		customer.service_time = new_serive_time
		customer.departure_time = new_serive_time + master_clock
		customer.clock = new_serive_time + master_clock
		customer.departure_generated = 0
		customer.event_type = "D"
	else:
		e_type = "D"+str(cio)
		seedIO, new_serive_time = expdev(seedIO, 0.5)
		customer.departure_generated = cio
		customer.service_time = new_serive_time
		customer.departure_time = new_serive_time + master_clock
		customer.clock = new_serive_time + master_clock
		customer.event_type = e_type

	return customer



def pop_event_from_list_ws():
	global event_list
	global M

	# customer = event_list.head.get_next()
	# if event_list.list_size == 1:
	# 	event_list.delete(customer)
	# if event_list.list_size > 1:
	# 	size = 0
	# 	next_customer = customer.get_next()
	# 	while size < event_list.list_size - 1:
	# 		if customer.clock > next_customer.clock:
	# 			customer = next_customer

	# 		next_customer = next_customer.get_next()
	# 		size += 1
	# 	event_list.delete(customer)

	# print("-- After Deletion")
	# event_list.print_list()

	# return customer	

	customer = event_list.head.get_next()
	if event_list.list_size == 1:
		event_list.delete(customer)
	if event_list.list_size > 1:
		size = 0
		next_customer = customer.get_next()
		while next_customer != None:
			if customer.clock >= next_customer.clock:
				customer = next_customer
			
			next_customer = next_customer.get_next()
			size += 1
		event_list.delete(customer)

	if LOG:
		print("-- After Deletion")
	customer.set_next(None)
	event_list.print_list()

	return customer	
	

	# customer = event_list.head
	# if event_list.list_size == 1:
	# 	event_list.delete(customer.customer_ID)
	# if event_list.list_size > 1:
	# 	next_customer = customer.get_next()
	# 	if customer.clock < next_customer.clock:
	# 		event_list.delete(customer.customer_ID)
	# 		return(customer)
	# 	elif customer.clock >= next_customer.clock:
	# 		event_list.delete(next_customer.customer_ID)
	# 		return next_customer
	# return customer
def queue_cpu_append(cust):
	global queue_c
	ins_ind = -1
	if len(queue_c) == 0:
		queue_c.append(cust)
		ins_ind = 0
	else:
		ins = 0
		for i in range(0, len(queue_c)):
			if cust.clock <= queue_c[i].clock:
				queue_c.insert(i,cust)
				ins = 1
				ins_ind = i
				break

		if ins == 0:
			queue_c.append(cust)
			ins_ind = len(queue_c)-1
	return ins_ind 


def webserver_avgWaiting(in_res_d):

	keys = list(in_res_d.keys())
	tmp_keys = []
	for k in keys:
		tmp_keys.append(int(k))

	tmp_keys.sort()

	# print(keys)
	# exit(1)

	wt_all = []
	wt_c = []
	wt_1 = []
	wt_2 = []
	wt_3 = []
	# print("Total Keys: ", len(tmp_keys), tmp_keys[0])
	for i in range(1003, len(tmp_keys)):
		# k = str(tmp_keys[i])
		k = tmp_keys[i]
		res_d = in_res_d[k]
		if res_d["served"] == 1:
			# print(k)
			wt_c.append(mean(res_d["wtc"]) if len(res_d["wtc"]) > 0 else 0)
			wt_1.append(mean(res_d["wt1"]) if len(res_d["wt1"]) > 0 else 0)
			wt_2.append(mean(res_d["wt2"]) if len(res_d["wt2"]) > 0 else 0)
			wt_3.append(mean(res_d["wt3"]) if len(res_d["wt3"]) > 0 else 0)
			wt_all.append(wt_c[-1] + wt_1[-1] + wt_2[-1] + wt_3[-1])

	return [mean(wt_all), abs(mean(wt_c)), mean(wt_1), mean(wt_2), mean(wt_3)]



def web_server(ro):
	global LAMBDA
	global Kc
	global K
	global Ki
	global C
	global L
	global event_list
	global task

	global queue_c
	global queue_1
	global queue_2
	global queue_3

	global customer_dropped_1
	global customer_dropped_2
	global customer_dropped_3
	global customer_dropped_c

	global customer_inqueue_1
	global customer_inqueue_2
	global customer_inqueue_3
	global customer_inqueue_c

	global customer_sent_to_c
	global customer_sent_to_1
	global customer_sent_to_2
	global customer_sent_to_3



	global result_dictionary

	LAMBDA = ro

	# event_list = LinkedList()

	ts1 = time.time()

	# Local variables initialization
	master_clock = 0
	customer_created = 0
	customer_served = 0
	
	customer_dropped_c = 0
	customer_dropped_1 = 0
	customer_dropped_2 = 0
	customer_dropped_3 = 0	
	
	customer_inqueue_c = 0
	customer_inqueue_1 = 0
	customer_inqueue_2 = 0
	customer_inqueue_3 = 0

	customer_sent_to_c = 0
	customer_sent_to_1 = 0
	customer_sent_to_2 = 0
	customer_sent_to_3 = 0

	# Local variables initialization
	master_clock     = 0
	customer_created = 0
	customer_served  = 0
	
	result_dictionary = {}
	
	queue_c = [] 
	queue_1 = [] 
	queue_2 = [] 
	queue_3 = [] 

	ts1 = time.time()

	# Simulation initialization
	customer_created, new_customer = generate_arrival(customer_created, master_clock)
	add_event_to_list(new_customer)
	result_dictionary[new_customer.customer_ID] = new_customer
	first = 0
	# Main loop of simulation terminating when all the C customers served
	while customer_served < C:
		# if customer_inqueue_c == 0:
		if customer_inqueue_c+customer_inqueue_1+customer_inqueue_2+customer_inqueue_3 == 0:
			if LOG:
				print("\n\n##\n\n")
			if first == 0:
				customer_event = pop_event_from_list_ws()
				master_clock = customer_event.clock
				customer_event.inqueue = True
				customer_event.queue_type = 0
				customer_event.visit_c += 1
				queue_c.append(customer_event)	
				customer_inqueue_c += 1

				customer_event = generate_departure_time_ws(customer_event, master_clock,0)
				add_event_to_list(customer_event)	
				result_dictionary[customer_event.customer_ID] = customer_event		
				customer_created, new_customer = generate_arrival(customer_created, master_clock)
				add_event_to_list(new_customer)
				result_dictionary[new_customer.customer_ID] = new_customer
				first = 0
			else:

				customer_event = pop_event_from_list_ws()
				master_clock = customer_event.clock
				customer_event.inqueue = True

				if customer_event.event_type in ["A1", "A2", "A3"] and LOG == 1:
					print("\n\n\n*************\n\n\n")

				if customer_event.event_type == "A":
					
					customer_event.queue_type = 0
					customer_event.visit_c += 1
					queue_c.append(customer_event)	
					customer_inqueue_c += 1
					customer_event = generate_departure_time_ws(customer_event, master_clock,0)
					add_event_to_list(customer_event)	
				if customer_event.event_type == "A1":
					customer_event.queue_type = 1
					customer_event.visit_1 += 1
					queue_1.append(customer_event)	
					customer_inqueue_1 += 1
					customer_event = generate_departure_time_ws(customer_event, master_clock,1)
					add_event_to_list(customer_event)	
				if customer_event.event_type == "A2":
					customer_event.queue_type = 2
					customer_event.visit_2 += 1
					queue_2.append(customer_event)	
					customer_inqueue_2 += 1
					customer_event = generate_departure_time_ws(customer_event, master_clock,2)
					add_event_to_list(customer_event)	
				if customer_event.event_type == "A3":
					customer_event.queue_type = 3
					customer_event.visit_3 += 1
					queue_3.append(customer_event)	
					customer_inqueue_3 += 1
					customer_event = generate_departure_time_ws(customer_event, master_clock,3)
					add_event_to_list(customer_event)	

			
				result_dictionary[customer_event.customer_ID] = customer_event		
				customer_created, new_customer = generate_arrival(customer_created, master_clock)
				add_event_to_list(new_customer)
				result_dictionary[new_customer.customer_ID] = new_customer


		else:
			if LOG:
				print("\n-------------")
				print(")) QLEN: ", len(queue_c), len(queue_1), len(queue_2), len(queue_3))
			event_list.print_list()
			customer_event = pop_event_from_list_ws()
			master_clock = customer_event.clock

			if LOG:
				print("\nCLK: {}, ID: {}, Type: {}, QType:{}, CLK:{}, IA: {}, AT: {}, ST: {}, DT: {}, QUEUE: {}, {}, {}, {}, DROPS: {}, {}, {}, {}:: {}".format(\
					customer_event.clock, customer_event.customer_ID, customer_event.event_type, customer_event.queue_type, customer_event.clock, \
					customer_event.inter_arrival, customer_event.arrival_time, \
				 customer_event.service_time, customer_event.departure_time,
				 customer_inqueue_c, customer_inqueue_1, customer_inqueue_2, customer_inqueue_3,\
				 customer_dropped_c, customer_dropped_1, customer_dropped_2, customer_dropped_3, event_list.list_size) )

			if customer_event.event_type == "A":
				if customer_inqueue_c < K:
					customer_event.inqueue = True
					customer_event.queue_type = 0
					queue_c.append(customer_event)
					customer_inqueue_c += 1
					if len(queue_c) == 1:
						customer_event = generate_departure_time_ws(customer_event, master_clock,0)
						add_event_to_list(customer_event)	
				else:
					customer_dropped_c += 1
					customer_event.served = -1
					result_dictionary[customer_event.customer_ID] = customer_event

				customer_created, new_customer = generate_arrival(customer_created, master_clock)
				add_event_to_list(new_customer)
				result_dictionary[new_customer.customer_ID] = new_customer

			# IO QUEUE STUFF
			elif customer_event.event_type in ["D1", "D2", "D3"]:
				if LOG:
					print("** IO STUFF:")
				if customer_event.event_type == "D1":
					cust = queue_1.pop(0)
					customer_inqueue_1 -= 1
					update_waiting_time(cust,1)

				if customer_event.event_type == "D2":
					cust = queue_2.pop(0)
					update_waiting_time(cust,2)
					customer_inqueue_2 -= 1

				if customer_event.event_type == "D3":
					cust = queue_3.pop(0)
					update_waiting_time(cust,3)
					customer_inqueue_3 -= 1

				cust.departure_generated = -1
				ins_ind = -1
				if len(queue_c) < Kc:
					cust.inqueue = True
					cust.queue_type = 0
					cust.event_type = "A"
					cust.visit_c += 1
					cust.arrival_time = cust.departure_time
					customer_sent_to_c += 1
					# Append at appropriate place
					ins_ind = queue_cpu_append(cust)
					# queue_c.append(cust)
					customer_inqueue_c += 1
					# add_event_to_list(cust)
					result_dictionary[cust.customer_ID] = cust
				elif len(queue_c) >= Kc:
					cust.inqueue = False
					cust.served = -1
					cust.departure_time = 0
					customer_dropped_c += 1
					result_dictionary[cust.customer_ID] = cust

				# CHECK QUEUE FOR ENTRY AND GENERATE DEPARTURE
				if len(queue_c) > 0:
					customer_event = queue_c[0]
					if customer_event.departure_generated == -1:
						queue_c[0].customer_departing = 0
						if ins_ind == 0:
							customer_event.departure_generated = 0
							customer_event.arrival_time = customer_event.departure_time
							customer_event.clock = customer_event.departure_time
							customer_event.event_type = "D"
							if LOG:
								print("*Que pop 0 self", customer_event.customer_ID, customer_event.event_type)
							add_event_to_list(customer_event)
						else:
							customer_event = generate_departure_time_ws(customer_event, master_clock,0)
							if LOG:
								print("*Que pop 0", customer_event.customer_ID, customer_event.event_type)
							add_event_to_list(customer_event)
						result_dictionary[customer_event.customer_ID] = customer_event

			# CPU STUFF
			elif customer_event.event_type == "D": 
				if LOG:
					print(")) QLEN: ", len(queue_c), len(queue_1), len(queue_2), len(queue_3))

				customer_departing = queue_c.pop(0)
				customer_inqueue_c -= 1
				
				# Test for r for i/o or exit
				update_waiting_time(customer_departing,0)

				ret = io_or_exit(customer_departing)

				if LOG:
					print("** RETURN:", ret)
					print(")) QLEN1: ", len(queue_c), len(queue_1), len(queue_2), len(queue_3))
				
				if ret == 0: # Customer existing system
					customer_event.served = 1
					customer_event.inqueue = False
					customer_event.queue_type = -1
					customer_event.in_system = customer_inqueue_c
					result_dictionary[customer_event.customer_ID] = customer_event
					customer_served += 1

				
				# CHECK QUEUE FOR ENTRY AND GENERATE DEPARTURE
				if len(queue_c) > 0:
					customer_event = queue_c[0]
					if customer_event.departure_generated == -1:
						queue_c[0].customer_departing = 0
						customer_event = generate_departure_time_ws(customer_event, master_clock,0)
						if LOG:
							print("Que pop 0", customer_event.customer_ID, customer_event.event_type)
						add_event_to_list(customer_event)
						result_dictionary[customer_event.customer_ID] = customer_event
				
			elif customer_event.event_type in ["A1", "A2", "A3"]:
				if len(queue_1) > 0 and customer_event.event_type == "A1":
					io_cust = queue_1[0]
					if io_cust.departure_generated == 0:
						queue_1[0].customer_departing = 1
						io_cust = generate_departure_time_ws(io_cust, master_clock,1)
						if LOG:
							print("Que pop 1", io_cust.customer_ID, io_cust.event_type)
						add_event_to_list(io_cust)
						result_dictionary[io_cust.customer_ID] = io_cust

				if len(queue_2) > 0 and customer_event.event_type == "A2":
					io_cust = queue_2[0]
					if io_cust.departure_generated == 0:
						queue_2[0].customer_departing = 2
						if LOG:
							print("Que pop h2", io_cust.customer_ID, io_cust.event_type, io_cust.customer_ID)
						io_cust = generate_departure_time_ws(io_cust, master_clock,2)
						if LOG:
							print("Que pop 2", io_cust.customer_ID, io_cust.event_type, io_cust.customer_ID)
						add_event_to_list(io_cust)
						result_dictionary[io_cust.customer_ID] = io_cust

				if len(queue_3) > 0 and customer_event.event_type == "A3":
					io_cust = queue_3[0]
					if io_cust.departure_generated == 0:
						queue_3[0].customer_departing = 3
						io_cust = generate_departure_time_ws(io_cust, master_clock,3)
						if LOG:
							print("Que pop 3", io_cust.customer_ID, io_cust.event_type)
						add_event_to_list(io_cust)
						result_dictionary[io_cust.customer_ID] = io_cust

				# CHECK QUEUE FOR ENTRY AND GENERATE DEPARTURE
				if len(queue_c) > 0:
					customer_event = queue_c[0]
					if customer_event.departure_generated == -1:
						queue_c[0].customer_departing = 0
						customer_event = generate_departure_time_ws(customer_event, master_clock,0)
						if LOG:
							print("*Que pop 0", customer_event.customer_ID, customer_event.event_type)
						add_event_to_list(customer_event)
						result_dictionary[customer_event.customer_ID] = customer_event
			


	rt = time.time() - ts1


	# PRINTING OF RESULTS OF STANDARD OUTPUT
	# if customer_served > 1000:
	# 	CLR = float(customer_dropped)/float(customer_served - 1000)
	# else:
	# 	CLR = 0

	clr_sys = 0
	clr_cpu = 0
	clr_1 = 0
	clr_2 = 0
	clr_3 = 0

	clr = float(customer_dropped_c+customer_dropped_1+customer_dropped_2+customer_dropped_3)/float(customer_created)
	clr_cpu = float(customer_dropped_c)/float(customer_dropped_c+customer_sent_to_c)
	clr_1 = float(customer_dropped_1)/float(customer_dropped_1+customer_sent_to_1)
	clr_2 = float(customer_dropped_2)/float(customer_dropped_2+customer_sent_to_2)
	clr_3 = float(customer_dropped_3)/float(customer_dropped_3+customer_sent_to_3)
	


	print("\n************************\n WEB SERVER FCFS")
	print(" Master Clock: {}\n".format(master_clock))

	print("Average service time for C served customer is {} units".format(average_service_time(result_dictionary, C)))
	# print("Average waiting time for C served customer is {} units\n".format(average_waiting_time(result_dictionary, C)))
	# print(customer_sent_to_c, customer_sent_to_1, customer_sent_to_2, customer_sent_to_3)
	# print_stats_for_L_param(result_dictionary, C, L)
	result_dictionary[-10] = [clr, clr_cpu, clr_1, clr_2, clr_3]
	result_dictionary[-20] = rt
	result_dictionary[-30] = master_clock

	# print("CLR: SYS:{}, CPU:{}, 1:{}, 2:{}, 3:{}".format(clr, clr_cpu, clr_1, clr_2, clr_3))

	result_dictionary = serialize_dictionary(result_dictionary)

	ret = webserver_avgWaiting(result_dictionary)
	print("Average system waiting time for C served customer is {} units".format(ret[0]))
	print("Average CPU waiting time for C served customer is {} units".format(ret[1]))
	print("Average I/O 1 waiting time for C served customer is {} units".format(ret[2]))
	print("Average I/O 2 waiting time for C served customer is {} units".format(ret[3]))
	print("Average I/O 3 waiting time for C served customer is {} units\n".format(ret[4]))

	return result_dictionary












def start_fcfs():
	global LAMBDA
	global K
	global C
	global L
	global event_list
	global task

	# Local variables initialization
	master_clock = 0
	customer_created = 0
	customer_served = 0
	customer_dropped = 0
	customer_inqueue = 0
	result_dictionary = {}
	queue = [] 

	ts1 = time.time()

	# Simulation initialization
	customer_created, new_customer = generate_arrival(customer_created, master_clock)
	add_event_to_list(new_customer)
	result_dictionary[new_customer.customer_ID] = new_customer

	# Main loop of simulation terminating when all the C customers served
	while customer_served < C:
		if customer_inqueue == 0:
			customer_event = pop_event_from_list()
			master_clock = customer_event.clock
			customer_event.inqueue = True
			queue.append(customer_event)	
			customer_inqueue += 1

			customer_event = generate_departure_time(customer_event, master_clock)
			add_event_to_list(customer_event)	
			result_dictionary[customer_event.customer_ID] = customer_event		
			customer_created, new_customer = generate_arrival(customer_created, master_clock)
			add_event_to_list(new_customer)
			result_dictionary[new_customer.customer_ID] = new_customer
		else:
			customer_event = pop_event_from_list()
			master_clock = customer_event.clock

			if customer_event.event_type == "A":
				if customer_inqueue < K:
					customer_event.inqueue = True
					queue.append(customer_event)
					customer_inqueue += 1
				else:
					customer_dropped += 1
					customer_event.served = -1
					result_dictionary[customer_event.customer_ID] = customer_event

				customer_created, new_customer = generate_arrival(customer_created, master_clock)
				add_event_to_list(new_customer)
				result_dictionary[new_customer.customer_ID] = new_customer
			else:
				customer_departing = queue.pop(0)
				customer_inqueue -= 1
				customer_departing.served = 1
				customer_departing.inqueue = False
				customer_departing.in_system = customer_inqueue
				result_dictionary[customer_departing.customer_ID] = customer_departing

				if len(queue) > 0:
					customer_event = queue[0]
					customer_event = generate_departure_time(customer_event, master_clock)
					add_event_to_list(customer_event)
					result_dictionary[customer_event.customer_ID] = customer_event
				customer_served += 1


	rt = time.time() - ts1


	# PRINTING OF RESULTS OF STANDARD OUTPUT
	if customer_served > 1000:
		CLR = float(customer_dropped)/float(customer_served+customer_dropped - 1000)
	else:
		CLR = 0


	print("\n************************\n Service Dicipline: FCFS")
	print(" Master Clock: {}\n".format(master_clock))

	print("Average service time for C served customer is {} units".format(average_service_time(result_dictionary, C)))
	print("Average waiting time for C served customer is {} units\n".format(average_waiting_time(result_dictionary, C)))

	# x,y,z = average_service_time_ci(result_dictionary, C)
	# print("Average service time is {} and +/- CI is {} and {} for C served customers".format(x,y,z))
	# x,y,z = average_waiting_time_ci(result_dictionary, C)
	# print("Average waiting time is {} and +/- CI is {} and {} for C served customers\n".format(x,y,z))


	result_dictionary[-10] = CLR
	result_dictionary[-20] = rt
	result_dictionary[-30] = master_clock

	result_dictionary = serialize_dictionary(result_dictionary)

	return result_dictionary


def start_lcfs():
	global LAMBDA
	global K
	global C
	global L
	global event_list
	global task

	# Local variables initialization
	master_clock = 0
	customer_created = 0
	customer_served = 0
	customer_dropped = 0
	customer_inqueue = 0
	result_dictionary = {}
	queue = [] 

	ts1 = time.time()

	# Simulation initialization
	customer_created, new_customer = generate_arrival(customer_created, master_clock)
	add_event_to_list(new_customer)
	result_dictionary[new_customer.customer_ID] = new_customer

	# Main loop of simulation terminating when all the C customers served
	while customer_served < C:
		# print(master_clock)
		if customer_inqueue == 0:
			customer_event = pop_event_from_list()
			master_clock = customer_event.clock
			customer_event.inqueue = True
			queue.append(customer_event)	
			customer_inqueue += 1

			customer_event = generate_departure_time(customer_event, master_clock)
			add_event_to_list(customer_event)	
			result_dictionary[customer_event.customer_ID] = customer_event		
			customer_created, new_customer = generate_arrival(customer_created, master_clock)
			add_event_to_list(new_customer)
			result_dictionary[new_customer.customer_ID] = new_customer
		else:
			customer_event = pop_event_from_list()
			master_clock = customer_event.clock

			if customer_event.event_type == "A":
				if customer_inqueue < K:
					customer_event.inqueue = True
					queue.append(customer_event)
					customer_inqueue += 1
				else:
					customer_dropped += 1
					customer_event.served = -1 # -1 indicates dropped
					result_dictionary[customer_event.customer_ID] = customer_event

				customer_created, new_customer = generate_arrival(customer_created, master_clock)
				add_event_to_list(new_customer)
				result_dictionary[new_customer.customer_ID] = new_customer
			else:
				# customer_departing = queue[-1]
				# del queue[-1]
				# customer_inqueue -= 1
				# customer_departing.served = 1
				# customer_departing.inqueue = False
				# customer_departing.in_system = customer_inqueue
				# result_dictionary[customer_departing.customer_ID] = customer_departing

				ind = get_cid_index(queue, customer_event)
				customer_departing = queue[ind]
				del queue[ind]

				customer_departing.departure_time = customer_event.departure_time				
				customer_departing.service_time = customer_event.service_time
				customer_inqueue -= 1
				customer_departing.served = 1
				customer_departing.inqueue = False
				customer_departing.in_system = customer_inqueue
				result_dictionary[customer_departing.customer_ID] = customer_departing

				if len(queue) > 0:
					customer_event = queue[-1]
					customer_event = generate_departure_time(customer_event, master_clock)
					add_event_to_list(customer_event)
					result_dictionary[customer_event.customer_ID] = customer_event
				customer_served += 1


	# if task == 5:
	# 	ts2 = time.time()
	# 	print("MCL: ", master_clock)
	# 	return ts2-ts1


	# if task == 1:
	# 	return float(customer_dropped)/float(customer_created)
	# if task == 4:
	# 	return average_waiting_time(result_dictionary, C)

	rt = time.time() - ts1

	# PRINTING OF RESULTS OF STANDARD OUTPUT
	if customer_served > 1000:
		CLR = float(customer_dropped)/float(customer_served+customer_dropped - 1000)
	else:
		CLR = 0

	print("\n************************\n Service Dicipline: LCFS")
	print(" Master Clock: {}\n".format(master_clock))

	print("Average service time for C served customer is {} units".format(average_service_time(result_dictionary, C)))
	print("Average waiting time for C served customer is {} units\n".format(average_waiting_time(result_dictionary, C)))
	# print_stats_for_L_param(result_dictionary, C, L)

	result_dictionary[-10] = CLR
	result_dictionary[-20] = rt
	result_dictionary[-30] = master_clock

	result_dictionary = serialize_dictionary(result_dictionary)

	return result_dictionary

	
def start_sjf():
	global LAMBDA
	global K
	global C
	global L
	global event_list
	global task

	# Local variables initialization
	master_clock = 0
	customer_created = 0
	customer_served = 0
	customer_dropped = 0
	customer_inqueue = 0
	result_dictionary = {}
	queue = [] 

	ts1 = time.time()

	# Simulation initialization
	customer_created, new_customer = generate_arrival(customer_created, master_clock)
	add_event_to_list(new_customer)
	result_dictionary[new_customer.customer_ID] = new_customer

	# Main loop of simulation terminating when all the C customers served
	while customer_served < C:
		if customer_inqueue == 0:
			customer_event = pop_event_from_list()
			master_clock = customer_event.clock
			customer_event.inqueue = True
			queue.append(customer_event)	
			customer_inqueue += 1

			customer_event = generate_departure_time(customer_event, master_clock)
			add_event_to_list(customer_event)	
			result_dictionary[customer_event.customer_ID] = customer_event		
			customer_created, new_customer = generate_arrival(customer_created, master_clock)
			add_event_to_list(new_customer)
			result_dictionary[new_customer.customer_ID] = new_customer
		else:
			customer_event = pop_event_from_list()
			master_clock = customer_event.clock


			if customer_event.event_type == "A":
				if customer_inqueue < K:
					customer_event.inqueue = True
					queue.append(customer_event)
					customer_inqueue += 1
				else:
					customer_dropped += 1
					customer_event.served = -1
					result_dictionary[customer_event.customer_ID] = customer_event

				customer_created, new_customer = generate_arrival(customer_created, master_clock)
				add_event_to_list(new_customer)
				result_dictionary[new_customer.customer_ID] = new_customer
			else:

				ind = get_cid_index(queue, customer_event)
				customer_departing = queue[ind]
				del queue[ind]

				customer_departing.departure_time = customer_event.departure_time				
				customer_departing.service_time = customer_event.service_time
				customer_inqueue -= 1
				customer_departing.served = 1
				customer_departing.inqueue = False
				customer_departing.in_system = customer_inqueue
				result_dictionary[customer_departing.customer_ID] = customer_departing

				if len(queue) > 0:
					customer_event = queue[get_sj_cid(queue)]
					customer_event = generate_departure_time(customer_event, master_clock)
					add_event_to_list(customer_event)
					result_dictionary[customer_event.customer_ID] = customer_event
				customer_served += 1

			# print("CLK: {}, ID: {}, Type: {}, IA: {}, AT: {}, ST: {}, DT: {}".format(\
			# 	customer_event.clock, customer_event.customer_ID, customer_event.event_type,\
			# 	customer_event.inter_arrival, customer_event.arrival_time, \
			#  customer_event.service_time, customer_event.departure_time) )



	# if task == 5:
	# 	ts2 = time.time()
	# 	print("MCL: ", master_clock)
	# 	return ts2-ts1


	# if task == 1:
	# 	return float(customer_dropped)/float(customer_created)
	# if task == 4:
	# 	return average_waiting_time(result_dictionary, C)
	rt = time.time() - ts1

	# PRINTING OF RESULTS OF STANDARD OUTPUT
	if customer_served > 1000:
		CLR = float(customer_dropped)/float(customer_served+customer_dropped - 1000)
	else:
		CLR = 0

	print("\n************************\n Service Dicipline: SJF")
	print(" Master Clock: {}\n".format(master_clock))

	print("Average service time for C served customer is {} units".format(average_service_time(result_dictionary, C)))
	print("Average waiting time for C served customer is {} units\n".format(average_waiting_time(result_dictionary, C)))
	# print_stats_for_L_param(result_dictionary, C, L)

	result_dictionary[-10] = CLR
	result_dictionary[-20] = rt
	result_dictionary[-30] = master_clock

	result_dictionary = serialize_dictionary(result_dictionary)

	return result_dictionary


def start_priority_NP(mode):
	global LAMBDA
	global K
	global C
	global L
	global event_list
	global task

	global queue_1
	global queue_2
	global queue_3
	global queue_4

	global customer_dropped_1
	global customer_dropped_2
	global customer_dropped_3
	global customer_dropped_4

	global customer_inqueue_1
	global customer_inqueue_2
	global customer_inqueue_3
	global customer_inqueue_4

	global result_dictionary



	# Local variables initialization
	master_clock = 0
	customer_created = 0
	customer_served = 0
	customer_dropped_1 = 0
	customer_dropped_2 = 0
	customer_dropped_3 = 0
	customer_dropped_4 = 0
	customer_inqueue_1 = 0
	customer_inqueue_2 = 0
	customer_inqueue_3 = 0
	customer_inqueue_4 = 0

	result_dictionary = {}
	
	queue_1 = [] 
	queue_2 = [] 
	queue_3 = [] 
	queue_4 = [] 

	ts1 = time.time()

	# Simulation initialization
	customer_created, new_customer = generate_arrival(customer_created, master_clock, mode)
	add_event_to_list(new_customer)
	result_dictionary[new_customer.customer_ID] = new_customer

	# Main loop of simulation terminating when all the C customers served
	customer_inqueue = customer_inqueue_1+customer_inqueue_2+customer_inqueue_3+customer_inqueue_4
	while customer_served < C:
		if customer_inqueue == 0:
			customer_event = pop_event_from_list()
			master_clock = customer_event.clock
			customer_event.inqueue = True
			add_to_queue_priority_NP(customer_event, K)

			customer_event = generate_departure_time(customer_event, master_clock)
			add_event_to_list(customer_event)	
			result_dictionary[customer_event.customer_ID] = customer_event		
			customer_created, new_customer = generate_arrival(customer_created, master_clock, mode)
			add_event_to_list(new_customer)
			result_dictionary[new_customer.customer_ID] = new_customer

			customer_inqueue = customer_inqueue_1+customer_inqueue_2+customer_inqueue_3+customer_inqueue_4

		else:
			customer_event = pop_event_from_list()

			# print("\n\n\n---------\n\nAfter Pop size: ", event_list.list_size)

			master_clock = customer_event.clock

			# print("CLK: {}, ID: {}, Type: {}, Priority:{}, CLK:{}, IA: {}, AT: {}, ST: {}, DT: {}, DROPS: {}, {}, {}, {}:: {}".format(\
			# 	customer_event.clock, customer_event.customer_ID, customer_event.event_type, customer_event.priority, customer_event.clock, \
			# 	customer_event.inter_arrival, customer_event.arrival_time, \
			#  customer_event.service_time, customer_event.departure_time,
			#  customer_dropped_1, customer_dropped_2, customer_dropped_3, customer_dropped_4, event_list.list_size) )

			if customer_event.event_type == "A":
				add_to_queue_priority_NP(customer_event, K)				
				
				customer_created, new_customer = generate_arrival(customer_created, master_clock, mode)
				add_event_to_list(new_customer)
				result_dictionary[new_customer.customer_ID] = new_customer

				customer_inqueue = customer_inqueue_1+customer_inqueue_2+customer_inqueue_3+customer_inqueue_4

			else:
				# print("condition D")
				customer_departing = pop_from_queue_P(customer_event)
				customer_departing.served = 1
				customer_departing.inqueue = False
				customer_departing.in_system = customer_inqueue
				result_dictionary[customer_departing.customer_ID] = customer_departing

				if len(queue_1) > 0:
					customer_event = queue_1[0]
					customer_event = generate_departure_time(customer_event, master_clock)
					add_event_to_list(customer_event)
					result_dictionary[customer_event.customer_ID] = customer_event
				elif len(queue_2) > 0:
					customer_event = queue_2[0]
					customer_event = generate_departure_time(customer_event, master_clock)
					add_event_to_list(customer_event)
					result_dictionary[customer_event.customer_ID] = customer_event
				elif len(queue_3) > 0:
					customer_event = queue_3[0]
					customer_event = generate_departure_time(customer_event, master_clock)
					add_event_to_list(customer_event)
					result_dictionary[customer_event.customer_ID] = customer_event
				elif len(queue_4) > 0:
					customer_event = queue_4[0]
					customer_event = generate_departure_time(customer_event, master_clock)
					add_event_to_list(customer_event)
					result_dictionary[customer_event.customer_ID] = customer_event
				
				customer_served += 1

			customer_inqueue = customer_inqueue_1+customer_inqueue_2+customer_inqueue_3+customer_inqueue_4


	# if task == 5:
	# 	ts2 = time.time()
	# 	print("MCL: ", master_clock)
	# 	return ts2-ts1


	# if task == 1:
	# 	return float(customer_dropped)/float(customer_created)
	# if task == 4:
	# 	return average_waiting_time(result_dictionary, C)


	# # PRINTING OF RESULTS OF STANDARD OUTPUT
	# CLR = float(customer_dropped)/float(customer_created)

	rt = time.time() - ts1

	# CLR
	served_1 = 0 
	served_2 = 0
	served_3 = 0
	served_4 = 0

	if customer_served > 1000:
		CLR = float(customer_dropped_1+customer_dropped_2+customer_dropped_3+customer_dropped_4)/float(customer_served+customer_dropped_1+customer_dropped_2+customer_dropped_3+customer_dropped_4 - 1000)
		id_list = list(result_dictionary.keys())
		for ID in range(1000, len(id_list)):
			if result_dictionary[ID].served == 1:
				if result_dictionary[ID].priority == 1:
					served_1 += 1
				if result_dictionary[ID].priority == 2:
					served_2 += 1
				if result_dictionary[ID].priority == 3:
					served_3 += 1
				if result_dictionary[ID].priority == 4:
					served_4 += 1

		CLR1 = float(customer_dropped_1)/float(served_1+customer_dropped_1)
		CLR2 = float(customer_dropped_2)/float(served_2+customer_dropped_2)
		CLR3 = float(customer_dropped_3)/float(served_3+customer_dropped_3)
		CLR4 = float(customer_dropped_4)/float(served_4+customer_dropped_4)

	else:
		CLR = 0
		CLR1 = 0
		CLR2 = 0
		CLR3 = 0
		CLR4 = 0

	print("\n************************\n Service Dicipline: Priority Non-Preemptive")
	print(" Master Clock: {}\n".format(master_clock))
	wt1 = average_waiting_time_priority_NP(result_dictionary, C, 1)
	wt2 = average_waiting_time_priority_NP(result_dictionary, C, 2)
	wt3 = average_waiting_time_priority_NP(result_dictionary, C, 3)
	wt4 = average_waiting_time_priority_NP(result_dictionary, C, 4)

	print("Average service time for C served customer in priority queue 1 is {} units".format(average_service_time_priority_NP(result_dictionary, C, 1)))
	print("Average service time for C served customer in priority queue 2 is {} units".format(average_service_time_priority_NP(result_dictionary, C, 2)))
	print("Average service time for C served customer in priority queue 3 is {} units".format(average_service_time_priority_NP(result_dictionary, C, 3)))
	print("Average service time for C served customer in priority queue 4 is {} units\n".format(average_service_time_priority_NP(result_dictionary, C, 4)))

	# print("Average waiting time for C served customer in priority queue 1 is {} units".format(average_waiting_time_priority_NP(result_dictionary, C, 1)))
	# print("Average waiting time for C served customer in priority queue 2 is {} units".format(average_waiting_time_priority_NP(result_dictionary, C, 2)))
	# print("Average waiting time for C served customer in priority queue 3 is {} units".format(average_waiting_time_priority_NP(result_dictionary, C, 3)))
	# print("Average waiting time for C served customer in priority queue 4 is {} units\n".format(average_waiting_time_priority_NP(result_dictionary, C, 4)))
	print("Average waiting time for C served customer in priority queue 1 is {} units".format(wt1))
	print("Average waiting time for C served customer in priority queue 2 is {} units".format(wt2))
	print("Average waiting time for C served customer in priority queue 3 is {} units".format(wt3))
	print("Average waiting time for C served customer in priority queue 4 is {} units\n".format(wt4))

	# print_stats_for_L_param(result_dictionary, C, L)
	result_dictionary[-10] = [CLR, CLR1, CLR2, CLR3, CLR4]
	result_dictionary[-20] = rt
	result_dictionary[-30] = master_clock
	result_dictionary[-40] = [wt1,wt2,wt3,wt4]

	result_dictionary = serialize_dictionary(result_dictionary)

	return result_dictionary



def start_priority_P(mode):

	global LAMBDA
	global K
	global C
	global L
	global event_list
	global task
	global M

	global queue_1
	global queue_2
	global queue_3
	global queue_4

	global customer_dropped_1
	global customer_dropped_2
	global customer_dropped_3
	global customer_dropped_4

	global customer_inqueue_1
	global customer_inqueue_2
	global customer_inqueue_3
	global customer_inqueue_4

	global result_dictionary

	ts1 = time.time()

	# Local variables initialization
	master_clock = 0
	customer_created = 0
	customer_served = 0
	customer_dropped_1 = 0
	customer_dropped_2 = 0
	customer_dropped_3 = 0
	customer_dropped_4 = 0
	customer_inqueue_1 = 0
	customer_inqueue_2 = 0
	customer_inqueue_3 = 0
	customer_inqueue_4 = 0

	result_dictionary = {}
	
	queue_1 = [] 
	queue_2 = [] 
	queue_3 = [] 
	queue_4 = [] 

	ts1 = time.time()

	# Simulation initialization
	customer_created, new_customer = generate_arrival(customer_created, master_clock, mode)
	add_event_to_list(new_customer)
	result_dictionary[new_customer.customer_ID] = new_customer

	# Main loop of simulation terminating when all the C customers served
	customer_inqueue = customer_inqueue_1+customer_inqueue_2+customer_inqueue_3+customer_inqueue_4
	once = 1
	while customer_served < C:
		if customer_inqueue == 0 and once:
			once = 1
			customer_event = pop_event_from_list_P()
			master_clock = customer_event.clock
			customer_event.inqueue = True
			add_to_queue_priority_NP(customer_event, K)

			customer_event = generate_departure_time(customer_event, master_clock)
			add_event_to_list(customer_event)	
			result_dictionary[customer_event.customer_ID] = customer_event		
			customer_created, new_customer = generate_arrival(customer_created, master_clock, mode)
			add_event_to_list(new_customer)
			# add_to_queue_priority_NP(customer_event, K)		
			result_dictionary[new_customer.customer_ID] = new_customer

			customer_inqueue = customer_inqueue_1+customer_inqueue_2+customer_inqueue_3+customer_inqueue_4

		else:
			customer_event = pop_event_from_list_P()
			# print("\n\n\n---------\n\nAfter Pop size: ", event_list.list_size)
			new_dep = None

			# print("CLK: {}, ID: {}, Type: {}, Priority:{}, CLK:{}, IA: {}, AT: {}, ST: {}, DT: {}, DROPS: {}, {}, {}, {}:: {}".format(\
			# 	customer_event.clock, customer_event.customer_ID, customer_event.event_type, customer_event.priority, customer_event.clock, \
			# 	customer_event.inter_arrival, customer_event.arrival_time, \
			#  customer_event.service_time, customer_event.departure_time,
			#  customer_dropped_1, customer_dropped_2, customer_dropped_3, customer_dropped_4, event_list.list_size) )


			if customer_event.event_type == "A":
				# print("ARR")
				master_clock = customer_event.clock
				add_to_queue_priority_NP(customer_event, K)		
				# print("ARR> {}, {}, {}, {}".format(customer_inqueue_1, customer_inqueue_2, customer_inqueue_3, customer_inqueue_4))		
				
				customer_created, new_customer = generate_arrival(customer_created, master_clock, mode)
				add_event_to_list(new_customer)
				result_dictionary[new_customer.customer_ID] = new_customer

				customer_inqueue = customer_inqueue_1+customer_inqueue_2+customer_inqueue_3+customer_inqueue_4

			else:
				
				customer_departing = pop_from_queue_P(customer_event)
				# print("\nBEFORE D")
				# event_list.print_list()

				if len(queue_1) > 0:
					# print("1: ", queue_1[0])
					new_dep = queue_1[0]
				elif len(queue_2) > 0:
					# print("2: ", queue_2)
					new_dep = queue_2[0]
				elif len(queue_3) > 0:
					# print("3: ", queue_3)
					new_dep = queue_3[0]
				elif len(queue_4) > 0:
					# print("4: ", queue_4)
					new_dep = queue_4[0]

				# print("\nAfter D")
				# event_list.print_list()

				if new_dep != None and (customer_event.event_type == "D" or customer_event.event_type == "P") and new_dep.priority < customer_event.priority and new_dep.arrival_time < customer_event.departure_time: 
					new_dep = generate_departure_time(new_dep, master_clock, M)
					add_event_to_list(new_dep)
					result_dictionary[new_dep.customer_ID] = new_dep

					master_clock = new_dep.clock
					# print("\n\n\n\n\n\n\n\n\n\nSTOP: ", customer_event)

					stop_service_and_enqueue(customer_event, master_clock, K)

				elif customer_event.event_type == "D":
				# if customer_event.event_type == "D" or customer_event.event_type == "P":
				# if customer_event.event_type == "D":
				# if 1:
					# if new_dep != None:
					# 	print("PLAY CE ND: ", customer_event.priority, new_dep.priority, customer_event.clock, new_dep.clock)
					# else:
					# 	print("PLAY CE: ", customer_event.priority, customer_event.clock)
					
					customer_departing.served = 1
					customer_departing.inqueue = False
					customer_departing.in_system = customer_inqueue
					customer_departing.clock = master_clock
					result_dictionary[customer_departing.customer_ID] = customer_departing

					master_clock = customer_event.clock

					if new_dep != None:
						new_dep = generate_departure_time(new_dep, master_clock)
						add_event_to_list(new_dep)
						result_dictionary[new_dep.customer_ID] = new_dep


					customer_served += 1

			customer_inqueue = customer_inqueue_1+customer_inqueue_2+customer_inqueue_3+customer_inqueue_4


	rt = time.time() - ts1


	# CLR
	served_1 = 0 
	served_2 = 0
	served_3 = 0
	served_4 = 0

	if customer_served > 1000:
		CLR = float(customer_dropped_1+customer_dropped_2+customer_dropped_3+customer_dropped_4)/float(customer_served+customer_dropped_1+customer_dropped_2+customer_dropped_3+customer_dropped_4 - 1000)
		id_list = list(result_dictionary.keys())
		for ID in range(1000, len(id_list)):
			if result_dictionary[ID].served == 1:
				if result_dictionary[ID].priority == 1:
					served_1 += 1
				if result_dictionary[ID].priority == 2:
					served_2 += 1
				if result_dictionary[ID].priority == 3:
					served_3 += 1
				if result_dictionary[ID].priority == 4:
					served_4 += 1

		CLR1 = float(customer_dropped_1)/float(served_1+customer_dropped_1)
		CLR2 = float(customer_dropped_2)/float(served_2+customer_dropped_2)
		CLR3 = float(customer_dropped_3)/float(served_3+customer_dropped_3)
		CLR4 = float(customer_dropped_4)/float(served_4+customer_dropped_4)

	else:
		CLR = 0
		CLR1 = 0
		CLR2 = 0
		CLR3 = 0
		CLR4 = 0

	print("\n************************\n Service Dicipline: Priority Preemptive")
	print(" Master Clock: {}\n".format(master_clock))

	wt1 = average_waiting_time_priority_NP(result_dictionary, C, 1)
	wt2 = average_waiting_time_priority_NP(result_dictionary, C, 2)
	wt3 = average_waiting_time_priority_NP(result_dictionary, C, 3)
	wt4 = average_waiting_time_priority_NP(result_dictionary, C, 4)

	print("Average service time for C served customer in priority queue 1 is {} units".format(average_service_time_priority_NP(result_dictionary, C, 1)))
	print("Average service time for C served customer in priority queue 2 is {} units".format(average_service_time_priority_NP(result_dictionary, C, 2)))
	print("Average service time for C served customer in priority queue 3 is {} units".format(average_service_time_priority_NP(result_dictionary, C, 3)))
	print("Average service time for C served customer in priority queue 4 is {} units\n".format(average_service_time_priority_NP(result_dictionary, C, 4)))

	# print("Average waiting time for C served customer in priority queue 1 is {} units".format(average_waiting_time_priority_NP(result_dictionary, C, 1)))
	# print("Average waiting time for C served customer in priority queue 2 is {} units".format(average_waiting_time_priority_NP(result_dictionary, C, 2)))
	# print("Average waiting time for C served customer in priority queue 3 is {} units".format(average_waiting_time_priority_NP(result_dictionary, C, 3)))
	# print("Average waiting time for C served customer in priority queue 4 is {} units\n".format(average_waiting_time_priority_NP(result_dictionary, C, 4)))
	print("Average waiting time for C served customer in priority queue 1 is {} units".format(wt1))
	print("Average waiting time for C served customer in priority queue 2 is {} units".format(wt2))
	print("Average waiting time for C served customer in priority queue 3 is {} units".format(wt3))
	print("Average waiting time for C served customer in priority queue 4 is {} units\n".format(wt4))

	# print_stats_for_L_param(result_dictionary, C, L)
	result_dictionary[-10] = [CLR, CLR1, CLR2, CLR3, CLR4]
	result_dictionary[-20] = rt
	result_dictionary[-30] = master_clock
	result_dictionary[-40] = [wt1,wt2,wt3,wt4]

	result_dictionary = serialize_dictionary(result_dictionary)


	return result_dictionary




def print_customer(customer):
	print("CID: {}, INTA: {}".format(customer.customer_ID, customer.inter_arrival))



def mean_confidence_interval(data, confidence=0.95):
    a = np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h


def mean_confidence_interval_self(data, confidence=0.95):
    a = np.array(data)
    n = len(a)
    m = mean(a)
    sdev = stdev(a)
    sq = sqrt(len(data)-1)
    alpha = 1.96
    low = m - alpha*(sdev/sq)
    high = m + alpha*(sdev/sq)

    # low = alpha*(sdev/sq)
    # high = alpha*(sdev/sq)

    return m, low, high



def extract_waiting_time_list(result_dict):
	waiting_time_list = []
	id_list = list(result_dict.keys())
	# print(id_list)
	id_list.sort()
	for ID in range(1000, len(id_list)):
		# if result_dict[ID].served == 1 and result_dict[ID].departure_time > 0:
		if result_dict[ID].served == 1:
			arrival_mcl = result_dict[ID].arrival_time - result_dict[ID].inter_arrival
			service_mcl = result_dict[ID].departure_time - result_dict[ID].service_time
			tmp_waiting_time = service_mcl - result_dict[ID].arrival_time 
			
			# if tmp_waiting_time >= 0:
				# waiting_time_list.append(tmp_waiting_time)
			waiting_time_list.append(tmp_waiting_time)

			# if tmp_waiting_time < 0:
			# 	print(ID, service_mcl - result_dict[ID].arrival_time,  result_dict[ID].arrival_time, service_mcl, result_dict[ID].departure_time, result_dict[ID].service_time)

	print("stats: ", min(waiting_time_list), len(waiting_time_list), len(id_list))
	return waiting_time_list

def extract_clr(result_dict):
	waiting_time_list = []
	id_list = list(result_dict.keys())
	# print(id_list)
	id_list.sort()
	dropped = 0
	served = 0
	for ID in range(1000, len(id_list)):
		if result_dict[ID].served == -1:
			dropped += 1
			
	clr = dropped/(len(id_list) - 1000)

	return clr 

def extract_waiting_time_list_P(result_dict, priority):
	waiting_time_list = []
	id_list = list(result_dict.keys())
	# print(id_list)
	id_list.sort()
	for ID in range(1000, len(id_list)):
		# if result_dict[ID].served == 1 and result_dict[ID].departure_time > 0:
		if result_dict[ID].served == 1 and result_dict[ID].priority == priority:
			arrival_mcl = result_dict[ID].arrival_time - result_dict[ID].inter_arrival
			service_mcl = result_dict[ID].departure_time - result_dict[ID].service_time
			tmp_waiting_time = service_mcl - result_dict[ID].arrival_time 
			
			# if tmp_waiting_time >= 0:
				# waiting_time_list.append(tmp_waiting_time)
			waiting_time_list.append(tmp_waiting_time)

			# if tmp_waiting_time < 0:
			# 	print(ID, service_mcl - result_dict[ID].arrival_time,  result_dict[ID].arrival_time, service_mcl, result_dict[ID].departure_time, result_dict[ID].service_time)

	print("stats: ", min(waiting_time_list), len(waiting_time_list), len(id_list))
	return waiting_time_list





def run_wb():
	global event_list
	global i 
	global LAMBDA

	event_list = LinkedList_P()
	ret_dict = web_server(LAMBDA)
	with open("data/web_"+str(LAMBDA)+"_"+str(i), 'w') as fp:
		json.dump(ret_dict, fp)		


def run_sd():
	global event_list
	global i 
	global LAMBDA

	# if LISTTYPEP:
	# 	event_list = LinkedList_P()
	# else:
	# 	event_list = LinkedList()
	
	# ret_dict = start_fcfs()
	# with open("dataSD1/fcfs_"+str(LAMBDA)+"_"+str(i), 'w') as fp:
	# 	json.dump(ret_dict, fp)		

	if LISTTYPEP:
		event_list = LinkedList_P()
	else:
		event_list = LinkedList()

	ret_dict = start_lcfs()
	with open("dataSD1/lcfs_"+str(LAMBDA)+"_"+str(i), 'w') as fp:
		json.dump(ret_dict, fp)	

	if LISTTYPEP:
		event_list = LinkedList_P()
	else:
		event_list = LinkedList()

	ret_dict = start_sjf()
	with open("dataSD1/sjf_"+str(LAMBDA)+"_"+str(i), 'w') as fp:
		json.dump(ret_dict, fp)		


	if LISTTYPEP:
		event_list = LinkedList_P()
	else:
		event_list = LinkedList()

	ret_dict = start_priority_NP(4)
	with open("dataSD1/pnp_"+str(LAMBDA)+"_"+str(i), 'w') as fp:
		json.dump(ret_dict, fp)		

	if LISTTYPEP:
		event_list = LinkedList_P()
	else:
		event_list = LinkedList()
	ret_dict = start_priority_P(5)
	with open("dataSD1/pp_"+str(LAMBDA)+"_"+str(i), 'w') as fp:
		json.dump(ret_dict, fp)		



def run_sd2():
	global event_list
	global i 
	global LAMBDA

	# if LISTTYPEP:
	# 	event_list = LinkedList_P()
	# else:
	# 	event_list = LinkedList()
	
	# ret_dict = start_fcfs()
	# with open("dataSD2/fcfs_"+str(LAMBDA)+"_"+str(i), 'w') as fp:
	# 	json.dump(ret_dict, fp)		

	if LISTTYPEP:
		event_list = LinkedList_P()
	else:
		event_list = LinkedList()

	ret_dict = start_lcfs()
	with open("dataSD2/lcfs_"+str(LAMBDA)+"_"+str(i), 'w') as fp:
		json.dump(ret_dict, fp)	

	if LISTTYPEP:
		event_list = LinkedList_P()
	else:
		event_list = LinkedList()

	ret_dict = start_sjf()
	with open("dataSD2/sjf_"+str(LAMBDA)+"_"+str(i), 'w') as fp:
		json.dump(ret_dict, fp)		



	if LISTTYPEP:
		event_list = LinkedList_P()
	else:
		event_list = LinkedList()

	ret_dict = start_priority_NP(4)
	with open("dataSD2/pnp_"+str(LAMBDA)+"_"+str(i), 'w') as fp:
		json.dump(ret_dict, fp)		

	if LISTTYPEP:
		event_list = LinkedList_P()
	else:
		event_list = LinkedList()
	ret_dict = start_priority_P(5)
	with open("dataSD2/pp_"+str(LAMBDA)+"_"+str(i), 'w') as fp:
		json.dump(ret_dict, fp)		



def dict_test():

	with open("data4/web_0.55_2", 'r') as fp:
		res_dict = json.load(fp)

	i = 0
	for k in list(res_dict.keys()):
		if k not in ["-30", "-20", "-10"] and i > 50000:
			if res_dict[k]["served"] == 1:
				print(k, res_dict[k]["vc"], res_dict[k]["v1"], res_dict[k]["v2"], res_dict[k]["v3"])
				print(res_dict[k]["wtc"])
				print(res_dict[k]["wt1"])
				print(res_dict[k]["wt2"])
				print(res_dict[k]["wt3"])
				print("\n")


		i += 1

		if i == 50500:
			exit(1)


	exit(1)

def set_list_type():
	global event_list

	if L > 0:
		event_list = LinkedList_P()
		
	elif L == 0:
		event_list = LinkedList()


if __name__ == '__main__':
	global task
	# global event_list
	
	task = 0
	if K == 0:
		print("K should be greater than 0")
		exit(1)
	

	if L > 0:
		set_list_type()
		print("STATING WEB SERVER")
		ret_dict = web_server(LAMBDA)

	elif L == 0:
		set_list_type()
		if M == 1:
			start_fcfs()
		if M == 2:
			start_lcfs()
		if M == 3:
			start_sjf()
		if M == 4:
			start_priority_NP(M)
		if M == 5:
			start_priority_P(M)










