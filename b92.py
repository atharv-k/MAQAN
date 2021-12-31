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

# detector_Z = QuantumDetector('single_detector_Z')
# detector_X = QuantumDetector('single_detector_X',observable=ns.X)
#
# alice = Node("Alice", port_names=["qout_bob", "cin_bob"])
# bob = Node("Bob", port_names=["qin_alice", "cout_alice"])
# bob.add_subcomponent(detector_Z,"Detector_Z")
# bob.add_subcomponent(detector_X,"Detector_X")

class AliceProtocol(NodeProtocol):

    def __init__(self,node,port_1,channel):
        super().__init__(node=node)
        self.port_name = port_1
        self.channel = channel
        self.matching_keybits = None

    def run(self):
        alice_port = self.node.ports[self.port_name]
        binary_key ={}
        for i in range(n):
            qubit, = create_qubits(num_qubits=1,system_name="Q")
            if rd.randint(0,1) == 0:
                assign_qstate(qubit,ns.qubits.ketstates.s0)
                binary_key[ns.sim_time()] = 0
            else:
                assign_qstate(qubit,ns.qubits.ketstates.h0)
                binary_key[ns.sim_time()] = 1
            alice_port.tx_output((None,qubit))
            yield self.await_timer(1)

        wait_expr = self.await_port_input(alice_port)
        yield wait_expr
        [(corrected_key,_)] = alice_port.rx_input().items
        raw_key = {time_stamp - self.channel.models['delay_model'].generate_delay(**{'length': self.channel.properties['length']}): binary_key[time_stamp - self.channel.models['delay_model'].generate_delay(**{'length': self.channel.properties['length']})] for time_stamp,keys in corrected_key.items() if keys == 1}
        self.matching_keybits = raw_key

class BobProtocol(NodeProtocol):

    def __init__(self,node,port_1):
        super().__init__(node=node)
        self.port_name = port_1
        self.add_signal('MEASUREMENT',pydynaa.EventType('Measurement','Send Measurement result'))
        self.matching_keybits = None
        self.list_length = None
        self.add_signal("KEY_ESTABLISHED", event_type=pydynaa.EventType("ESTABLISHED!!","The key is established"))

    def run(self):
        bob_port = self.node.ports[self.port_name]
        binary_key = {}
        measurement = {}
        raw_key = {}
        Detector_Z = self.node.subcomponents["Detector_Z"]
        Detector_X = self.node.subcomponents["Detector_X"]
        wait_evexpr = self.await_port_input(bob_port)
        for i in range(n):
            yield wait_evexpr
            [(_, [key])] = bob_port.rx_input().items
            if key is None:
                yield self.await_timer(1)
            else:
                if rd.randint(0, 1) == 0:
                    binary_key[ns.sim_time()] = 0
                    Detector_Z.ports['qin0'].tx_input(Message(key))
                    yield self.await_port_output(Detector_Z.ports['cout0'])
                    [msg] = Detector_Z.ports['cout0'].rx_output().items
                    measurement[ns.sim_time()] = msg
                    yield self.await_timer(1)
                else:
                    binary_key[ns.sim_time()] = 1
                    Detector_X.ports['qin0'].tx_input(Message(key))
                    yield self.await_port_output(Detector_X.ports['cout0'])
                    [msg] = Detector_X.ports['cout0'].rx_output().items
                    measurement[ns.sim_time()] = msg
                    yield self.await_timer(1)

        self.send_signal('MEASUREMENT')
        bob_port.tx_output((measurement, None))
        keybits = {time_stamp: binary_key[time_stamp] for time_stamp,keys in measurement.items() if keys == 1}
        for time_stamp,value in keybits.items():
            if value == 0:
                raw_key[time_stamp] = 1
            else:
                raw_key[time_stamp] = 0
        self.matching_keybits = raw_key
        self.list_length = len(raw_key)
        self.send_signal("KEY_ESTABLISHED")
        # print(f"The Binary key is: \n {binary_key}\n\n")
        # print(f"The Measurement result is: \n {measurement}\n\n")
        # print(f"The final key is: \n {self.key}\n\n")

n = 10000

if __name__ == '__main__':

    alice_qmemory = QuantumMemory("Alice_Memory", num_positions=n)
    bob_qmemory = QuantumMemory("Bob_Memory", num_positions=n)

    detector_Z = QuantumDetector('single_detector_Z')
    detector_X = QuantumDetector('single_detector_X',observable=ns.X)

    alice = Node("Alice", qmemory=alice_qmemory, port_names=["qout_bob", "cin_bob"])
    bob = Node("Bob", port_names=["qin_alice", "cout_alice"])
    bob.add_subcomponent(detector_Z,"Detector_Z")
    bob.add_subcomponent(detector_X,"Detector_X")

    channel_a2b = CombinedChannel("QC_Channel_a2b", length=5, models={"delay_model": FibreDelayModel(),
                                                                    "quantum_loss_model": FibreLossModel(p_loss_init=0,
                                                                                                         p_loss_length=0.2),
                                                                    "quantum_noise_model": DepolarNoiseModel(
                                                                        depolar_rate=1e3, time_independent=False)},
                              transmit_empty_items=True)
    channel_b2a = CombinedChannel("QC_Channel_b2a", length=5, models={"delay_model": FibreDelayModel(),
                                                                    "quantum_loss_model": FibreLossModel(p_loss_init=0,
                                                                                                         p_loss_length=0.2),
                                                                    "quantum_noise_model": DepolarNoiseModel(
                                                                        depolar_rate=1e3, time_independent=False)},
                              transmit_empty_items=True)
    connect = DirectConnection("Connection", channel_AtoB=channel_a2b, channel_BtoA=channel_b2a)

    network = Network(name="Network")
    network.add_nodes([alice, bob])
    network.add_connection(alice, bob, connection=connect, label="quantum", port_name_node1="qout_bob",
                       port_name_node2="qin_alice")

    alice_protocol = AliceProtocol(alice, "qout_bob",channel_a2b)
    bob_protocol = BobProtocol(bob, "qin_alice")
    alice_protocol.receiver_protocol = bob_protocol

# ns.sim_reset()
    alice_protocol.start()
    bob_protocol.start()
    stats = ns.sim_run()
    list_length = getattr(bob_protocol, 'list_length')
    alice_matching_key = getattr(alice_protocol, 'matching_keybits')
    bob_matching_key = getattr(bob_protocol, 'matching_keybits')
    alice_key = [value for value in alice_matching_key.values()]
    bob_key = [value for value in bob_matching_key.values()]
    error_bits = list(map(lambda x, y: x ^ y, alice_key, bob_key))
    key_bit_error = np.sum(error_bits) / list_length
    print(f"The key bit error for a key established between Alice and Bob is {key_bit_error:.3f}\n\n")
    print(stats)
