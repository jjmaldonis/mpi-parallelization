from subproc import run_subproc

def do_calc():
    run_subproc("mpiexec -n 4 ./testmpi : -n 6 ./testmpi")
    #run_subproc("mpiexec -n 4 ./hrmc test param_file.in : -n 6 ./hrmc test param_file.in")

def main():
    do_calc()


if __name__ == '__main__':
    main()
