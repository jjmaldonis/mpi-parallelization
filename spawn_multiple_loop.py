"""
Calls the spawn_multiple command in spawn_multiple.py in a loop.


Run with:
    mpiexec -np 4  -oversubscribe  -mca btl tcp,sm,self  python spawn_multiple_loop.py
"""

from mpi4py import MPI
import numpy
import sys
import time

from spawn_multiple import spawn_multiple


def main(split_into=2, nloops=3):
    world = MPI.COMM_WORLD
    rank = world.Get_rank()
    size = world.Get_size()
    if size < split_into:
        raise ValueError("The number of cores passed to 'mpiexec' must be greater than the number of desired communicators.")
    cores_per_comm = size // split_into

    # Create fake data for input for each of the different processes we will spawn
    data_by_process = [str(i+1) for i in range(split_into)]


    if rank == 0:
        print("At each iteration we will spawn {} workers with {} cores each out of a total of {} cores.".format(split_into, cores_per_comm, size))
        print("Those {} workers will get the following as input:".format(split_into))
        for i in range(split_into):
            print("    Worker {}: {}".format(i, data_by_process[i]))
        for i in range(nloops):
            spawn_multiple(split_into, cores_per_comm, data_by_process)

if __name__ == "__main__":
    main()
