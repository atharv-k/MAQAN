import netsquid as ns
import pydynaa
from netsquid.nodes import Node, Network
from netsquid.components import QuantumMemory,QuantumDetector,Message
from netsquid.nodes.connections import DirectConnection
import numpy as np
from netsquid.qubits.qubitapi import *
from netsquid.components.models import FibreDelayModel, FibreLossModel, DepolarNoiseModel
from netsquid.protocols.nodeprotocols import LocalProtocol, NodeProtocol, Signals
from netsquid.components.cqchannel import CombinedChannel
from netsquid.protocols import Protocol, Signals
import BB84 as qkd
import b92
from pydynaa.core import SimulationEngine
import random as rd

# class AliceProtocol(NodeProtocol):
#
#     n = 10000
#
#     def __init__(self, node, port_1, channel):
#         """
#
#         :type port_2: object
#         """
#         super().__init__(node)
#         self.port_name = port_1
#         self.connected_channel = channel
#         self.matching_keybits = None
#         self.send_evtype = pydynaa.EventType("Send", "Send the prepared qubit")
#         self.time_stamp = []
#         self.binary_key = {}
#         self.alice_basis = {}
#         self.delay = 2
#         self.time_stamp_label = "TIME_STAMP"
#         self.add_signal(self.time_stamp_label,event_type=pydynaa.EventType("The final time stamp", "The final time stamp to be sent"))
#
#     def _Assign_Quantum_State(self, qubit):
#         if rd.randint(1, 2) == 1:
#             basis = "|Z >"
#             if rd.randint(0, 1) == 0:
#                 assign_qstate(qubit, ns.qubits.ketstates.s0)
#                 binary = 0
#             else:
#                 assign_qstate(qubit, ns.qubits.ketstates.s1)
#                 binary = 1
#         else:
#             basis = "|X >"
#             if rd.randint(0, 1) == 0:
#                 assign_qstate(qubit, ns.qubits.ketstates.h0)
#                 binary = 0
#             else:
#                 assign_qstate(qubit, ns.qubits.ketstates.h1)
#                 binary = 1
#
#         return (qubit, basis, binary)
#
#     def _create_qubit(self, event):
#         qubit = create_qubits(num_qubits=1, system_name="Q")
#         #print(qubit)
#         q, basis, binary = self._Assign_Quantum_State(qubit)
#         self.time_stamp.append(ns.sim_time())
#         self.alice_basis[ns.sim_time()] = basis
#         self.binary_key[ns.sim_time()] = binary
#         self.node.ports[self.port_name].tx_output((None, q))
#
#     def run(self):
#         print("Alice protocol started")
#         port_qout_bob = self.node.ports[self.port_name]
#         sim_engine = SimulationEngine()
#         qubit_create = pydynaa.EventHandler(self._create_qubit)
#         for i in range(n):
#             self._schedule_after(i * self.delay, self.send_evtype)
#             self._wait(qubit_create, entity=self, event_type=self.send_evtype)
#
#         yield self.await_signal(self.receiver_protocol, Signals.READY)
#         yield self.await_port_input(port_qout_bob)
#         [(Bob_Basis, _)] = port_qout_bob.rx_input().items
#         bob_basis = {keys - self.connected_channel.models['delay_model'].generate_delay(**{'length': self.connected_channel.properties['length']}): Bob_Basis[keys] for keys in Bob_Basis}
#         exact_basis = {k: self.alice_basis[k] for k in self.alice_basis if k in bob_basis and self.alice_basis[k] == bob_basis[k]}
#         matching_time_stamps = [key + self.connected_channel.models['delay_model'].generate_delay(**{'length': self.connected_channel.properties['length']}) for key in exact_basis]
#         self.matching_keybits = {key: self.binary_key.get(key) for key in exact_basis}
#         self.send_signal(self.time_stamp_label)
#         port_qout_bob.tx_output((matching_time_stamps, None))
#         print(f"the time at which alice sent the labels {ns.sim_time()}")
#
# class BobProtocol(NodeProtocol):
#
#     n = 10000
#
#     def __init__(self, node, port_1):
#         super().__init__(node=node)
#         self.port_name = port_1
#         self.list_length = None
#         self.binary_key = None
#         self.bob_basis = None
#         self.matching_keybits = None
#         self.recv_evtype = None
#         self.bob_time_stamp = None
#         self.bob_signal_label = "BASIS_READY"
#         self.add_signal("BASIS_READY", event_type=pydynaa.EventType("The Bob's basis", "The Bob's basis are ready"))
#
#     def _Measure_Quantum_State(self, node, qubit, i):
#
#         if qubit is None:
#             return ("None", "None")
#         else:
#             node.qmemory.put(qubit, positions=i)
#             if rd.randint(1, 2) == 1:
#                 basis = "|Z >"
#                 [m], _ = node.qmemory.measure(positions=[i], observable=ns.Z)
#                 bin_key = m
#             else:
#                 basis = "|X >"
#                 [m], _ = node.qmemory.measure(positions=[i], observable=ns.X)
#                 bin_key = m
#
#             return (basis, bin_key)
#
#     def run(self):
#         print("Bob protocol started")
#         port_qin_alice = self.node.ports[self.port_name]
#         sim_engine = SimulationEngine()
#         recv_evt = pydynaa.EventType("Recieve qubit", "Recieve the prepared qubit")
#         self.recv_evtype = recv_evt
#         recv_evexpr = pydynaa.EventExpression(source=self, event_type=self.recv_evtype)
#         wait_evexpr = self.await_port_input(port_qin_alice)
#         time_stamp = []
#         basis = {}
#         bin_key = {}
#         i = 0
#         while i < n:
#             evexpr = yield recv_evexpr | wait_evexpr
#             if evexpr.second_term.value:
#                 [(_, [key])] = port_qin_alice.rx_input().items
#                 basis[sim_engine.current_time], bin_key[sim_engine.current_time] = self._Measure_Quantum_State(self.node, key,i)
#                 time_stamp.append(sim_engine.current_time)
#                 i = i + 1
#                 self._schedule_at(sim_engine.current_time + i, self.recv_evtype)
#             else:
#                 i = i + 1
#                 self._schedule_at(sim_engine.current_time + i, self.recv_evtype)
#
#         self.bob_basis = {key: basis[key] for key in basis if basis[key] != "None"}
#         self.binary_key = {key: bin_key[key] for key in bin_key if bin_key[key] != "None"}
#         self.bob_time_stamp = time_stamp
#         self.send_signal(Signals.READY)
#         port_qin_alice.tx_output((self.bob_basis, None))
#         print(f"time at which bob sent his basis {ns.sim_time()}")
#         for position in self.node.qmemory.used_positions:
#             self.node.qmemory.discard(position)
#
#
#         ev_exp = self.await_signal(self.sender_protocol, self.sender_protocol.time_stamp_label)
#         yield ev_exp
#         print(f"The time when signal was recieved is {ns.sim_time()}")
#         yield self.await_port_input(port_qin_alice)
#         print(f"time at which bob recieved his timestamps {ns.sim_time()}")
#         [(matching_time_stamp, _)] = port_qin_alice.rx_input().items
#         print(matching_time_stamp)
#         self.matching_keybits = {key: self.binary_key[key] for key in matching_time_stamp}
#         self.list_length = len(self.matching_keybits)

