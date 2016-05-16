from mpi4py import MPI

rank = MPI.COMM_WORLD.Get_rank()
print("I am rank {} of {}".format(rank, MPI.COMM_WORLD.Get_size()))

ranks = MPI.COMM_WORLD.allgather(rank)

print(ranks)
