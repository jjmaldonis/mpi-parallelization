"""
A master-worker example similar to spawn.py and https://mpi4py.scipy.org/docs/usrman/tutorial.html#compute-pi
This example uses `Split` and `Spawn` rather than `Spawn_multiple` to create multiple copies of the same executable.
Each executable is given different data, so the values sent back to the master process are different.

Run with:
    mpiexec -np 4  -oversubscribe  -mca btl tcp,sm,self  python split_multiple.py
"""

from mpi4py import MPI
import numpy
import sys
import os
import time

from check_mpi import check_mpi


def main(split_into=2):
    check_mpi()
    world = MPI.COMM_WORLD
    rank = world.Get_rank()
    size = world.Get_size()
    if size < split_into:
        raise ValueError("The number of cores passed to 'mpiexec' must be greater than the number of desired communicators.")
    cores_per_comm = size // split_into

    # Create fake data for input for each of the different processes we will spawn
    multipliers = [i+1 for i in range(split_into)]
    colors = [(i+1)//split_into for i in range(split_into)]
    data_by_process = [[str(multipliers[i]), str(colors[i])] for i in range(split_into)]

    if rank == 0:
        print("Spawning {} workers with {} cores each out of a total of {} cores.".format(split_into, cores_per_comm, size))
        print("Those {} split communicators will get the following as input:".format(split_into))
        for i in range(split_into):
            print("    Communicator {}: {}".format(i, data_by_process[i]))
    split_multiple(split_into, cores_per_comm, data_by_process)


def split_multiple(split_into, cores_per_comm, args):
    world = MPI.COMM_WORLD
    rank = world.Get_rank()
    size = world.Get_size()
    color = int(args[rank//cores_per_comm][1])
    args = args[rank//cores_per_comm]
    colored_comm = world.Split(color)
    colored_size = colored_comm.Get_size()
    colored_rank = colored_comm.Get_rank()

    if colored_rank == 0:
        print("Trying to spawn...")
        intercomm = MPI.COMM_SELF.Spawn(sys.executable, args=['worker_split_multiple.py']+args, maxprocs=colored_size)
        print("Spawn successful!")

        # Use a barrier to interact with parent.barrier() in worker_multiple.py for demonstration
        intercomm.barrier()

        # Then use a gather to show how to pass information back and forth
        intercomm.barrier()
        results = intercomm.gather(None, root=MPI.ROOT)
        results = [data for data in results if data is not None]
        assert len(results) == 1
        results = results[0]

        intercomm.Disconnect()
        print("Successfully disconnected parent.")
        print('')
    else:
        results = None

    world.barrier()
    results = world.gather((color, colored_rank, results), root=0)
    if rank == 0:
        results = [results for c, cr, results in sorted(results) if cr == 0]
        print("After parcing the results by color, the parent gathered the following data:  {}".format(results))



if __name__ == "__main__":
    main()