class EstablishKey(Protocol):

    def __init__(self, aliceprotocol, bobprotocol):
        super().__init__(name="Key_Establishment")
        self.add_subprotocol(aliceprotocol,"Alice")
        self.add_subprotocol(bobprotocol,"Bob")

    def run(self):
        yield self.await_signal(sender=self.subprotocols["Bob"],signal_label="KEY_ESTABLISHED")
        list_length = getattr(self.subprotocols["Bob"], 'list_length')
        alice_matching_key = getattr(self.subprotocols["Alice"], 'matching_keybits')
        bob_matching_key = getattr(self.subprotocols["Bob"], 'matching_keybits')
        alice_key = [value for value in alice_matching_key.values()]
        bob_key = [value for value in bob_matching_key.values()]
        error_bits = list(map(lambda x, y: x ^ y, alice_key, bob_key))
        key_bit_error = (np.sum(error_bits) / list_length)
        print(f"The key bit error is {key_bit_error}\n\n")

    def start(self):
        super().start()
        self.start_subprotocols()

def handle_2_nodes(node_Alice,node_Bob,channel):
        port_Alice = None
        port_Bob = None
        for name in node_Alice.ports:
            if node_Bob.name in name:
                port_Alice = name
                break
            else:
                continue
        for name in node_Bob.ports:
            if node_Alice.name in name:
                port_Bob = name
                break
            else:
                continue
        alice_protocol = qkd.AliceProtocol(node_Alice,port_Alice,channel)
        bob_protocol = qkd.BobProtocol(node_Bob,port_Bob)
        alice_protocol.receiver_protocol = bob_protocol
        bob_protocol.sender_protocol = alice_protocol
        key_establish = EstablishKey(alice_protocol,bob_protocol)
        return key_establish

class C_NetworkProtocol(LocalProtocol):

    def __init__(self, node_1, node_2, node_3, node_4, node_5,channel_C_A,channel_C_B,channel_C_D2,channel_C_D1):
        super().__init__(nodes={"A": node_1, "B": node_2, "C": node_3, "D1": node_4, "D2": node_5})
        self.add_subprotocol(handle_2_nodes(self.nodes["C"],self.nodes["A"],channel_C_A),"A_and_C")
        self.add_subprotocol(handle_2_nodes(self.nodes["C"],self.nodes["B"],channel_C_B),"B_and_C")
        self.add_subprotocol(handle_2_nodes(self.nodes["C"],self.nodes["D2"],channel_C_D2),"D2_and_C")
        self.add_subprotocol(handle_2_nodes(self.nodes["C"],self.nodes["D1"],channel_C_D1),"D1_and_C")
        #self.add_signal("D2_STARTED",pydynaa.EventType("D2 started","D2 is started"))
        #self.add_signal("D2_FINISHED",pydynaa.EventType("D2 finished","D2 is finished"))

    def run(self):
        sim_engine = SimulationEngine()
        time_before_A_C = ns.sim_time()
        self.subprotocols["A_and_C"].start()
        yield self.await_signal(self.subprotocols["A_and_C"],Signals.FINISHED)
        time_after_A_C = ns.sim_time()
        time_taken_A_C = time_after_A_C - time_before_A_C
        print(f"The time taken to establish key between bob and C is {time_taken_A_C} ns\n\n")
        time_before_B_C = ns.sim_time()
        self.subprotocols["B_and_C"].start()
        yield self.await_signal(self.subprotocols["B_and_C"],Signals.FINISHED)
        time_after_B_C = ns.sim_time()
        time_taken_B_C = time_after_B_C - time_before_B_C
        print(f"The time taken to establish the key between B and C is {time_taken_B_C} ns\n\n")
        time_before_C_D2 = ns.sim_time()
        self.subprotocols["D2_and_C"].start()
        yield self.await_signal(self.subprotocols["D2_and_C"],Signals.FINISHED)
        time_after_C_D2 = ns.sim_time()
        time_taken_C_D2 = time_after_C_D2 - time_before_C_D2
        print(f"The time taken to establish the key between D2 and C is {time_taken_C_D2} ns\n\n")
        while overall_protocol.flag_D1 == 1:
            yield self.await_timer(5)
        time_before_C_D1 = ns.sim_time()
        self.subprotocols["D1_and_C"].start()
        yield self.await_signal(self.subprotocols["D1_and_C"],Signals.FINISHED)
        time_after_C_D1 = ns.sim_time()
        time_taken_C_D1 = time_after_C_D1 - time_before_C_D1
        print(f"The time taken to establish the key between D1 and C is {time_taken_C_D1} ns\n\n")

