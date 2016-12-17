"""
A worker/child program that calculates PI, multiplies it by the first argument to this program, and returns the value to the parent.
It should not be run as a stand-alone program.
"""

from mpi4py import MPI
import numpy
import sys, os


def split_and_calculate_pi(multiplier):
    parent = MPI.Comm.Get_parent()
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    # Split the communicator.
    parent_size = parent.Get_size()
    parent_rank = parent.Get_rank()

    # Use a barrier to interact with intercomm.barrier() in spawn_multiple_loop.py for demonstration.
    parent.barrier()

    # Show that you can still use the entire world's communicator.
    # However, since the point of this example is to split this communicator,
    # it should never be used because different cores have different data
    comm.barrier()


    # Perform an internal operation on the parent which calculates.
    # Each core in the parent communicator will calculate a differnt portion of PI
    # and then it will get reduced to the root
    fraction = 1 / 2**(1+parent_rank)
    partial_pi = fraction * 3.14159
    pi = comm.reduce(partial_pi, op=MPI.SUM, root=0)

    print("I am worker with rank {} of {}. I recieved {} as my multiplier and calculated my portion of pi as {}.".format( \
           rank, size, multiplier, partial_pi))
    sys.stdout.flush()

    if parent_rank == 0:
        # Use the root on the parent to fix any bit of pi that the cores within parent were not given to calculate
        leftover_fraction = 1.0 - sum( ( 1 / 2**(1+i)) for i in range(parent_size) )
        pi += leftover_fraction * 3.14159
        print("The cores were not assigned to calculate {}% of pi, so it has been added to the \
result by worker {}.".format(100.0*leftover_fraction, parent_rank))
        # Multiply the calculated value of PI by the input value
        data = multiplier * pi
    else:
        data = None

    # And finally demonstrate how to pass this data back to the parent process, where it will be parsed.
    # Note that each core in comm sends information back to the parent, but only rank == 0 has data != None.
    parent.barrier()
    parent.gather(data, root=0)  # Note that root=0 refers to the parent core that originally did the spawning

    parent.Disconnect()
    print("Successfully disconnected worker with rank {}.".format(rank))


if __name__ == '__main__':
    multiplier = float(sys.argv[1])
    split_and_calculate_pi(multiplier)

