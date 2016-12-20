"""
Calls the spawn_fortran_multiple command in spawn_fortran_multiple.py in a loop.

Run with:
    mpiexec -np 4  -oversubscribe  -mca btl tcp,sm,self  python spawn_multiple_loop.py
"""

from mpi4py import MPI
import numpy
import sys
import time

from spawn_fortran_multiple import spawn_fortran_multiple


def main(split_into=2, nloops=3):
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
        print("At each iteration we will spawn {} workers with {} cores each out of a total of {} cores.".format(split_into, cores_per_comm, size))
        print("Those {} split communicators will get the following as input:".format(split_into))
        for i in range(split_into):
            print("    Communicator {}: {}".format(i, data_by_process[i]))

        for i in range(nloops):
            print("Iteration {}...".format(i))
            spawn_fortran_multiple(size, split_into, cores_per_comm, data_by_process)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--split_into', default=2, type=int)
    parser.add_argument('-n', '--nloops', default=3, type=int)
    args = parser.parse_args()
    main(split_into=args.split_into, nloops=args.nloops)

