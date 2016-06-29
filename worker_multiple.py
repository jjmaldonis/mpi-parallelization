from mpi4py import MPI
import sys

print("Starting worker")
parent = MPI.Comm.Get_parent()
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
print("I am worker {} of {}".format(rank, size))
sys.stdout.flush()

parent.Disconnect()
print("Successfully disconnected worker.")
