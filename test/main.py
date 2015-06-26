from ndimCollector import ndimCollector
from ndimTester import ndimTester
import pprint
import time

infra = ndimTester(3)

"""JOB1"""
infra.create_node("JOB1",2)
infra.create_inputport("JOB1","G1",False)
infra.create_inputport("JOB1","G2",False)
infra.create_outputport("JOB1","O1",4)


"""JOB2"""
infra.create_node("JOB2",1)
infra.create_inputport("JOB2","G1",True)
infra.create_outputport("JOB2","O1",1)

"""JOB3"""
infra.create_node("JOB3",1)
infra.create_inputport("JOB3","G1",True)
infra.create_outputport("JOB3","O1",1)


"""LINKS"""
infra.create_link("JOB1","JOB2","G1")
infra.create_link("JOB2","JOB3","G1")

"""ADDING INPUTS"""
infra.feed_input("JOB1","G1",[2,2])
infra.feed_input("JOB1","G2",[5])

"""SIMULATING NODES"""
infra.simulate_onenode("JOB1")
infra.simulate_onenode("JOB2")
infra.simulate_onenode("JOB3")


"""WATCH ALL NODE INTERNALS"""
infra.dump()
