class cache_runner:
    cache_l1=None
    cache_l2=None
    size_l2=0
    counter=0

    def __init__(self,l1, l2, trace,size_l2):
        self.cache_l1=l1
        self.cache_l2=l2
        self.size_l2=size_l2
        with open(trace) as f:
            self.lines = f.readlines()

    def start_run(self,inc_policy):
        c = 0
        for line in self.lines:
            c += 1
            self.counter= self.counter + 1
            line_input= line.split(' ')
            if 'w' in line_input[0]:
                operation = 'w'
            else:
                operation = 'r'
            #print(c)
            hex_addrress_inp=line_input[1].strip()
            l1_status= False
            l2_status= None
            out=None
            hex_addr=None
            if (operation =='w'):
                l1_status= self.cache_l1.writeCache(hex_addrress_inp)
            elif(operation=='r'):
                l1_status= self.cache_l1.readCache(hex_addrress_inp)
            if ((l1_status==False )and (self.size_l2==0)):
                self.cache_l1.mem_alloc(hex_addrress_inp, self.counter, operation)
            elif((l1_status==False) and (self.size_l2!=0)):
                out = self.cache_l1.mem_alloc(hex_addrress_inp, self.counter, operation)
                if (out != ""):
                    hex_addr=self.bin_to_hex(out)
                    l2_status=self.cache_l2.writeCache(hex_addr)
                    if (l2_status==False):
                        self.cache_l2.mem_alloc(hex_addr, self.counter,'w')
                l2_status=self.cache_l2.readCache(hex_addrress_inp)
                if (l2_status==False):
                    out = self.cache_l2.mem_alloc(hex_addrress_inp,self.counter,"r")
                    if(out != "" and inc_policy==1):
                        hex_addr=self.bin_to_hex(out)
                        self.cache_l1.makeInvalid(hex_addr)
    def display(self):
        print("===== L1 contents =====")
        self.print_content(self.cache_l1)
        if (self.size_l2 !=0):
            print("===== L1 contents =====")
            self.print_content(self.cache_l2)
        print("===== Simulation results (raw) =====")
        print("a. number of L1 reads:       ",self.cache_l1.read)
        print("b. number of L1 read misses: ",self.cache_l1.read_miss)
        print("c. number of L1 writes:      ",self.cache_l1.write)
        print("d. number of L1 write misses:",self.cache_l1.write_miss)
        l1_miss_rate =(self.cache_l1.read_miss + self.cache_l1.write_miss)/(self.cache_l1.read + self.cache_l1.write)
        print("e. L1 miss rate:            {:.6f}".format(l1_miss_rate))
        print("f. number of L1 writebacks:  ", self.cache_l1.write_back)
        traffic = self.cache_l1.read_miss + self.cache_l1.write_miss + self.cache_l1.write_back
        if (self.size_l2 != 0): 
             print("g. number of L2 reads:       ", self.cache_l2.read)
             print("h. number of L2 read misses: ", self.cache_l2.read_miss)
             print("i. number of L2 writes:      ", self.cache_l2.write)
             print("j. number of L2 write misses:", self.cache_l2.write_miss)
             l2_miss_rate =(self.cache_l2.read_miss)/(self.cache_l2.read)
             print("k. L2 miss rate:            {:.6f}". format(l2_miss_rate))
             print("l. number of L2 writebacks:  ", self.cache_l2.write_back)
             traffic = self.cache_l2.read_miss + self.cache_l2.write_miss + self.cache_l2.write_back + self.cache_l1.write_back_m
        else:
            print("g. number of L2 reads:       ", 0)
            print("h. number of L2 read misses: ", 0)
            print("i. number of L2 writes:      ", 0)
            print("j. number of L2 write misses:", 0)
            print("k. L2 miss rate:             ", 0)
            print("l. number of L2 writebacks:  ", 0)
        print ("m. total memory traffic:     ",traffic)
    def print_content(self,c):
        for i in range(0,c.sets):
            print("Set     ",i,":	", end='')
            for j in range(0, c.asc):
                dec_val = int(str(c.cache[i][j]),2)
                h1 = hex(dec_val)
                print(h1[2:], end='')
                if(c.dirty_bit[i][j]==1):
                    print(" D\t", end='')
                else:
                    print (" \t", end='')
            print()
        print("\n")

    def bin_to_hex(self,input_val):
        while len(input_val) < 32:
            input_val += "0"
        dec_val=int(input_val,2)
        h1= hex(dec_val)
        h1= h1[2:]
        return h1
    
