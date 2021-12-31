import netsquid as ns
import pydynaa
from netsquid.nodes import Node, Network
from netsquid.components import QuantumMemory, Message, QuantumDetector
from netsquid.nodes.connections import DirectConnection
import numpy as np
from netsquid.qubits.qubitapi import *
from netsquid.components.models import FibreDelayModel, FibreLossModel, DepolarNoiseModel
from netsquid.protocols.nodeprotocols import LocalProtocol, NodeProtocol, Signals
from netsquid.components.cqchannel import CombinedChannel
from netsquid.protocols import Protocol, Signals
from pydynaa.core import SimulationEngine
import random as rd

q1, q2, q3 = create_qubits(3,no_state=True)
assign_qstate(q1,ns.qubits.ketstates.s1)

print(f" The state of q1 is: {q1.qstate.qrepr.ket}\n")
print(f" The photon is present in q1: {q1.is_number_state}\n")
print(f" The photon is present in q2: {q2.is_number_state}\n")