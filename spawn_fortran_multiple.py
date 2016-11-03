"""
A master-worker example similar to spawn.py and https://mpi4py.scipy.org/docs/usrman/tutorial.html#compute-pi
This example uses `Spawn_multiple` rather than `Spawn` to create multiple copies of the same executable.
Each executable is given different data, so the values sent back to the master process are different.


Run with:
    mpiexec -np 4  -oversubscribe  -mca btl tcp,sm,self  python spawn_multiple.py
"""

from mpi4py import MPI
import numpy
import sys
import time


def main(split_into=2):
    import os
    import distutils.spawn
    import mpi4py
    mpiexec_path, _ = os.path.split(distutils.spawn.find_executable("mpiexec"))
    for executable, path in mpi4py.get_config().items():
        if mpiexec_path not in path:
            raise ImportError("mpi4py may not be configured against the same version of 'mpiexec' that you are using. The 'mpiexec' path is {mpiexec_path} and mpi4py.get_config() returns:\n{mpi4py_config}\n".format(mpiexec_path=mpiexec_path, mpi4py_config=mpi4py.get_config()))
    if 'Open MPI' not in MPI.get_vendor():
        raise ImportError("mpi4py must have been installed against Open MPI in order for StructOpt to function correctly.")
    vendor_number = ".".join([str(x) for x in MPI.get_vendor()[1]])
    if vendor_number not in mpiexec_path:
        raise ImportError("The MPI version that mpi4py was compiled against does not match the version of 'mpiexec'. mpi4py's version number is {}, and mpiexec's path is {}".format(MPI.get_vendor(), mpiexec_path))

    world = MPI.COMM_WORLD
    rank = world.Get_rank()
    size = world.Get_size()
    if size < split_into:
        raise ValueError("The number of cores passed to 'mpiexec' must be greater than the number of desired communicators.")
    cores_per_comm = size // split_into

    # Create fake data for input for each of the different processes we will spawn
    data_by_process = [str(i+1) for i in range(split_into)]

    if rank == 0:
        print("We will spawn {} workers with {} cores each out of a total of {} cores.".format(split_into, cores_per_comm, size))
        print("Those {} split communicators will get the following as input:".format(split_into))
        for i in range(split_into):
            print("    Communicator {}: {}".format(i, data_by_process[i]))
        spawn_fortran_multiple(split_into, cores_per_comm, data_by_process)


def spawn_fortran_multiple(split_into, cores_per_comm, args):
    print("Trying to spawn...")
    args = [[data] for data in args]
    intercomm = MPI.COMM_SELF.Spawn_multiple(['fortran_worker_multiple']*split_into, args=args, maxprocs=[cores_per_comm]*split_into)
    print("Spawn successful!")

    # Use a barrier to interact with parent.barrier() in worker_multiple.py for demonstration
    intercomm.barrier()

    # Then use a gather to show how to pass information back and forth
    intercomm.barrier()
    results = numpy.array([[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]], 'float64')
    intercomm.Gather(numpy.array([0.0, 0.0], 'float64'), results, root=MPI.ROOT)
    results = {color: data for color, data in results}  # Remove duplicate color info
    results = [data for _, data in sorted(results.items())]  # Recast to a list with just the data, sorted by color
        
    print("After parcing the results by color, the parent gathered the following data:  {}".format(results))

    intercomm.Disconnect()
    print("Successfully disconnected parent.")
    print('')


if __name__ == "__main__":
    main()
