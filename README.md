This repository contains MPI examples for [mpi4py](https://bitbucket.org/mpi4py/mpi4py).

### Examples

`worker_multiple.py` is a program that is designed to be run as a worker/child process. `fortran_worker_multiple.f90` is the corresponding FORTRAN example. These programs will be called in the spawning programs below.

`spawn.py` performs a basic spawn. `spawn_loop.py` runs that spawn in a loop.

`spawn_multiple.py` spawns multiple copies of an executable with different data. `spawn_multiple_loop.py` runs that spawn in a loop.

`spawn_fortran_multiple.py` and `spawn_fortran_multiple_loop.py` are the analogous programs that call the FORTRAN worker rather than the Python worker.

### Dependencies

This code has only been tested with Open MPI 1.10.2 and mpi4py 2.0.0.

Open MPI sets the environment variable `OMPI_MCA_orte_app_num`, which is crucial for the `spawn_multiple` commands.

