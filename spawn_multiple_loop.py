# Run with:
# mpiexec -np 16 -oversubscribe -mca btl tcp,sm,self python spawn_multiple_loop.py
from mpi4py import MPI
import sys
import time

rank = MPI.COMM_WORLD.Get_rank()
size = MPI.COMM_WORLD.Get_size()

if rank == 0:
    for i in range(20):
        print("Trying to spawn...", i)
        count = 4
        intercomm = MPI.COMM_SELF.Spawn_multiple([sys.executable]*count, args=['worker_multiple.py']*count, maxprocs=[4]*count)
        print("Spawn successful!")

        intercomm.Disconnect()
        print("Successfully disconnected parent.")
        print('')

