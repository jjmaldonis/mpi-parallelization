import os
import distutils.spawn
import mpi4py
from mpi4py import MPI

def check_mpi():
    mpiexec_path, _ = os.path.split(distutils.spawn.find_executable("mpiexec"))
    for executable, path in mpi4py.get_config().items():
        if executable not in ['mpicc', 'mpicxx', 'mpif77', 'mpif90', 'mpifort']:
            continue
        if mpiexec_path not in path:
            raise ImportError("mpi4py may not be configured against the same version of 'mpiexec' that you are using. The 'mpiexec' path is {mpiexec_path} and mpi4py.get_config() returns:\n{mpi4py_config}\n".format(mpiexec_path=mpiexec_path, mpi4py_config=mpi4py.get_config()))
    if 'Open MPI' not in MPI.get_vendor():
        raise ImportError("mpi4py must have been installed against Open MPI in order for StructOpt to function correctly.")
    vendor_number = ".".join([str(x) for x in MPI.get_vendor()[1]])
    if vendor_number not in mpiexec_path:
        raise ImportError("The MPI version that mpi4py was compiled against does not match the version of 'mpiexec'. mpi4py's version number is {}, and mpiexec's path is {}".format(MPI.get_vendor(), mpiexec_path))
