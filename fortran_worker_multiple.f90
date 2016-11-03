elemental subroutine str2int(str, int, stat)
    implicit none
    character(len=*), intent(in) :: str
    integer, intent(out)         :: int
    integer, intent(out)         :: stat

    read(str, *, iostat=stat)  int
end subroutine str2int


program split_worker
    implicit none
    include 'mpif.h'

    integer :: ipvd, nthr, mpierr, stat
    integer :: color, colored_comm, parent_comm
    character(len=16) :: color_str
    integer :: world_rank, colored_rank
    integer :: world_nprocs, nprocs
    integer :: root
    integer, dimension(:), allocatable :: world_ranks, colored_ranks, world_colors, colors, temp
    integer :: to_send
    integer :: i, multiplier, length
    character (len=256) :: argv1
    double precision :: fraction, partial_pi, pi, pi_out, result, leftover_fraction
    double precision, dimension(2) :: array_result
    double precision, dimension(:,:), allocatable :: array_results

 
    ! Read in this special environemnt variable set by OpenMPI
    ! Context:  http://stackoverflow.com/questions/35924226/openmpi-mpmd-get-communication-size
    ! (See the solution by Hristo Iliev)
    ! The below two lines set `color` to be 0, 1, ..., P where P is the number
    ! of executables given on the command line within `mpiexec` that are colon-deliminated
    call get_environment_variable("OMPI_MCA_orte_app_num", color_str)
    call str2int(color_str, color, stat)

    ! Initialize MPI
    call mpi_init_thread(MPI_THREAD_MULTIPLE, ipvd, mpierr)
    call mpi_comm_rank(mpi_comm_world, world_rank, mpierr)
    call mpi_comm_size(mpi_comm_world, world_nprocs, mpierr)

    call mpi_comm_get_parent(parent_comm, mpierr)

    ! Split the world communicator into separate pieces for each mpiexec subprogram
    call mpi_barrier(mpi_comm_world, mpierr)
    call mpi_comm_split(mpi_comm_world, color, world_rank, colored_comm, mpierr)

    ! Get each core's rank within its new communicator
    call mpi_comm_rank(colored_comm, colored_rank, mpierr)
    ! Get the total number of cores (ie the sum of all the worlds)
    call mpi_comm_size(colored_comm, nprocs, mpierr)
    ! Also set the root to 0 for every processor
    root = 0

    call get_command_argument(1, argv1, length, stat)
    call str2int(argv1, multiplier, stat)

    !write(*,'(A10, I2, A4, I2, A11, I2, A6, I2, A18, I2)') "I am core ", colored_rank, " of ", nprocs, " with color", color, ", root", root, ", and communicator", colored_comm
    
    call mpi_barrier(parent_comm, mpierr)
    call mpi_barrier(mpi_comm_world, mpierr)
    call mpi_barrier(colored_comm, mpierr)


    fraction = 1.0 / 2**(1+colored_rank)
    partial_pi = fraction * 3.14159
    call mpi_reduce(pi, pi_out, 1, MPI_DOUBLE, MPI_SUM, 0, colored_comm, mpierr)
    pi = pi_out

    write(*,"(A,I3,A,I3,A,I2,A,I3,A,I3,A,I3,A,F9.6)") "I am worker with world rank", world_rank, " of", world_nprocs, " and color", color, "; and rank", colored_rank, " of", nprocs, " in the colored communicator. I recieved", multiplier, " as my multiplier and calculated my portion of pi as", partial_pi

    if(colored_rank .eq. root) then
        leftover_fraction = 0.0
        do i=0, nprocs-1
            leftover_fraction = leftover_fraction + 1.0 / 2**(1+i)
        enddo
        leftover_fraction = 1.0 - leftover_fraction
        pi = pi + leftover_fraction * 3.14159
    endif

    if(colored_rank .eq. 0) then
        write(*,"(A,F15.12,A,I3,A,I2)") "The cores were not assigned to calculate ", 100.0*leftover_fraction ,"% of pi, so it has been added to the result by worker", colored_rank, " on color", color
    endif


    call mpi_bcast(pi, 1, MPI_DOUBLE, root, colored_comm, mpierr)
    result = multiplier * pi


    call mpi_barrier(parent_comm, mpierr)
    array_result = (/dble(color), result/)
    allocate(array_results(2, nprocs))
    call mpi_gather(array_result, 2, MPI_DOUBLE, array_results, 2, MPI_DOUBLE, root, parent_comm, mpierr)

    ! Free the sub-communicators and finalize
    call mpi_comm_free(colored_comm, mpierr)
    if(parent_comm .ne. mpi_comm_null) then
        call mpi_comm_disconnect(parent_comm, mpierr)
        write(*,"(A,I3)") "Successfully disconnected worker", world_rank
    endif
    call mpi_finalize(mpierr)

end program split_worker


