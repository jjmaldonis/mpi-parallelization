import sys
from mpi4py import MPI
from random import shuffle

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
root = 0

data = [i*10 for i in range(size)]
shuffle(data)
data = comm.bcast(data)

print("Starting data for rank {}:        {}".format(rank, data))


# Assign a piece of data to each core
positions_per_core = {i: i for i in range(len(data))}

# Update the data assigned to this core
data[positions_per_core[rank]] += 1

# Allgather all the data
data = comm.gather(data[positions_per_core[rank]])

print("Ending data for rank {}:          {}  (this is only correct on the root)".format(rank, data))
data = comm.bcast(data)
print("After broadcasting, rank {} has:  {}".format(rank, data))
