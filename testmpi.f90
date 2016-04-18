elemental subroutine str2int(str, int, stat)
    implicit none
    character(len=*), intent(in) :: str
    integer, intent(out)         :: int
    integer, intent(out)         :: stat

    read(str, *, iostat=stat)  int
end subroutine str2int


program rmc
    implicit none
    include 'mpif.h'

    integer :: ipvd, nthr, mpierr, stat
    integer :: color, colored_comm
    character(len=16) :: color_str
    integer :: world_rank, rank
    integer :: world_nprocs, nprocs
    integer :: root
    integer, dimension(:), allocatable :: world_ranks, ranks, world_colors, colors, temp
    integer :: to_send

 
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
    write(*,*) "Core", world_rank, "has color", color

    ! Split the world communicator into separate pieces for each mpiexec subprogram
    call mpi_barrier(mpi_comm_world, mpierr)
    call mpi_comm_split(mpi_comm_world, color, world_rank, colored_comm, mpierr)

    ! Get each core's rank within its new communicator
    call mpi_comm_rank(colored_comm, rank, mpierr)
    ! Get the total number of cores (ie the sum of all the worlds)
    call mpi_comm_size(colored_comm, nprocs, mpierr)
    ! Also set the root to 0 for every processor
    root = 0

    call mpi_barrier(colored_comm, mpierr)
    write(*,'(A10, I2, A4, I2, A11, I2, A6, I2, A18, I2)') "I am core ", rank, " of ", nprocs, " with color", color, ", root", root, ", and communicator", colored_comm

    ! Allocate space for a few variables that are going to be used for gathering and printing
    allocate(world_ranks(nprocs), stat=stat)
    world_ranks = -1

    ! Gather each 'rank' into 'world_ranks' on processor 'root' through each 'colored_comm'
    call mpi_gather(world_rank, 1, MPI_INT, world_ranks, 1, MPI_INT, root, colored_comm, mpierr)

    call mpi_barrier(colored_comm, mpierr)
    if(rank .eq. root) then
        write(*,*) "World", color, "got the following ranks from the whole world:", world_ranks
    endif

    ! Now try a bcast
    if(rank .eq. root) then
        to_send = 5
    endif
    call mpi_barrier(colored_comm, mpierr)
    call mpi_bcast(to_send, 1, MPI_INT, root, colored_comm, mpierr)
    write(*,'(A10, I2, A10, I2, A32)') "I am core ", rank, " and I got", to_send, " broadcasted to me from my root."

    ! Free the sub-communicators and finalize
    call mpi_comm_free(colored_comm, mpierr)
    call mpi_finalize(mpierr)

end program rmc




! Example output:
! Core           5 has color           1
! Core           8 has color           1
! Core           9 has color           1
! Core          11 has color           1
! Core          12 has color           1
! Core          13 has color           1
! Core          14 has color           1
! Core          15 has color           1
! Core           0 has color           0
! Core           1 has color           0
! Core           2 has color           0
! Core           3 has color           0
! Core           4 has color           1
! Core           6 has color           1
! Core           7 has color           1
! Core          10 has color           1
! I am core  6 of 12 with color 1, root 0, and communicator 3
! I am core 11 of 12 with color 1, root 0, and communicator 3
! I am core  0 of  4 with color 0, root 0, and communicator 3
! World           0 got the following ranks from the whole world:           0
!            1           2           3
! I am core  0 and I got 5 broadcasted to me from my root.
! I am core  1 of  4 with color 0, root 0, and communicator 3
! I am core  1 and I got 5 broadcasted to me from my root.
! I am core  2 of  4 with color 0, root 0, and communicator 3
! I am core  2 and I got 5 broadcasted to me from my root.
! I am core  3 of  4 with color 0, root 0, and communicator 3
! I am core  3 and I got 5 broadcasted to me from my root.
! I am core  0 of 12 with color 1, root 0, and communicator 3
! World           1 got the following ranks from the whole world:           4
!            5           6           7           8           9          10
!           11          12          13          14          15
! I am core  0 and I got 5 broadcasted to me from my root.
! I am core  2 of 12 with color 1, root 0, and communicator 3
! I am core  2 and I got 5 broadcasted to me from my root.
! I am core  1 of 12 with color 1, root 0, and communicator 3
! I am core  1 and I got 5 broadcasted to me from my root.
! I am core  4 of 12 with color 1, root 0, and communicator 3
! I am core  4 and I got 5 broadcasted to me from my root.
! I am core  3 of 12 with color 1, root 0, and communicator 3
! I am core  3 and I got 5 broadcasted to me from my root.
! I am core  5 of 12 with color 1, root 0, and communicator 3
! I am core  5 and I got 5 broadcasted to me from my root.
! I am core  7 of 12 with color 1, root 0, and communicator 3
! I am core  7 and I got 5 broadcasted to me from my root.
! I am core  8 of 12 with color 1, root 0, and communicator 3
! I am core  8 and I got 5 broadcasted to me from my root.
! I am core  9 of 12 with color 1, root 0, and communicator 3
! I am core  9 and I got 5 broadcasted to me from my root.
! I am core 10 of 12 with color 1, root 0, and communicator 3
! I am core 10 and I got 5 broadcasted to me from my root.
! I am core 11 and I got 5 broadcasted to me from my root.
! I am core  6 and I got 5 broadcasted to me from my root.
