"""
A master-worker example that spawns a worker process of the same size as the master process.
The worker process calcuates PI and the master prints out the result.

Run with:
    mpiexec -np 4  -oversubscribe  -mca btl tcp,sm,self  python spawn.py
"""

from mpi4py import MPI
import numpy
import sys
import time

from check_mpi import check_mpi


def main():
    check_mpi()
    world = MPI.COMM_WORLD
    rank = world.Get_rank()
    size = world.Get_size()

    multiplier = 1
    color = 0
    args = [str(multiplier), str(color)]

    if rank == 0:
        spawn(args, size)


def spawn(args, size):
    print("Trying to spawn...")
    intercomm = MPI.COMM_SELF.Spawn(sys.executable, args=['worker_multiple.py']+args, maxprocs=size)
    print("Spawn successful!")

    # First use a barrier to interact with parent.barrier() in worker_multiple.py
    intercomm.barrier()

    # Then use a gather to show how to pass information back and forth
    intercomm.barrier()
    results = intercomm.gather(None, root=MPI.ROOT)
    results = {color: data for color, data in results}  # Remove duplicate color info
    results = [data for _, data in sorted(results.items())]  # Recast to a list with just the data, sorted by color
    print("After parcing the results by color, the parent gathered the following data:  {}".format(results))

    intercomm.Disconnect()
    print("Successfully disconnected parent.")
    print('')


if __name__ == '__main__':
    main()

