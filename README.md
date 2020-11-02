# Web server simulator
## REQUIREMENTS:

- To run webserver.py, python version 3.5 or above is required.
- Libraries required are:-
-- time
-- math
-- statistics
-- argparse


--------------------------------
## EXECUTION:

Sample execution command is:$ python3 webserver.py -l 0.25 -Kc 40 -Ki 30 -C 100000 -L 0 -M 1

usage: webserver.py [-h] -l  -Kc  -Ki  -C  -L  -M

optional arguments:
  -h, --help          show this help message and exit
  -l , --Lambda       the parameter λ of the distribution of interarrival times
  -Kc , --CPU_Queue   the number K of customers that the CPU queue may hold
  -Ki , --IO_Queue    the number K of customers that the I/O queue may hold
  -C , --Customers    the number C of customers served before the program terminates
  -L , --L            an integer L such that L = 0 (runs service disciplines), L>0 (runs web server)
  -M , --mode         1 – FCFS, 2 – LCFS-NP, 3 – SJF-NP, 4 – Prio-NP, 5 – Prio-P


--------------------------------
## EXECUTION EXAMPLES:

-> FCFS
python3 webserver.py -l 0.25 -Kc 40 -Ki 30 -C 100000 -L 0 -M 1

-> LCFS
python3 webserver.py -l 0.25 -Kc 40 -Ki 30 -C 100000 -L 0 -M 2

-> SJF
python3 webserver.py -l 0.25 -Kc 40 -Ki 30 -C 100000 -L 0 -M 3

-> Priority-Non Preemptive
python3 webserver.py -l 0.25 -Kc 40 -Ki 30 -C 100000 -L 0 -M 4

-> Priority-Preemptive
python3 webserver.py -l 0.25 -Kc 40 -Ki 30 -C 100000 -L 0 -M 5


-> Web Server
python3 webserver.py -l 0.25 -Kc 40 -Ki 30 -C 100000 -L 1 -M 1
