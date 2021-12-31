import netsquid as ns
import pydynaa
from netsquid.nodes import Node, Network
from netsquid.components import QuantumMemory, Component, Message, QuantumDetector
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

ns.sim_reset()
bob = Node("bob",port_names=["qin_alice"])
detector_1 = QuantumDetector('single_detector_1')
detector_2 = QuantumDetector('single_detector_2',observable=ns.X)
bob.add_subcomponent(detector_1, "Detector_1")
bob.add_subcomponent(detector_2, "Detector_2")

class BobProtocol(NodeProtocol):

    def __int__(self,node):
        super().__int__(node=node)

    key = {}

    def run(self):
        qin_alice = self.node.ports["qin_alice"]
        Detector_1 = self.node.subcomponents["Detector_1"]
        Detector_2 = self.node.subcomponents["Detector_2"]
        # Detector_1.ports['cout0'].bind_output_handler(self._handle_message)
        # Detector_2.ports['cout0'].bind_output_handler(self._handle_message)
        for i in range(10):
            q1, = create_qubits(1, "Q")
            if rd.randint(0, 1) == 0:
                assign_qstate(q1, ns.qubits.ketstates.s0)
                Detector_1.ports['qin0'].tx_input(Message(q1))
                yield self.await_port_output(Detector_1.ports['cout0'])
                [msg] = Detector_1.ports['cout0'].rx_output().items
                self.key[ns.sim_time()] = msg
            else:
                assign_qstate(q1, ns.qubits.ketstates.h1)
                Detector_2.ports['qin0'].tx_input(Message(q1))
                yield self.await_port_output(Detector_2.ports['cout0'])
                [msg] = Detector_2.ports['cout0'].rx_output().items
                self.key[ns.sim_time()] = msg
            yield self.await_timer(1)
        print(self.key)

bob_protocol = BobProtocol(bob)
bob_protocol.start()

stats = ns.sim_run()



