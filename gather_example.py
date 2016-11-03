"""
This example creates data contained in a list.
The length of the list is equal to the number of cores mpi4py is using.
Each core gets assigned one piece of data in that list and modifies it.
The updated data is passed to the root via gather, where it is then
broadcast to all the other cores.
"""

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
