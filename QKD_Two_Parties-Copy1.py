#!/usr/bin/env python
# coding: utf-8

# In[1]:


import netsquid as ns
import pydynaa
from netsquid.nodes import Node
from netsquid.components import QuantumMemory
from netsquid.components import ClassicalChannel
from netsquid.nodes.connections import Connection, DirectConnection
from netsquid.components.qchannel import QuantumChannel
import random as rd
from netsquid.qubits.qubitapi import *
from netsquid.protocols import NodeProtocol, Signals
from netsquid.nodes import Network
import numpy as np
from netsquid.components.models import FibreDelayModel
from netsquid.components.models.qerrormodels import FibreLossModel, DepolarNoiseModel
from collections import OrderedDict
from netsquid.components.models.delaymodels import FixedDelayModel
from netsquid.components.cqchannel import CombinedChannel
from pydynaa.core import SimulationEngine


# In[2]:


def Assign_Quantum_State(qubit):
    
    if rd.randint(1,2) == 1:
        basis = "|Z >"
        if rd.randint(0,1) == 0:
            assign_qstate(qubit, ns.qubits.ketstates.s0)
            binary= 0
        else:
            assign_qstate(qubit, ns.qubits.ketstates.s1)
            binary = 1
    else:
        basis = "|X >"
        if rd.randint(0,1) == 0:
            assign_qstate(qubit, ns.qubits.ketstates.h0)
            binary = 0
        else:
            assign_qstate(qubit, ns.qubits.ketstates.h1)
            binary = 1
                    
    return (qubit, basis, binary)            


# In[3]:


def Measure_Quantum_State(node,qubit,i):
    
    if qubit is None:
        return ("None", "None")
    else:    
        node.qmemory.put(qubit,positions=i)
        if rd.randint(1,2) == 1:
            basis = "|Z >"
            [m],_ = node.qmemory.measure(positions=[i], observable=ns.Z)
            bin_key = m
        else:    
            basis = "|X >"
            [m],_ = node.qmemory.measure(positions=[i], observable=ns.X)
            bin_key = m
                    
        return (basis, bin_key)  


# In[4]:


class AliceProtocol(NodeProtocol):
    
    def __init__(self, node):
        super().__init__(node)
        #self.binary_key = None
        self.matching_keybits = None
        self.send_evtype = pydynaa.EventType("Send", "Send the prepared qubit")
        self.time_stamp = []
        self.binary_key = {}
        self.alice_basis = {}
        self.delay = 2
        self.time_stamp_label = "TIME_STAMP"
        self.add_signal(self.time_stamp_label, event_type = pydynaa.EventType("The final time stamp", "The final time stamp to be sent"))
        
    def _create_qubit(self, event):
        qubit, = create_qubits(num_qubits=1, system_name="Q")
        q, basis, binary = Assign_Quantum_State(qubit)
        self.time_stamp.append(ns.sim_time())
        self.alice_basis[ns.sim_time()] = basis
        self.binary_key[ns.sim_time()] = binary
        self.node.ports["qout_bob"].tx_output((None,q))    
    
    def run(self):    
        port_qout_bob = self.node.ports["qout_bob"]
        port_cin_bob = self.node.ports["cin_bob"]
        sim_engine = SimulationEngine()
        qubit_create = pydynaa.EventHandler(self._create_qubit)
        for i in range(n):
            self._schedule_after(i*self.delay,self.send_evtype)
            self._wait(qubit_create, entity=self, event_type=self.send_evtype)
            
                
        #self.binary_key = bin_key
        #print(f"\n\n The Alice's key \n\n {self.binary_key}")
        yield self.await_signal(bob_protocol,Signals.READY)
        yield self.await_port_input(port_qout_bob)
        [(Bob_Basis,_)]= port_qout_bob.rx_input().items
        bob_basis = {keys-channel_a2b.models['delay_model'].generate_delay(**{'length': 100}): Bob_Basis[keys] for keys in Bob_Basis}
        exact_basis = {k: self.alice_basis[k] for k in self.alice_basis if k in bob_basis and self.alice_basis[k] == bob_basis[k]}
        matching_time_stamps = [key + channel_a2b.models['delay_model'].generate_delay(**{'length': 100}) for key in exact_basis]
        #print(f"\nAlice key:\n\n{self.binary_key}\n")
        self.matching_keybits = {key: self.binary_key.get(key) for key in exact_basis}
        self.send_signal(self.time_stamp_label)
        port_qout_bob.tx_output((matching_time_stamps,None))


# In[5]:


class BobProtocol(NodeProtocol):
    
    def _init__(self,node):
        super().__init__(node)
        self.list_length = None
        self.binary_key = None
        self.bob_basis = None
        self.matching_keybits = None
        self.recv_evtype = None
        self.bob_time_stamp = None
        self.bob_signal_label ="BASIS_READY"
        self.add_signal("BASIS_READY", event_type=pydynaa.EventType("The Bob's basis", "The Bob's basis are ready"))
        
    def run(self):
        port_qin_alice = self.node.ports["qin_alice"]
        port_cout_alice = self.node.ports["cout_alice"] 
        sim_engine = SimulationEngine()
        recv_evt = pydynaa.EventType("Recieve qubit", "Recieve the prepared qubit")
        self.recv_evtype = recv_evt
        recv_evexpr = pydynaa.EventExpression(source=self, event_type=self.recv_evtype)
        wait_evexpr = self.await_port_input(port_qin_alice)
        time_stamp=[]
        basis ={}
        bin_key={}
        i = 0
        while i < n:
            evexpr = yield recv_evexpr | wait_evexpr
            if evexpr.second_term.value:
                [(_,[key])] = port_qin_alice.rx_input().items
                basis[sim_engine.current_time], bin_key[sim_engine.current_time]= Measure_Quantum_State(self.node,key,i)
                time_stamp.append(sim_engine.current_time)
                i =i+1
                self._schedule_at(sim_engine.current_time+i,self.recv_evtype)
            else:    
                i= i+1
                self._schedule_at(sim_engine.current_time+i,self.recv_evtype)   
        
        self.bob_basis = {key: basis[key] for key in basis if basis[key] != "None"}
        self.binary_key = {key: bin_key[key] for key in bin_key if bin_key[key] != "None"}
        self.bob_time_stamp = time_stamp
        self.send_signal(Signals.READY)
        port_qin_alice.tx_output((self.bob_basis,None)) 
        used = self.node.qmemory.used_positions
        for position in self.node.qmemory.used_positions:
            self.node.qmemory.discard(position)
        
        yield self.await_signal(alice_protocol, alice_protocol.time_stamp_label)
        yield self.await_port_input(port_qin_alice)
        [(matching_time_stamp,_)] = port_qin_alice.rx_input().items
        self.matching_keybits = {key: self.binary_key[key] for key in matching_time_stamp}
        self.list_length = len(self.matching_keybits)
        #print(f"The time taken to set the key is {ns.sim_time()}")
        #print(f"\n\n The positions where the choice of their basis match \n\n {exact_basis}")


# In[6]:


n = 10000
alice_qmemory = QuantumMemory("Alice_Memory", num_positions=n, models={'delay_model': FixedDelayModel(1)})
bob_qmemory = QuantumMemory("Bob_Memory", num_positions=n, models={"delay_model": FixedDelayModel(1)})

alice = Node("Alice", qmemory=alice_qmemory, port_names=["qout_bob", "cin_bob"])
bob = Node("Bob", qmemory=bob_qmemory,  port_names=["qin_alice", "cout_alice"])

channel_a2b = CombinedChannel("QC_Channel_a2b", length=100, models={"delay_model": FibreDelayModel(), "quantum_loss_model": FibreLossModel(p_loss_init=0, p_loss_length=0.2), "quantum_noise_model": DepolarNoiseModel(depolar_rate=1e3, time_independent=False)}, transmit_empty_items=True)
channel_b2a = CombinedChannel("QC_Channel_b2a", length=100, models={"delay_model": FibreDelayModel(), "quantum_loss_model": FibreLossModel(p_loss_init=0, p_loss_length=0.2), "quantum_noise_model": DepolarNoiseModel(depolar_rate=1e3, time_independent=False)}, transmit_empty_items=True)
connect = DirectConnection("Connection",channel_AtoB=channel_a2b,channel_BtoA=channel_b2a)
    
network = Network(name="Network")
network.add_nodes([alice, bob])
network.add_connection(alice, bob, connection=connect, label="quantum", port_name_node1="qout_bob", port_name_node2="qin_alice")
#cport1_bob, cport1_alice = network.add_connection(alice, bob, channel_to=cconnect_b2a.cchannel_a2b, channel_from=cconnect_b2a.cchannel_b2a, delay=2, bidirectional=True, label="classical_1", port_name_node1="cout_alice", port_name_node2="cin_bob")
#cport2_alice, cport2_bob = network.add_connection(alice, bob, connection=cconnect_a2b, delay=2, bidirectional=True, label="classical_2", port_name_node1="cout_bob", port_name_node2="cin_alice")

#alice.qmemory.ports["qout"].forward_output(alice.ports[qport_alice])
#bob.ports[qport_bob].forward_input(bob.qmemory.ports["qin"])
    
alice_protocol = AliceProtocol(alice)
bob_protocol = BobProtocol(bob)


# In[7]:


#for i in range(0,101,10):
    
#qconnect_a2b = quantumconnect_a2b("QuantumConnection_a2b", 100)
#cconnect_b2a = classicalconnect_b2a("ClassicalConnection_b2a", 100)
#cconnect_a2b = classicalconnect_a2b("ClassicalConnection_a2b", 100)
    
key_bit_error = []
for j in range(1):
    ns.sim_reset()
    alice_protocol.start()
    bob_protocol.start()
    stats = ns.sim_run()
    list_length = getattr(bob_protocol, 'list_length')
    alice_matching_key = getattr(alice_protocol, 'matching_keybits')
    bob_matching_key = getattr(bob_protocol, 'matching_keybits')
    alice_key = [value for value in alice_matching_key.values()]
    bob_key = [value for value in bob_matching_key.values()]
    error_bits = list(map(lambda x,y: x ^ y, alice_key, bob_key))
    key_bit_error.append(np.sum(error_bits)/list_length)
print(f"The time required to establish the key is {ns.sim_time()}\n\n")    
print(f"The key bit error for an iteration. is:\n\n {key_bit_error}\n\n")


# In[ ]:




