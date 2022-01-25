import netsquid as ns
import pydynaa
from netsquid.components.component import Component
from netsquid.components import QuantumDetector, QSource, Clock
import numpy as np
from netsquid.qubits.qubitapi import *
#from netsquid.components.models import FibreDelayModel, FibreLossModel, DepolarNoiseModel
from pydynaa.core import SimulationEngine
import random as rd

class DelayLineInterferometer(Component):

    def __init__(self,name,delay=1):
        super().__init__(name=name,port_names=["qin","cout0","cout1"])
        self.delay_time = delay
        self.sim_engine = SimulationEngine()
        self.detector_click_event = pydynaa.EventType("CLICK","Click the detectors")


    def _high_amplitude_detector(self,event):
        qubit, = create_qubits(1,'Q')
        # print(f'The time when the destructive detector was clicked: {ns.sim_time()}')
        assign_qstate(qubit,ns.qubits.ketstates.s0)
        self.ports["cout0"].tx_output(qubit)
        event.unschedule()

    def _zero_amplitude_detector(self,event):
        qubit, = create_qubits(1,'Q')
        # print(f'The time when the destructive detector was clicked: {ns.sim_time()}')
        assign_qstate(qubit,ns.qubits.ketstates.s1)
        self.ports["cout1"].tx_output(qubit)
        event.unschedule()

    def first_constructive_second_constructive(self):
        rng = np.random.choice([1,2,3,4],p=[1/6,1/3,1/3,1/6])
        if rng == 1:
            first_event_handler = pydynaa.EventHandler(self._high_amplitude_detector)
            self._schedule_at(self.sim_engine.current_time + 1, self.detector_click_event)
            self._wait_once(first_event_handler,self,self.detector_click_event)
        elif rng == 2:
            second_event_handler = pydynaa.EventHandler(self._high_amplitude_detector)
            self._schedule_at(self.sim_engine.current_time + 2, self.detector_click_event)
            self._wait_once(second_event_handler,self,self.detector_click_event)
        elif rng == 3:
            third_event_handler = pydynaa.EventHandler(self._high_amplitude_detector)
            self._schedule_at(self.sim_engine.current_time + 3, self.detector_click_event)
            self._wait_once(third_event_handler,self,self.detector_click_event)
        else:
            last_event_handler = pydynaa.EventHandler(self._high_amplitude_detector)
            self._schedule_at(self.sim_engine.current_time + 4, self.detector_click_event)
            self._wait_once(last_event_handler,self,self.detector_click_event)

    def first_constructive_second_destructive(self):
        rng = np.random.choice([1,2,3,4],p=[1/6,1/3,1/3,1/6])
        if rng == 1:
            first_event_handler = pydynaa.EventHandler(self._high_amplitude_detector)
            self._schedule_at(self.sim_engine.current_time + 1, self.detector_click_event)
            self._wait_once(first_event_handler,self,self.detector_click_event)
        elif rng == 2:
            second_event_handler = pydynaa.EventHandler(self._high_amplitude_detector)
            self._schedule_at(self.sim_engine.current_time + 2, self.detector_click_event)
            self._wait_once(second_event_handler,self,self.detector_click_event)
        elif rng == 3:
            third_event_handler = pydynaa.EventHandler(self._zero_amplitude_detector)
            self._schedule_at(self.sim_engine.current_time + 3, self.detector_click_event)
            self._wait_once(third_event_handler,self,self.detector_click_event)
        else:
            last_event_handler = pydynaa.EventHandler(self._high_amplitude_detector)
            self._schedule_at(self.sim_engine.current_time + 4, self.detector_click_event)
            self._wait_once(last_event_handler,self,self.detector_click_event)

    def first_destructive_second_destructive(self):
        rng = np.random.choice([1,2,3,4],p=[1/6,1/3,1/3,1/6])
        if rng == 1:
            first_event_handler = pydynaa.EventHandler(self._high_amplitude_detector)
            self._schedule_at(self.sim_engine.current_time + 1, self.detector_click_event)
            self._wait_once(first_event_handler,self,self.detector_click_event)
        elif rng == 2:
            second_event_handler = pydynaa.EventHandler(self._zero_amplitude_detector)
            self._schedule_at(self.sim_engine.current_time + 2, self.detector_click_event)
            self._wait_once(second_event_handler,self,self.detector_click_event)
        elif rng == 3:
            third_event_handler = pydynaa.EventHandler(self._zero_amplitude_detector)
            self._schedule_at(self.sim_engine.current_time + 3, self.detector_click_event)
            self._wait_once(third_event_handler,self,self.detector_click_event)
        else:
            last_event_handler = pydynaa.EventHandler(self._high_amplitude_detector)
            self._schedule_at(self.sim_engine.current_time + 4, self.detector_click_event)
            self._wait_once(last_event_handler,self,self.detector_click_event)

    def first_destructive_second_constructive(self):
        rng = np.random.choice([1,2,3,4],p=[1/6,1/3,1/3,1/6])
        if rng == 1:
            first_event_handler = pydynaa.EventHandler(self._high_amplitude_detector)
            self._schedule_at(self.sim_engine.current_time + 1, self.detector_click_event)
            self._wait_once(first_event_handler,self,self.detector_click_event)
        elif rng == 2:
            second_event_handler = pydynaa.EventHandler(self._zero_amplitude_detector)
            self._schedule_at(self.sim_engine.current_time + 2, self.detector_click_event)
            self._wait_once(second_event_handler,self,self.detector_click_event)
        elif rng == 3:
            third_event_handler = pydynaa.EventHandler(self._high_amplitude_detector)
            self._schedule_at(self.sim_engine.current_time + 3, self.detector_click_event)
            self._wait_once(third_event_handler,self,self.detector_click_event)
        else:
            last_event_handler = pydynaa.EventHandler(self._high_amplitude_detector)
            self._schedule_at(self.sim_engine.current_time + 4, self.detector_click_event)
            self._wait_once(last_event_handler,self,self.detector_click_event)

    def interference(self,photon):
        state = photon.qstate.qrepr.ket
        first_phase = (state[0][0] + state[1][0])/(2*0.57735)
        second_phase = (state[1][0] + state[2][0])/(2*0.57735)
        discard(photon)
        if first_phase == 1 and second_phase == 1:
            self.first_constructive_second_constructive()
        elif first_phase == 1 and second_phase == 0:
            self.first_constructive_second_destructive()
        elif first_phase == 0 and second_phase == 0:
            self.first_destructive_second_destructive()
        else:
            self.first_destructive_second_constructive()

    def start(self):
        input_port = self.ports["qin"]
        p = input_port.rx_input().items
        [photon] = p
        print(f'The photon {photon} received by Bob at time {ns.sim_time()}')
        self.interference(photon)

class ConstructiveInterferenceDetector(QuantumDetector):

    def __init__(self,name,system_delay=0,dead_time=0,models=None,error_on_fail=False,properties=None):
        super().__init__(name=name,num_input_ports=1,num_output_ports=1,observable=ns.Z,system_delay=system_delay,dead_time=dead_time,models=models,error_on_fail=error_on_fail,properties=properties)

class DestructiveInterferenceDetector(QuantumDetector):

    def __init__(self,name,system_delay=0,dead_time=0,models=None,error_on_fail=False,properties=None):
        super().__init__(name=name,num_input_ports=1,num_output_ports=1,observable=ns.Z,system_delay=system_delay,dead_time=dead_time,models=models,error_on_fail=error_on_fail,properties=properties)

class BeamSplitter(Component):

    def __init__(self,name):
        super().__init__(name=name,port_names=["qin","qout"])
        self.sim_engine = SimulationEngine()
        self.first_time_bin = 0.57735
        self.second_time_bin = None
        self.third_time_bin = None
        self.second_time_bin_event_0 = pydynaa.EventType('Second time 0','Second time bin for 0')
        self.second_time_bin_event_1 = pydynaa.EventType('Second time 1','Second time bin for 1')
        self.third_time_bin_event_00 = pydynaa.EventType('Third time 00','Third time bin 00')
        self.third_time_bin_event_01 = pydynaa.EventType('Third time 01','Third time bin 01')
        self.third_time_bin_event_10 = pydynaa.EventType('Third time 10','Third time bin 10')
        self.third_time_bin_event_11 = pydynaa.EventType('Third time 11','Third time bin 11')
        self.finished_evtype = pydynaa.EventType("finished","Finished for a photon")
        self.finished_evexpr = pydynaa.EventExpression(self,self.finished_evtype)
        self.received_photon = None
        self.ports["qin"].bind_input_handler(self._start)

    raw_key = {}

    # def _handle_third_bin_for_00(self,event):
    #     self.third_time_bin = (+1)*self.first_time_bin
    #     self.raw_key[ns.sim_time()+3] = 0
    #     self._set_photon_state()
    #     event.unschedule()

    # def _handle_third_bin_for_01(self,event):
    #     self.third_time_bin = (-1)*self.first_time_bin
    #     self.raw_key[ns.sim_time()+3] = 1
    #     self._set_photon_state()
    #     event.unschedule()

    # def _handle_third_bin_for_10(self,event):
    #     self.third_time_bin = (-1)*self.first_time_bin
    #     self.raw_key[ns.sim_time()+3] = 0
    #     self._set_photon_state()
    #     event.unschedule()

    # def _handle_third_bin_for_11(self,event):
    #     self.third_time_bin = (+1)*self.first_time_bin
    #     self.raw_key[ns.sim_time()+3] = 1
    #     self._set_photon_state()
    #     event.unschedule()

    # def _handle_second_bin_for_0(self,event):
    #     self.second_time_bin = (+1)*self.first_time_bin
    #     self.raw_key[ns.sim_time()+2] = 0
    #     print('inside s 0')
    #     if rd.randint(0,1) == 0:
    #         third_bin_handler_00 = pydynaa.EventHandler(self._handle_third_bin_for_00)
    #         third_00 = self._schedule_now(self.third_time_bin_event_00)
    #         self._wait(third_bin_handler_00,self,self.third_time_bin_event_00)
    #     else:
    #         third_bin_handler_01 = pydynaa.EventHandler(self._handle_third_bin_for_01)
    #         third_01 = self._schedule_now(self.third_time_bin_event_01)
    #         self._wait(third_bin_handler_01,self,self.third_time_bin_event_01)
    #     event.unschedule()

    # def _handle_second_bin_for_1(self,event):
    #     self.second_time_bin = (-1)*self.first_time_bin
    #     self.raw_key[ns.sim_time()+2] = 1
    #     print('inside s 1')
    #     if rd.randint(0,1) == 0:
    #         third_bin_handler_10 = pydynaa.EventHandler(self._handle_third_bin_for_10)
    #         third_10 = self._schedule_now(self.third_time_bin_event_10)
    #         self._wait(third_bin_handler_10,self,self.third_time_bin_event_10)
    #     else:
    #         third_bin_handler_11 = pydynaa.EventHandler(self._handle_third_bin_for_11)
    #         third_11 =self._schedule_now(self.third_time_bin_event_11)
    #         self._wait(third_bin_handler_11,self,self.third_time_bin_event_11)
    #     event.unschedule()

    # def _split_in_time_bins(self,event):
    #     if rd.randint(0,1) == 0:
    #         second_bin_handler_0 = pydynaa.EventHandler(self._handle_second_bin_for_0)
    #         second_0 = self._schedule_now(self.second_time_bin_event_0)
    #         self._wait(second_bin_handler_0,self,self.second_time_bin_event_0)
    #         event.unschedule()
    #     else:
    #         second_bin_handler_1 = pydynaa.EventHandler(self._handle_second_bin_for_1)
    #         second_1 = self._schedule_now(self.second_time_bin_event_1)
    #         self._wait(second_bin_handler_1,self,self.second_time_bin_event_1)
    #         event.unschedule()

    # def _set_photon_state(self):
    #     pseudo_photon_1, pseudo_photon_2 = create_qubits(2,"Qubits",no_state=True)
    #     assign_qstate([self.received_photon,pseudo_photon_1,pseudo_photon_2],np.array([self.first_time_bin,self.second_time_bin,self.third_time_bin,0,0,0,0,0]))
    #     print(f'The photon {self.received_photon} sent by Alice at time {ns.sim_time()}')
    #     self.ports["qout"].tx_output(self.received_photon)
    #     self._schedule_now(self.finished_evtype)

    def _start(self,msg):
        [photon] = msg.items
        self.received_photon = photon
        if rd.randint(0,1) == 0:
            self.second_time_bin = (+1) * self.first_time_bin
            self.raw_key[ns.sim_time() + 2] = 0
            if rd.randint(0, 1) == 0:
                self.third_time_bin = (+1) * self.first_time_bin
                self.raw_key[ns.sim_time() + 3] = 0
            else:
                self.third_time_bin = (-1) * self.first_time_bin
                self.raw_key[ns.sim_time() + 3] = 1
        else:
            self.second_time_bin = (-1) * self.first_time_bin
            self.raw_key[ns.sim_time() + 2] = 1
            if rd.randint(0, 1) == 0:
                self.third_time_bin = (-1) * self.first_time_bin
                self.raw_key[ns.sim_time() + 3] = 0
            else:
                self.third_time_bin = (+1) * self.first_time_bin
                self.raw_key[ns.sim_time() + 3] = 1
        pseudo_photon_1, pseudo_photon_2 = create_qubits(2,"Qubits",no_state=True)
        assign_qstate([self.received_photon,pseudo_photon_1,pseudo_photon_2],np.array([self.first_time_bin,self.second_time_bin,self.third_time_bin,0,0,0,0,0]))
        print(f'The photon {self.received_photon} sent by Alice at time {ns.sim_time()}')
        self.ports["qout"].tx_output(self.received_photon)


        # split_evtype = pydynaa.EventType("SPLIT IN TIME", "Start the splitting in time bins")
        # split_handler = pydynaa.EventHandler(self._split_in_time_bins)
        # self._schedule_now(split_evtype)
        # self._wait(split_handler, self, split_evtype)

    # def start(self):
    #     input_port = self.ports["qin"]
    #     [photon] = input_port.rx_input().items
    #     self.received_photon = photon
    #     split_evtype = pydynaa.EventType("SPLIT IN TIME","Start the splitting in time bins")
    #     split_handler = pydynaa.EventHandler(self._split_in_time_bins)
    #     self._schedule_now(split_evtype)
    #     self._wait(split_handler,self,split_evtype)