class E_NetworkProtocol(LocalProtocol):

    def __init__(self,node_1,node_2,node_3,channel_E_D1,channel_E_D2):
        super().__init__(nodes={"D1": node_1, "D2": node_2, "E": node_3})
        self.add_subprotocol(handle_2_nodes(self.nodes["E"],self.nodes["D1"],channel_E_D1),"E_and_D1")
        self.add_subprotocol(handle_2_nodes(self.nodes["E"],self.nodes["D2"],channel_E_D2),"E_and_D2")
        self.add_signal("E_D1_STARTED",pydynaa.EventType("D1 started","D1 is started"))
        self.add_signal("E_D1_FINISHED",pydynaa.EventType("D1 finished","D1 is finished"))

    def run(self):
        sim_engine = SimulationEngine()
        time_before_E_D1 = ns.sim_time()
        self.send_signal("E_D1_STARTED")
        self.subprotocols["E_and_D1"].start()
        yield self.await_signal(self.subprotocols["E_and_D1"],Signals.FINISHED)
        self.send_signal("E_D1_FINISHED")
        time_after_E_D1 = ns.sim_time()
        time_taken_E_D1 = time_after_E_D1 - time_before_E_D1
        print(f"The time taken to establish the key between E and D1 is {time_taken_E_D1} ns\n\n")
        time_before_E_D2 = ns.sim_time()
        self.subprotocols["E_and_D2"].start()
        yield self.await_signal(self.subprotocols["E_and_D2"], Signals.FINISHED)
        time_after_E_D2 = ns.sim_time()
        time_taken_E_D2 = time_after_E_D2 - time_before_E_D2
        print(f"The time taken to establish the key between E and D2 is {time_taken_E_D2}")

class OverallProtocol(Protocol):

    def __init__(self,node_A,node_B,node_C,node_D1,node_D2,node_E,channel_C_A,channel_C_B,channel_D2_C,channel_D1_C,channel_D1_E,channel_D2_E):
        super().__init__(name="Handler")
        self.add_subprotocol(C_NetworkProtocol(node_A,node_B,node_C,node_D1,node_D2,channel_C_A,channel_C_B,channel_D2_C,channel_D1_C),"C_protocol")
        self.add_subprotocol(E_NetworkProtocol(node_D1,node_D2,node_E,channel_D1_E,channel_D2_E),"E_protocol")
        self.flag_D1 = 0

    def run(self):
        sim_engine = SimulationEngine()
        print(f"The simulation started at {ns.sim_time()} ns \n\n")
        yield self.await_signal(self.subprotocols["E_protocol"],"E_D1_STARTED")
        self.flag_D1 = 1
        yield self.await_signal(self.subprotocols["E_protocol"],"E_D1_FINISHED")
        self.flag_D1 = 0
        C_evexpr = self.await_signal(self.subprotocols["C_protocol"],Signals.FINISHED)
        E_evexpr = self.await_signal(self.subprotocols["E_protocol"],Signals.FINISHED)
        yield E_evexpr & C_evexpr
        print(f"The simulation ended at {ns.sim_time()} ns \n\n")

    def start(self):
        super().start()
        self.start_subprotocols()


