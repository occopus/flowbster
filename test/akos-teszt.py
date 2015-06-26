from ndimCollector import ndimCollector
from ndimTester import ndimTester
import pprint
import time

infra = ndimTester(11)

"""MG1"""
infra.create_node("MG1",1)
infra.create_inputport("MG1","G1",False)
infra.create_outputport("MG1","O1",3)

"""MG2"""
infra.create_node("MG2",1)
infra.create_inputport("MG2","G1",False)
infra.create_outputport("MG2","O1",5)

"""G1"""
infra.create_node("G1",1)
infra.create_inputport("G1","G1",False)
infra.create_outputport("G1","O1",1)

"""G2"""
infra.create_node("G2",1)
infra.create_inputport("G2","G1",False)
infra.create_outputport("G2","O1",5)

"""N1"""
infra.create_node("N1",1)
infra.create_inputport("N1","G1",False)
infra.create_outputport("N1","O1",1)

"""M"""
infra.create_node("M",3)
infra.create_inputport("M","G1",False)
infra.create_inputport("M","G2",False)
infra.create_inputport("M","G3",False)
infra.create_outputport("M","O1",1)

"""MC1"""
infra.create_node("MC1",1)
infra.create_inputport("MC1","G1",True)
infra.create_outputport("MC1","O1",1)

"""MC2"""
infra.create_node("MC2",1)
infra.create_inputport("MC2","G1",True)
infra.create_outputport("MC2","O1",1)

"""C1"""
infra.create_node("C1",1)
infra.create_inputport("C1","G1",True)
infra.create_outputport("C1","O1",1)

"""C2"""
infra.create_node("C2",1)
infra.create_inputport("C2","G1",False)
infra.create_outputport("C2","O1",1)

"""N2"""
infra.create_node("N2",1)
infra.create_inputport("N2","G1",False)
infra.create_outputport("N2","O1",1)


"""LINKS"""
infra.create_link("MG1","MG2","G1")
infra.create_link("G1","G2","G1")
infra.create_link("MG2","M","G1")
infra.create_link("G2","M","G2")
infra.create_link("N1","M","G3")
infra.create_link("M","MC1","G1")
infra.create_link("MC1","MC2","G1")
infra.create_link("M","C1","G1")
infra.create_link("C1","C2","G1")
infra.create_link("M","N2","G1")

"""ADDING INPUTS"""
infra.feed_input("MG1","G1",[1])
infra.feed_input("G1","G1",[1])
infra.feed_input("N1","G1",[1])
#infra.feed_input("JOB1","G2",[5])

"""SIMULATING NODES"""
infra.simulate_onenode("MG1")
infra.simulate_onenode("MG2")
infra.simulate_onenode("G1")
infra.simulate_onenode("G2")
infra.simulate_onenode("N1")
infra.simulate_onenode("M")
infra.simulate_onenode("MC1")
infra.simulate_onenode("MC2")
infra.simulate_onenode("C1")
infra.simulate_onenode("C2")
infra.simulate_onenode("N2")


"""WATCH ALL NODE INTERNALS"""
infra.dump()
