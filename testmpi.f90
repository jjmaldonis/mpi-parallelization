program rmc

    use omp_lib
    implicit none
    include 'mpif.h'
    integer :: ipvd, nthr, myid, numprocs, mpierr

    write(*,*) "BEGINNING"

    call mpi_init_thread(MPI_THREAD_MULTIPLE, ipvd, mpierr)
    call mpi_comm_rank(mpi_comm_world, myid, mpierr)
    call mpi_comm_size(mpi_comm_world, numprocs, mpierr)

    nthr = omp_get_max_threads()
    if(myid.eq.0)then
        write(*,*)
        write(*,*) "Using", numprocs, "processors."
        write(*,*) "OMP found a max number of threads of", nthr
        write(*,*)
    endif

    write(*,*) "I am core", myid

    call mpi_finalize(mpierr)

    write(*,*) "END"

end program rmc
