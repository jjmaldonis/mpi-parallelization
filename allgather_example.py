"""
Similar to the gather example, but this uses allgather and parses the results
to reflect the original list structure and discards the old data.
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

print("Starting data for rank {}:  {}".format(rank, data))


# Assign a piece of data to each core
positions_per_core = {i: i for i in range(len(data))}

# Update the data assigned to this core
data[positions_per_core[rank]] += 1

# Allgather all the data
all_data = comm.allgather(data)

# Create a single updated piece of data based on the updates that each core performed
data = [all_data[i][positions_per_core[i]] for i in range(size)]

print("Ending data for rank {}:    {}".format(rank, data))
