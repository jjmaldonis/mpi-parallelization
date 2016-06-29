import sys
import time
from mpi4py import MPI

rank = MPI.COMM_WORLD.Get_rank()
print("I am rank {} of {}".format(rank, MPI.COMM_WORLD.Get_size()))

t = time.time()
ranks = MPI.COMM_WORLD.allgather(rank)

time.sleep(3)

sys.stdout.flush()
if rank == 0:
    time.sleep(3)

print(time.time()-t)
print(ranks)
