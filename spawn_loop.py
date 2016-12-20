"""
Calls the spawn command in spawn.py in a loop.

Run with:
    mpiexec -np 4  -oversubscribe  -mca btl tcp,sm,self  python spawn_loop.py
"""

from mpi4py import MPI
import numpy
import sys
import time

from spawn import spawn


def main(split_into=2, nloops=3):
    world = MPI.COMM_WORLD
    rank = world.Get_rank()
    size = world.Get_size()
    if size < split_into:
        raise ValueError("The number of cores passed to 'mpiexec' must be greater than the number of desired communicators.")

    if rank == 0:
        for i in range(nloops):
            print("Iteration {}...".format(i))
            args = [str(i+1)]
            spawn(args, size)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--split_into', default=2, type=int)
    parser.add_argument('-n', '--nloops', default=3, type=int)
    args = parser.parse_args()
    main(split_into=args.split_into, nloops=args.nloops)

