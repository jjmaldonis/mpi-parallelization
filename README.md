This repository contains MPI examples for [mpi4py](https://bitbucket.org/mpi4py/mpi4py).

### Examples

#### Basic Gather Examples

* `gather.py` uses each core to update a different piece of information in a list and passes that information to all cores using the `.gather` and `.bcast` methods.  The `allgather.py` example is similar, but uses the `.allgather` method instead; it then parses the resulting information to keep only the updated values.

#### Spawn Multiple Examples

* `spawn_multiple_worker.py` is a program designed to be run as a worker/child process. `spawn_multiple_worker_fortran.f90` is the corresponding FORTRAN example. These programs will be called in the spawning programs below. They distribute a calculation of pi over the cores that were allocated to them and return the reduced-sum value to their parent process.

* `spawn.py` is the most basic example of spawning, and performs a single spawn. `spawn_loop.py` has similar functionality, but spawns workers iteratively, waiting for each child process to finish before starting a new one.

* `spawn_multiple.py` spawns multiple copies of an executable with different data. `spawn_multiple_loop.py` spawns multiple executables during each iteration of a loop.

* `spawn_fortran_multiple.py` and `spawn_fortran_multiple_loop.py` are the analogous programs that call the FORTRAN worker rather than the Python worker.

#### Split-Spawn Examples

* `split_multiple.py` is an analogous program to `spawn_multiple.py`, only rather than using spawn_multiple, it splits the world communicator within the parent process and then spawns processes on the newly created communicators. The worker process can be found in `split_multiple_worker.py`.

* `split_multiple_loop.py` splits and spawns multiple executables within a loop.

### Dependencies

This code has only been tested with Open MPI 1.10.2 and mpi4py 2.0.0.

Open MPI sets the environment variable `OMPI_MCA_orte_app_num`, which is crucial for the `spawn_multiple` commands. This necessity can be avoided in other MPI implementations by passing the color in to the worker program. This is illustrated in the examples.

