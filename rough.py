import netsquid as ns
import pydynaa
from netsquid.nodes import Node, Network
from netsquid.components import QuantumMemory, Component, Message,QuantumDetector
from netsquid.nodes.connections import DirectConnection
from netsquid.components.qprocessor import *
from netsquid.components.instructions import *
from netsquid.components.qprogram import *
import numpy as np
from netsquid.qubits.qubitapi import *
from netsquid.components.models import FibreDelayModel, FibreLossModel, DepolarNoiseModel
from netsquid.protocols.nodeprotocols import LocalProtocol, NodeProtocol, Signals
from netsquid.components.cqchannel import CombinedChannel
from netsquid.protocols import Protocol, Signals
from pydynaa.core import SimulationEngine
import random as rd


class AliceProtocol(NodeProtocol):

    def __init__(self,node,port_1):
        super().__init__(node=node)
        self.port_name = port_1

    def run(self):
        print("Alice protocol started")
        alice_port = self.node.ports[self.port_name]
        binary_key = []
        for i in range(n):
            qubit, = create_qubits(num_qubits=1,system_name="Q")
            if rd.randint(0,1) == 0:
                assign_qstate(qubit,ns.qubits.ketstates.s0)
                binary_key.append(0)
            else:
                assign_qstate(qubit,ns.qubits.ketstates.h0)
                binary_key.append(1)
            alice_port.tx_output((None,qubit))
            yield self.await_timer(1)

class BobProtocol(NodeProtocol):

    def __init__(self,node,port_1):
        super().__init__(node=node)
        self.port_name = port_1

    binary_key = {}

    def _handle_message(self,msg):
        [q] = msg.items
        self.binary_key[ns.sim_time()] = q

    def run(self):
        Detector_1 = self.node.subcomponents["Detector_1"]
        Detector_2 = self.node.subcomponents["Detector_2"]
        Detector_1.ports['cout0'].bind_output_handler(self._handle_message)
        Detector_2.ports['cout0'].bind_output_handler(self._handle_message)
        for i in range(10):
            q1, = create_qubits(1, "Q")
            if rd.randint(0, 1) == 0:
                assign_qstate(q1, ns.qubits.ketstates.s0)
                Detector_1.ports['qin0'].tx_input(Message(q1))
            else:
                assign_qstate(q1, ns.qubits.ketstates.h0)
                Detector_2.ports['qin0'].tx_input(Message(q1))
            yield self.await_timer(1)
        print(self.binary_key)


n = 10000

alice_qmemory = QuantumMemory("Alice_Memory", num_positions=n)
bob_qmemory = QuantumMemory("Bob_Memory", num_positions=n)

alice = Node("Alice", qmemory=alice_qmemory, port_names=["bob", "cin_bob"])
bob = Node("Bob", port_names=["alice", "cout_alice"])

detector_1 = QuantumDetector('single_detector_1')
detector_2 = QuantumDetector('single_detector_2',observable=ns.X)
bob.add_subcomponent(detector_1,"Detector_1")
bob.add_subcomponent(detector_2,"Detector_2")


channel_a2b = CombinedChannel("QC_Channel_a2b", length=1, models={"delay_model": FibreDelayModel(),
                                                                    "quantum_loss_model": FibreLossModel(p_loss_init=0,
                                                                                                         p_loss_length=0.2),
                                                                    "quantum_noise_model": DepolarNoiseModel(
                                                                        depolar_rate=1e3, time_independent=False)},
                              transmit_empty_items=True)
channel_b2a = CombinedChannel("QC_Channel_b2a", length=1, models={"delay_model": FibreDelayModel(),
                                                                    "quantum_loss_model": FibreLossModel(p_loss_init=0,
                                                                                                         p_loss_length=0.2),
                                                                    "quantum_noise_model": DepolarNoiseModel(
                                                                        depolar_rate=1e3, time_independent=False)},
                              transmit_empty_items=True)
connect = DirectConnection("Connection", channel_AtoB=channel_a2b, channel_BtoA=channel_b2a)

network = Network(name="Network")
network.add_nodes([alice, bob])
network.add_connection(alice, bob, connection=connect, label="quantum", port_name_node1="bob",
                       port_name_node2="alice")

alice_protocol = AliceProtocol(alice, "bob")
bob_protocol = BobProtocol(bob, "alice")

ns.sim_reset()
alice_protocol.start()
bob_protocol.start()
stats = ns.sim_run()
