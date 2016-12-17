"""
A worker/child program that calculates PI, multiplies it by the first argument to this program, and returns the value to the parent.
It should not be run as a stand-alone program.
"""

from mpi4py import MPI
import numpy
import sys, os


def split_and_calculate_pi(multiplier, color=None):
    parent = MPI.Comm.Get_parent()
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    if color is None:
        color = int(os.environ['OMPI_MCA_orte_app_num'])  # An OMPI environment variable specifies the color when using MPMD

    # Split the communicator.
    colored_comm = comm.Split(color)
    colored_size = colored_comm.Get_size()
    colored_rank = colored_comm.Get_rank()

    # Use a barrier to interact with intercomm.barrier() in spawn_multiple_loop.py for demonstration.
    parent.barrier()

    # Show that you can still use the entire world's communicator.
    # However, since the point of this example is to split this communicator,
    # it should never be used because different cores have different data
    comm.barrier()


    # Perform an internal operation on the colored_comms which calculates.
    # Each core in the colored communicator will calculate a differnt portion of PI
    # and then it will get reduced to the root
    fraction = 1 / 2**(1+colored_rank)
    partial_pi = fraction * 3.14159
    pi = colored_comm.reduce(partial_pi, op=MPI.SUM, root=0)

    print("I am worker with world rank {} of {} and color {}; and rank {} of {} in the colored communicator.  \
I recieved {} as my multiplier and calculated my portion of pi as {}.".format( \
           rank, size, color, colored_rank, colored_size, multiplier, partial_pi))
    sys.stdout.flush()

    if colored_rank == 0:
        # Use the root on the colored_comm to fix any bit of pi that the cores within colored_comm were not given to calculate
        leftover_fraction = 1.0 - sum( ( 1 / 2**(1+i)) for i in range(colored_size) )
        pi += leftover_fraction * 3.14159
        print("The cores were not assigned to calculate {}% of pi, so it has been added to the \
result by worker {} on color {}.".format(100.0*leftover_fraction, colored_rank, color))

    # Multiply the calculated value of PI by the input value
    data = multiplier * colored_comm.bcast(pi)

    # And finally demonstrate how to pass this data back to the parent process, where it will be parsed by color.
    # Note that each core in the colored_comms sends information back to the parent.
    # However, since we reduced and broadcasted that data within the colored_comms first, each core with the same color has identical data.
    parent.barrier()
    x = [color, data]
    parent.gather(x, root=0)  # Note that root=0 refers to the parent core that originally did the spawning


    parent.Disconnect()
    print("Successfully disconnected worker with rank {} and color {}.".format(rank, color))


if __name__ == '__main__':
    multiplier = float(sys.argv[1])
    try:
        color = int(sys.argv[2])
    except:
        color = None
    split_and_calculate_pi(multiplier, color)

