from math import ceil, log2

class Cache:
    rp_policy = None 
    asc = None
    cache = None
    tag_index = None
    dirty_bit = None
    offset, index, tag = None, None, None
    lru = None
    opt=None
    valid=None
    count=0
    sets = None
    
    read=0
    read_miss=0
    write=0
    write_miss=0
    write_back=0
    write_back_m=0
    def __init__(self,block_size,cache_size,asc,replacement_policy,trace):
        if (cache_size!=0):
            self.sets = cache_size // (block_size * asc)
            self.asc = asc
            self.rp_policy = replacement_policy
            self.cache = [[0 for _ in range(self.asc)] for _ in range(self.sets)]

            self.tag_index= [[0 for _ in range(self.asc)] for _ in range(self.sets)]
            self.dirty_bit = [[0 for _ in range(self.asc)] for _ in range(self.sets)]
            self.valid = [[0 for _ in range(self.asc)] for _ in range(self.sets)]
            self.offset = int(log2(block_size))
            self.index = int(log2(self.sets))
            self.tag = 32 - self.index - self.offset

            if (self.rp_policy == 0 or self.asc == 1):
                self.lru= [[0 for _ in range(self.asc)] for _ in range(self.sets)]
            elif(self.rp_policy==1):
                x=0
                p=1
                temp =0.1
                while(temp!=0):
                    temp= self.asc/pow(2,p)
                    if (temp>0.5):
                        x=x+ceil(temp)
                        p=p+1
                    else:
                        temp=0
                self.lru= [[0 for _ in range(x)] for _ in range(self.sets)]
            elif(self.rp_policy==2):
                self.opt= []
                with open(trace) as f:
                    lines = f.readlines()
                    for line in lines:
                        address= line.split(' ')
                        op=address[0]
                        addr=address[1].strip()
                        int_value= int(addr, 16)
                        bin_value= str(bin(int_value))
                        bin_value=bin_value[2:]
                        while len(bin_value) < 32:
                            bin_value='0'+bin_value
                        self.opt.append(bin_value[:self.tag+self.index])
        
    def retreive_Tag_Index(self,address):
        req_addr=[]
        int_value= int(address, 16)
        bin_value= bin(int_value)
        bin_value=bin_value[2:]
        while len(bin_value) < 32:
            bin_value='0'+bin_value

        tagb=bin_value[:self.tag]
        idxb=bin_value[self.tag:self.tag+self.index]
        req_addr.append(tagb)
        req_addr.append(idxb)

        return req_addr

    def readCache(self,address):
        status = False
        idx=0
        self.read=self.read +1
        ti = self.retreive_Tag_Index(address)
        tg = ti[0]
        idxx = ti[1]
        if (self.sets !=1 ):
            idx =int(idxx,2)
        for i in range(0,self.asc):
            if (self.valid[idx][i]==1):
                if (self.cache[idx][i]==tg):
                    if (self.rp_policy==0 or self.asc==1):
                        self.modify_lru(idx,i)
                    elif(self.rp_policy==1):
                        self.modify_plru(idx,i)
                    status = True
                    break
        if(status==False):
            self.read_miss=self.read_miss+1
        return status

    def writeCache(self,address):
        self.write =self.write+1
        idx=0
        status=False
        ti = self.retreive_Tag_Index(address)
        tg = ti[0]
        idxx = ti[1]
        if (self.sets !=1 ):
            idx =int(idxx,2)
        for i in range(0,self.asc):
            if (self.valid[idx][i]==1):
                if (self.cache[idx][i]==tg):
                    if (self.rp_policy==0 or self.asc==1):
                        self.modify_lru(idx,i)
                    elif(self.rp_policy==1):
                        self.modify_plru(idx,i)
                    status = True
                    self.dirty_bit[idx][i]=1
                    break
        if(status==False):
            self.write_miss=self.write_miss+1
        return status

    def mem_alloc(self,address,counter,op):
        status=False
        idx=0
        ti=[]
        ti = self.retreive_Tag_Index(address)
        tg = ti[0]
        idxx = ti[1]
        if (self.sets !=1 ):
            idx =int(idxx,2)
        for i in range(0,self.asc):
            if (self.valid[idx][i]==0):
                self.cache[idx][i]=tg
                self.tag_index[idx][i]=tg+idxx
                self.valid[idx][i]=1
                status = True
                if (self.rp_policy==0 or self.asc ==1):
                    self.modify_lru(idx,i)
                elif(self.rp_policy==1):
                    self.modify_plru(idx,i)
                if(op=='w'):
                    self.dirty_bit[idx][i]=1
                else:
                    self.dirty_bit[idx][i]=0
                break
        if(status==False):
            return self.replace_alloc(address,counter,op)
        return ""

    
    def replace_alloc(self,address,counter,op):
        idx=0
        ti = self.retreive_Tag_Index(address)
        tg = ti[0]
        idxx = ti[1]
        if (self.sets !=1 ):
            idx =int(idxx,2)
        out = ""
        r_idx=0
        if (self.rp_policy==0 or self.asc ==1):
            r_idx=self.getLRU(idx)
        elif(self.rp_policy==1):
            r_idx=self.getPLRU(idx)
        elif(self.rp_policy==2):
            r_idx=self.getOpt(idx,counter)
        
        if(self.dirty_bit[idx][r_idx]==1):
            self.write_back=self.write_back+1
            out =self.tag_index[idx][r_idx]

        self.cache[idx][r_idx]= tg
        self.tag_index[idx][r_idx]=tg+idxx
        self.valid[idx][r_idx]=1
        
        if (self.rp_policy==0 or self.asc==1):
            self.modify_lru(idx,r_idx)
        elif(self.rp_policy==1):
            self.modify_plru(idx,r_idx)
        
        if(op=='w'):
            self.dirty_bit[idx][r_idx]=1
        else:
            self.dirty_bit[idx][r_idx]=0

        return out
    
    def makeInvalid(self,address):
        out=0
        idx=0
        ti = self.retreive_Tag_Index(address)
        tg = str(ti[0])
        idxx = str(ti[1])
        if (self.sets !=1 ):
            idx =int(idxx,2)
        for i in range(0,self.asc):
            if(self.cache[idx][i]==tg):
                self.valid[idx][i]=0
                out=self.dirty_bit[idx][i]
                break
        if (out==1):
            self.write_back_m=self.write_back_m+1

    def getLRU(self,s):
        min_idx=0
        for i in range(0,self.asc):
            if (self.lru[s][i]< self.lru[s][min_idx]):
                min_idx=i
        return min_idx
    

    def modify_lru(self,i,j):
        self.lru[i][j] =self.count
        self.count=self.count+1

    def getPLRU(self,set):
        x=""
        i=1
        while(i-1 < len(self.lru[0])):
            x=x+str(self.lru[set][i-1])
            if (self.lru[set][i-1]==0):
                i= (2*i) +1
            else:
                i=2*i
        xx= list(x)
        y=""
        for j in range(0,len(x)):
            if (xx[j]=='0'):
                y=y+'1'
            else:
                y=y+'0'
        return int(y,2)


    
   
    def modify_plru(self,set,idx):
        x=bin(idx)
        x=x[2:]
        l= ceil(log2(self.asc))
        while (len(x)<l):
            x='0'+x
        y=list(x)
        f=1
        for i in range(0,len(x)):
            self.lru[set][f-1]=int(y[i])
            if (y[i]=='0'):
                f=(2*f)
            else:
                f=(2*f)+1
    
    def getOpt(self, set,counter):
        temp=[0]*self.asc
        count=0
        for i in range(0,self.asc):
            for j in range(counter-1, len(self.opt)):
                if (self.tag_index[set][i]==self.opt[j]):
                    temp[i]=j
                    count=count+1
                    break
            if (count==i):
                return i
        max_idx =0
        for k in range(0,self.asc):
            if (temp[k]>temp[max_idx]):
                max_idx=k
        return max_idx