n = 10000
if __name__ == "__main__":
    A_qmemory = QuantumMemory("A_QMemory", num_positions=n)
    B_qmemory = QuantumMemory("B_QMemory", num_positions=n)
    D1_qmemory = QuantumMemory("D1_QMemory", num_positions=n)
    D2_qmemory = QuantumMemory("D2_QMemory", num_positions=n)

    A = Node("A", qmemory=A_qmemory, port_names=["port_C"])
    B = Node("B", qmemory=B_qmemory, port_names=["port_C"])
    C = Node("C", port_names=["port_A", "port_B", "port_D1", "port_D2"])
    D1 = Node("D1", qmemory=D1_qmemory, port_names=["port_C", "port_E"])
    D2 = Node("D2", qmemory=D2_qmemory, port_names=["port_C", "port_E"])
    E = Node("E", port_names=["port_D1", "port_D2"])

    detector_Z_A = QuantumDetector('single_detector_Z')
    detector_X_A = QuantumDetector('single_detector_X',observable=ns.X)
    A.add_subcomponent(detector_Z_A,"Detector_Z")
    A.add_subcomponent(detector_X_A,"Detector_X")

    detector_Z_B = QuantumDetector('single_detector_Z')
    detector_X_B = QuantumDetector('single_detector_X',observable=ns.X)
    B.add_subcomponent(detector_Z_B,"Detector_Z")
    B.add_subcomponent(detector_X_B,"Detector_X")

    detector_Z_D1 = QuantumDetector('single_detector_Z')
    detector_X_D1 = QuantumDetector('single_detector_X',observable=ns.X)
    D1.add_subcomponent(detector_Z_D1,"Detector_Z")
    D1.add_subcomponent(detector_X_D1,"Detector_X")

    detector_Z_D2 = QuantumDetector('single_detector_Z')
    detector_X_D2 = QuantumDetector('single_detector_X',observable=ns.X)
    D2.add_subcomponent(detector_Z_D2,"Detector_Z")
    D2.add_subcomponent(detector_X_D2,"Detector_X")

    network = Network("Network")
    network.add_nodes([A, B, C, D1, D2, E])

    channel_A2C = CombinedChannel("QC_channel_A2C", length=5, models={"delay_model": FibreDelayModel(), "quantum_loss_model": FibreLossModel(p_loss_init=0,p_loss_length=0.2), "quantum_noise_model": DepolarNoiseModel(depolar_rate=1e3, time_independent=False)}, transmit_empty_items=True)
    channel_C2A = CombinedChannel("QC_channel_C2A", length=5, models={"delay_model": FibreDelayModel(), "quantum_loss_model": FibreLossModel(p_loss_init=0,p_loss_length=0.2), "quantum_noise_model": DepolarNoiseModel(depolar_rate=1e3, time_independent=False)}, transmit_empty_items=True)
    connect_A2C = DirectConnection("Connection_A2C", channel_AtoB=channel_A2C, channel_BtoA=channel_C2A)
    network.add_connection(A,C,connection=connect_A2C,label="A_to_C",port_name_node1="port_C",port_name_node2="port_A")

    channel_B2C = CombinedChannel("QC_channel_B2C", length=0.5, models={"delay_model": FibreDelayModel(), "quantum_loss_model": FibreLossModel(p_loss_init=0,p_loss_length=0.2), "quantum_noise_model": DepolarNoiseModel(depolar_rate=1e3, time_independent=False)}, transmit_empty_items=True)
    channel_C2B = CombinedChannel("QC_channel_C2B", length=0.5, models={"delay_model": FibreDelayModel(), "quantum_loss_model": FibreLossModel(p_loss_init=0,p_loss_length=0.2), "quantum_noise_model": DepolarNoiseModel(depolar_rate=1e3, time_independent=False)}, transmit_empty_items=True)
    connect_B2C = DirectConnection("Connection_B2C", channel_AtoB=channel_B2C, channel_BtoA=channel_C2B)
    network.add_connection(B,C,connection=connect_B2C,label="B_to_C",port_name_node1="port_C",port_name_node2="port_B")

    channel_C2D1 = CombinedChannel("QC_channel_C2D1", length=1, models={"delay_model": FibreDelayModel(), "quantum_loss_model": FibreLossModel(p_loss_init=0,p_loss_length=0.2), "quantum_noise_model": DepolarNoiseModel(depolar_rate=1e3, time_independent=False)}, transmit_empty_items=True)
    channel_D12C = CombinedChannel("QC_channel_D12C", length=1, models={"delay_model": FibreDelayModel(), "quantum_loss_model": FibreLossModel(p_loss_init=0,p_loss_length=0.2), "quantum_noise_model": DepolarNoiseModel(depolar_rate=1e3, time_independent=False)}, transmit_empty_items=True)
    connect_C2D1 = DirectConnection("Connection_C2D1", channel_AtoB=channel_C2D1, channel_BtoA=channel_D12C)
    network.add_connection(D1,C,connection=connect_C2D1,label="C_to_D1",port_name_node1="port_C",port_name_node2= "port_D1")

    channel_C2D2 = CombinedChannel("QC_channel_C2D2", length=1, models={"delay_model": FibreDelayModel(), "quantum_loss_model": FibreLossModel(p_loss_init=0,p_loss_length=0.2), "quantum_noise_model": DepolarNoiseModel(depolar_rate=1e3, time_independent=False)}, transmit_empty_items=True)
    channel_D22C = CombinedChannel("QC_channel_D22C", length=1, models={"delay_model": FibreDelayModel(), "quantum_loss_model": FibreLossModel(p_loss_init=0,p_loss_length=0.2), "quantum_noise_model": DepolarNoiseModel(depolar_rate=1e3, time_independent=False)}, transmit_empty_items=True)
    connect_C2D2 = DirectConnection("Connection_C2D2", channel_AtoB=channel_C2D2, channel_BtoA=channel_D22C)
    network.add_connection(D2,C,connection=connect_C2D2,label="C_to_D2",port_name_node1="port_C", port_name_node2= "port_D2")

    channel_E2D1 = CombinedChannel("QC_channel_E2D1", length=8, models={"delay_model": FibreDelayModel(), "quantum_loss_model": FibreLossModel(p_loss_init=0,p_loss_length=0.2), "quantum_noise_model": DepolarNoiseModel(depolar_rate=1e3, time_independent=False)}, transmit_empty_items=True)
    channel_D12E = CombinedChannel("QC_channel_D12E", length=8, models={"delay_model": FibreDelayModel(), "quantum_loss_model": FibreLossModel(p_loss_init=0,p_loss_length=0.2), "quantum_noise_model": DepolarNoiseModel(depolar_rate=1e3, time_independent=False)}, transmit_empty_items=True)
    connect_E2D1 = DirectConnection("Connection_E2D1", channel_AtoB=channel_E2D1, channel_BtoA=channel_D12E)
    network.add_connection(E,D1,connection=connect_E2D1,label="E_to_D1",port_name_node1="port_D1",port_name_node2="port_E")

    channel_E2D2 = CombinedChannel("QC_channel_E2D2", length=8, models={"delay_model": FibreDelayModel(), "quantum_loss_model": FibreLossModel(p_loss_init=0,p_loss_length=0.2), "quantum_noise_model": DepolarNoiseModel(depolar_rate=1e3, time_independent=False)}, transmit_empty_items=True)
    channel_D22E = CombinedChannel("QC_channel_D22E", length=8, models={"delay_model": FibreDelayModel(), "quantum_loss_model": FibreLossModel(p_loss_init=0,p_loss_length=0.2), "quantum_noise_model": DepolarNoiseModel(depolar_rate=1e3, time_independent=False)}, transmit_empty_items=True)
    connect_E2D2 = DirectConnection("Connection_E2D2", channel_AtoB=channel_E2D2, channel_BtoA=channel_D22E)
    network.add_connection(E,D2,connection=connect_E2D2,label="E_to_D2", port_name_node1="port_D2",port_name_node2="port_E")

    #alice_protocol = qkd.AliceProtocol(C,"port_C_A",channel_C2A)
    #bob_protocol = qkd.BobProtocol(bob,"port_A_C")

    # #alice_protocol.receiver_protocol = bob_protocol
    # #bob_protocol.sender_protocol = alice_protocol
    #
    #key_establish = EstablishKey(alice_protocol,bob_protocol)
    overall_protocol = OverallProtocol(A, B, C, D1, D2, E, channel_A2C, channel_B2C, channel_D22C, channel_D12C,
                                          channel_D12E, channel_D22E)

    # ns.sim_reset()
    overall_protocol.start()
    stats = ns.sim_run()
    print(stats)