import netsquid as ns
import pydynaa
from netsquid.nodes import Node, Network
from netsquid.components import QuantumChannel, ClassicalChannel, Clock, QSource
from netsquid.nodes.connections import DirectConnection
import numpy as np
from netsquid.qubits.qubitapi import *
from netsquid.components.models import FibreDelayModel, FibreLossModel, DepolarNoiseModel
from netsquid.protocols.nodeprotocols import LocalProtocol, NodeProtocol
from netsquid.protocols import Protocol
from pydynaa.core import SimulationEngine
import random as rd
from Optical_Components import DelayLineInterferometer, DestructiveInterferenceDetector, ConstructiveInterferenceDetector, BeamSplitter

class AliceProtocol(NodeProtocol):

    def __init__(self,node):
        super().__init__(node=node)
        self.sim_engine = SimulationEngine()

    raw_key = {}

    def run(self):
        photon_source = self.node.subcomponents["Photon_Source"]
        bs = self.node.subcomponents["Beam_Splitter"]
        photon_source.status = ns.components.qsource.SourceStatus.EXTERNAL
        for i in range(n):
            photon_source.trigger()
            yield self.await_port_input(bs.ports["qin"])
            yield self.await_timer(5)
        print(f"\nThe alice's key is: {bs.raw_key}\n")

class BobProtocol(NodeProtocol):

    def __init__(self,node):
        super().__init__(node=node)
        self.receive_evtype = pydynaa.EventType("RECEIVE","Receive the photon")

    raw_key = {}

    def _store_key(self,msg):
        [key] = msg.items
        self.raw_key[ns.sim_time()] = key

    def run(self):
        dli = self.node.subcomponents["DLI"]
        cons_detector = self.node.subcomponents["Constructive"]
        des_detector = self.node.subcomponents["Destructive"]
        cons_detector.ports["cout0"].bind_output_handler(self._store_key)
        des_detector.ports["cout0"].bind_output_handler(self._store_key)
        for i in range(n):
            yield self.await_port_input(dli.ports["qin"])
            dli.start()
            detector_evexpr = yield self.await_port_input(
                cons_detector.ports["qin0"]) | self.await_port_input(
                des_detector.ports["qin0"])
            yield self.await_timer(1)
        print(f"\nThe bob's key is: {self.raw_key}\n")

n = 100

alice = Node("Alice", port_names=["q_bob", "c_bob"])
bob = Node("Bob", port_names=["q_alice", "c_alice"])

PhotonSource = QSource(name="Photon_Source")
beam_spiltter = BeamSplitter(name="Beam_Splitter")
dli = DelayLineInterferometer("DLI")
constructive_detector = ConstructiveInterferenceDetector("Constructive")
destructive_detector = DestructiveInterferenceDetector("Destructive")

alice.add_subcomponent(PhotonSource,"Photon_Source")
alice.add_subcomponent(beam_spiltter,"Beam_Splitter")
bob.add_subcomponent(dli,"DLI")
bob.add_subcomponent(constructive_detector,"Constructive")
bob.add_subcomponent(destructive_detector,"Destructive")

alice.subcomponents["Photon_Source"].ports['qout0'].connect(alice.subcomponents["Beam_Splitter"].ports["qin"])
alice.subcomponents["Beam_Splitter"].ports["qout"].forward_output(alice.ports["q_bob"])

bob.ports["q_alice"].forward_input(bob.subcomponents["DLI"].ports["qin"])
bob.subcomponents["DLI"].ports["cout0"].connect(bob.subcomponents["Constructive"].ports["qin0"])
bob.subcomponents["DLI"].ports["cout1"].connect(bob.subcomponents["Destructive"].ports["qin0"])

qchannel_a2b = QuantumChannel("Quantum_Channel_a2b", length=1, models={'delay_model': FibreDelayModel()} ,transmit_empty_items=True)
qchannel_b2a = QuantumChannel("Quantum_Channel_b2a", length=1, models={'delay_model': FibreDelayModel()}, transmit_empty_items=True)
qconnect = DirectConnection("Connection", channel_AtoB=qchannel_a2b, channel_BtoA=qchannel_b2a)

cchannel_a2b = ClassicalChannel("Classical_Channel_a2b", length=1, models={'delay_model': FibreDelayModel()}, transmit_empty_items=True )
cchannel_b2a = ClassicalChannel("Classical_Channel_b2a", length=1, models={'delay_model': FibreDelayModel()}, transmit_empty_items=True )
cconnect = DirectConnection("Connection", channel_AtoB=cchannel_a2b, channel_BtoA=cchannel_b2a)

network = Network(name="Network")
network.add_nodes([alice, bob])
network.add_connection(alice, bob, connection=qconnect, label="quantum", port_name_node1="q_bob", port_name_node2="q_alice")
network.add_connection(alice, bob, connection=cconnect, label="channel", port_name_node1="c_bob", port_name_node2="c_alice")

alice_protocol = AliceProtocol(alice)
bob_protocol = BobProtocol(bob)
alice_protocol.start()
bob_protocol.start()

stats = ns.sim_run()
print(stats)