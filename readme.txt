
Step1: Keep Cache_runner.py, cache.py ,sim_cache.py including with the trace files in a single directory and change your present working directory to directory where we saved the above files.

Step 2: Now use the below command to run the program in the command prompt .

Command: Python3 sim_cache.py BlockSize L1Size L1Assoc L2Size L2Assoc Rpolocy IncPolicy Trace.txt
Example: python3 sim_cache.py 16 1024 2 8192 4 0 0 gcc_trace.txt

Note:
Replacement Policy = 0 ==> LRU
Replacement Policy = 1 ==> Pseudo LRU
Replacement Policy = 2 ==> Optimal
Inclusion Policy =0 ==>Non Inclusive
Inclusion Policy =1 ==>Inclusive
