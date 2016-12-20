"""
A master-worker example similar to spawn_multiple.py, but this uses a fortran worker.
Each executable is given different data, so the values sent back to the master process are different.

Run with:
    mpiexec -np 4  -oversubscribe  -mca btl tcp,sm,self  python spawn_fortran_multiple.py
"""

from mpi4py import MPI
import numpy
import sys
import time


def main(split_into=2):
    world = MPI.COMM_WORLD
    rank = world.Get_rank()
    size = world.Get_size()
    if size < split_into:
        raise ValueError("The number of cores passed to 'mpiexec' must be greater than the number of desired communicators.")
    cores_per_comm = size // split_into

    # Create fake data for input for each of the different processes we will spawn
    multipliers = [i+1 for i in range(split_into)]
    if 'Open MPI' not in MPI.get_vendor():
        colors = [(i+1)//split_into for i in range(split_into)]
        data_by_process = [(str(multipliers[i]), str(colors[i])) for i in range(split_into)]
    else:
        data_by_process = [(str(multipliers[i]),) for i in range(split_into)]

    if rank == 0:
        print("We will spawn {} workers with {} cores each out of a total of {} cores.".format(split_into, cores_per_comm, size))
        print("Those {} split communicators will get the following as input:".format(split_into))
        for i in range(split_into):
            print("    Communicator {}: {}".format(i, data_by_process[i]))
        spawn_fortran_multiple(size, split_into, cores_per_comm, data_by_process)


def spawn_fortran_multiple(world_size, split_into, cores_per_comm, args):
    print("Trying to spawn...")
    args = [[*data] for data in args]
    intercomm = MPI.COMM_SELF.Spawn_multiple(['spawn_multiple_worker_fortran']*split_into, args=args, maxprocs=[cores_per_comm]*split_into)
    print("Spawn successful!")

    # Use a barrier to interact with parent.barrier() in worker_multiple.py for demonstration
    intercomm.barrier()

    # Then use a gather to show how to pass information back and forth
    intercomm.barrier()
    results = numpy.array([[0.0, 0.0] for _ in range(world_size)], 'float64')
    intercomm.Gather(numpy.array([0.0, 0.0], 'float64'), results, root=MPI.ROOT)
    results = {color: data for color, data in results}  # Remove duplicate color info
    results = [data for _, data in sorted(results.items())]  # Recast to a list with just the data, sorted by color
        
    print("After parcing the results by color, the parent gathered the following data:  {}".format(results))

    intercomm.Disconnect()
    print("Successfully disconnected parent.")
    print('')


if __name__ == "__main__":
    main()

