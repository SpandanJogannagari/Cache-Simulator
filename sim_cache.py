import sys
from cache import Cache
from Cache_runner import cache_runner

class sim_cache:
    def main(args):
        if(len(args)!= 8):
            print("Too many arguements")
        else:
            blk_Size = int(args[0])
            size_l1 =int(args[1])
            asc_l1=int(args[2])
            size_l2  = int(args[3])
            asc_l2 = int(args[4])
            rp_policy = int(args[5])
            inc_property = int(args[6])
            trace = str(args[7])
            print("===== Simulator configuration =====")
            print("BLOCKSIZE:            ",blk_Size)
            print("L1_SIZE:              ",size_l1)
            print("L1_ASSOC:             ",asc_l1)
            print("L2_SIZE:              ",size_l2)
            print("L2_ASSOC:             ",asc_l2)
            if (rp_policy==0):
                print("REPLACEMENT POLICY:    LRU")
            elif (rp_policy==1):
                print("REPLACEMENT POLICY:    Pseudo-LRU")
            else:
                print("REPLACEMENT POLICY:    Optimal")
            if(inc_property==0):
                print("INCLUSION PROPERTY:    non-inclusive")
            else:
                print("INCLUSION PROPERTY:    inclusive")
            print("trace_file:           ",trace)
            
            cache_l1 = Cache(blk_Size, size_l1, asc_l1, rp_policy, trace)
            cache_l2 = Cache(0,0,0,rp_policy, trace)
            if (size_l2 !=0):
                cache_l2=Cache(blk_Size, size_l2, asc_l2, rp_policy, trace)
            run_cache = cache_runner(cache_l1,cache_l2,trace,size_l2)
            run_cache.start_run(inc_property)
            run_cache.display()
    main(sys.argv[1:])

# main(1,10,20,30,40,50,60,70)
