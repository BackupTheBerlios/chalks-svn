# Base implementation of the paper concepts. This code do not worry about 
# comunication methods.
class ConcurrentEditable:
    """
    This is the core class.
    It instanciate a Site that contain an editable text.
    Will receive and generate operations.
    The implementation is focused on simplicity and paper similarities.
    """
    
    def __init__(self, site_index, num_of_sites):
        """
        if site_index == None then the site is and Observer
        """
                       
        self.site_index   = site_index
        self.state_vector = [0] * num_of_sites
                
        self.state_vector_table   = [[0]* num_of_sites]* num_of_sites # required by the garbage collector (SVT)
        self.minimum_state_vector = [0]*num_of_sites # required by the garbage collector (MSV)

        if self.site_index != None:
            self.state_vector_table [self.site_index] = self.state_vector # link with local state_vector
  
        self.HB = [] # history buffer
        self.delayed_operations = [] 

        self.text_buffer = ""
        
        
    def get_text(self):
        """
        """
        
        return self.text_buffer


    def receive_operation(self, t_op, *args, **kw):
        """
        can receive operations receiving an Operation object, or being called as : (type, pos, data, {extra args}) 
        receive an operation to execute
        check if it is causally ready
        if not delay it
        else execute it
        if executed check the delayed buffer to check for operation that now can be operated (and so on until no operation is executable)
        ---
        The workflow is receive->apply->execute
        """
    
        if not isinstance(t_op, Operation):
            try:
                assert len(args) == 2
                t_op = Operation(t_op, args[0], args[1])
                for k in kw:
                    t_op[k] = kw[k]
            except:
                raise "Error on receive_operation arguments (%s, %s, %s)"%(t_op, args, kw)
                
        # receive an operation to execute
        if dbg >=1:
            print "Site %s;%s; '%s'; receiving %s"%(self.site_index, self.state_vector, self.get_text(), t_op)
    
        

        if is_causally_ready(t_op, self): 		# check if it is causally ready
            self.apply(t_op) # execute it (apply to local buffer)
                
            # if executed check the delayed buffer to check for operation that now can be operated
            # (and so on until no operation is executable)			
            
            while 1: # uhhh, dangerous
                for tt_op in self.delayed_operations:
                    if is_causally_ready(tt_op, self): 
                        self.apply(tt_op) 
                        self.delayed_operations.remove(tt_op)
                        break # break the 'for'; go back to 'while 1'
                break # end of while 1
    
        else: # if not delay it
            self.delayed_operations.append(t_op)
        
        if dbg >=1:
            print "Site %s; HB %s"%(self.site_index, self.HB)
            print "Site %s;%s; '%s'; delayed_ops: %s\n"%(self.site_index, self.state_vector, self.get_text(), self.delayed_operations)
    
                
        return
    
    receive_op = receive_operation # alias
        
    def apply(self, Onew):
        """
        Algorithm 3: The undo/transform-do/transform-redo scheme (sun98generic)
        
        Given a new causally-ready operation Onew , and HB = [EO1,..., EOm,..., EOn ], the following steps are executed:
        
        1. Undo operations in HB from right to left until an operation EOm is found such that EOm => Onew .
        2. Transform Onew into EOnew by applying the GOT control scheme. Then, do EOnew .
        3. Transform each operation EOm+i in HB[m+1,n] into the new execution form EO'm+i as follows:
            - EO'm+1 := IT (EOm+1, EOnew ).
            - For 2 <= i <= (n - m),
                (1) TO := LET (EOm+i, reverse(HB[m+1,m+i - 1]) );
                (2) EO'm+i := LIT (TO, [EOnew, EO'm+1,..., EO'm+i-1 ]).
            Then, redo EO'm+1, EO'm+2, ..., EO'n , sequentially.
        
        After the execution of the above steps, the contents of the history buffer becomes: HB = [EO1,..., EOm, EOnew, EO'm+1,..., EO'n ].
        ---
        This function manage the History Buffer and update the State Vector Table.
        """
            
        assert T(Onew) in ["Insert", "Delete"], "Invalid operation request."
        
        if dbg >=1:
            print "Site %s;%s; '%s'; applying %s"%(self.site_index, self.state_vector, self.get_text(), Onew)
    
    
        HB = self.HB
    
        # 1.
        m = 0 # manage the case HB == []
        undoed = []
        for m in xrange(len(HB) -1, 0 -1, -1):	 # from right to left
            EOm = HB[m]
            #print "check_total_ordering(%s, %s) => %i"%(EOm, Onew, check_total_ordering(EOm, Onew)) # just for debugging
            if not check_total_ordering(EOm, Onew):
                self.undo(EOm)
                # operations do should not be erased from HB, because they will later be transformed !
                undoed.append(EOm)
            else:
                break
            
        if HB and len(undoed) == len(HB):
            if dbg>=2:
                print "No previous op found !"
            m = -1 # to indicate that no previous op was found
    
        # 2.
        EOnew = GOT( Onew, HB[:m+1]) # pass Onew and HB = [EO1, EO2, ..., EOm ]
        self.execute(EOnew)
        # EOnew will be inserted after step 3 to follow better the paper notation.
        if dbg>=2:
            print "m %i; [EO1, ..., EOm ] %s; HB[m+1:] %s"%(m,  HB[:m+1],  HB[m+1:])
    
        
        # 3.
        if undoed: # if there was an undo, then redo
            if dbg>=1:
                print "Site %s; '%s'; undoed %s; executed %s;"%(self.site_index, self.get_text(), undoed, EOnew) # just for debugging
            EOoL = [] # EO'm+1 List
    
            EOoL.append( IT( HB[m+1], EOnew ) ) 
            for i in xrange(1, len(undoed)):  # python indexes start from 'zero' (in the paper they start from 'one')
                TO = LET( HB[m+1+i], reverse(HB[m+1: m+i +1])) # paper [m+1,m+i - 1] -> python [m+1:m+i +1]
                EOoL.append( LIT( TO, [EOnew] + EOoL) )
    
            #print "m: %i; len(EOoL) %i;EOoL %s"%(m, len(EOoL), EOoL) # just for debugging
            for i in xrange(len(EOoL)):			
                t_op = EOoL[i]
                self.execute(t_op)
                HB[m+1+i] = t_op # python indexes start from 'zero'
    
    
        # After the execution of the above steps [...] HB = [EO1,..., EOm, EOnew, EO'm+1,..., EO'n ].
        HB.insert(m + 1, EOnew) # insert into the HB, just after EOm
            
            
        # Update local State vector
        t_index = Onew["source_site"]
        assert t_index < len(self.state_vector), "Received an operation from a source_site outside the state_vector range"
        self.state_vector[t_index] += 1
        
        # Update the State Vector Table (what we know about the status of each site, including ourself)
        self.state_vector_table[EOnew["source_site"]] = list(EOnew["timestamp"]) # update state_vector_table (via a list copy)
    
        if (len(HB) % 10) == 0: # call the garbage collector (over a dummy periodic condition)
            self.collect_garbage()
    
        return

    
    def execute(self, EO, splitted_part=0):
        """
        Modify the text buffer.
        The lost information is stored into the operators for future undos.
        """
        
        if EO.get("is_splitted"):
            self.execute(EO["splitted_head"], splitted_part=1)
            self.execute(EO["splitted_tail"], splitted_part=1)
            return
            
        startpos = P(EO)
        data     = EO["data"]
        
        if T(EO) == "Insert":
            self.insert_text(startpos, data, op=EO)
            
        elif T(EO) == "Delete":
            self.delete_text(startpos, data, op=EO)
        else:
            raise " Tried to execute an Unmanaged Operation type"
            
        return
        
    redo = execute # alias

    def insert_text(self, startpos, data, op=None):
        """
        the op argument is used to obtain extra information in some specific posible implementations
        """
            
        self.text_buffer = self.text_buffer[:startpos] + data + self.text_buffer[startpos:]
        
        return
    
    def delete_text(self, startpos, length, op=None):
        """
        the op argument is used to obtain extra information in some specific posible implementations
        It is necessary to store there some undo information.
        """
        
        t_text = self.text_buffer
        op["deleted_text"] = t_text[startpos:(startpos+length)]
        self.text_buffer = ''.join(t_text[:startpos] + t_text[(startpos+length):])	
            
        return

    def undo(self, EO):
        """
        Undo an operation. Return the text to his previous state.
        The undo operation supose that EO is the last operation executed over the buffer.
        """
        
        if EO.get("is_splitted"):
            self.undo(EO["splitted_head"])
            self.undo(EO["splitted_tail"])
            return
    
        if T(EO) == "Delete":
            assert EO.has_key("deleted_text"), "Undoable operation (no undo info stored)"
            self.execute( op("Insert", P(EO), EO["deleted_text"]) ) # create the undo operation and execute it
            
        elif T(EO) == "Insert":
            self.execute( op("Delete", P(EO), len(S(EO)) ) ) # create the undo operation and execute it
            
        else:
            raise "Trying to undo an Unmanaged Operation."
        
        
        return
    
    
    def collect_garbage(self):
        """
        Algorithm 4. The garbage collection procedure. sun98achieving (page 18, 19, 20).
        Scan HB from left to right. Let EO be the current operation under inspection.
        Suppose that EO was generated at site i and timestamped by SVEO.
            (1) If SVEO [i] <= MSVk[i], then EO is removed from HB and continue scanning.
            (2) Otherwise stop scanning and return.
            
        (The garbage collection procedure can be invoked periodically, or after processing each remote operation/message, or when the number of buffered operations in HB goes beyond a preset threshold value.)
        """
                
        #dbg = 1 # just for debugging
            
        # reference asignations (local aliases)
        HB  = self.HB 
        SVT = self.state_vector_table
        MSV = self.minimum_state_vector
    
        if dbg>=1:
            print "Site %s; before garbage collector; HB %s"%(self.site_index, map(lambda x: "{from S%i%s}"%(x["source_site"], x["timestamp"]) , HB))
        
        # compute the MSV
        for i in xrange(len(MSV)):
            MSV[i] = min( [ sv[i] for sv in SVT ] )
        
        if dbg >=1:
            print "Site %s; garbage collector; MSV %s; SVT %s;"%(self.site_index, MSV, SVT)
            
        # collect the garbage
        deleted_operations_list = []
        for EO in list(HB): # iterate over a copy of HB (to be able to mutate HB will iterating over it)
            i    = EO["source_site"]
            SVEO = EO["timestamp"]
    
            if dbg>=1:
                print "Site %s; garbage collector; EO %s; i %i; %s <=? %s"%(self.site_index, EO, i,  SVEO[i], MSV[i])
            
            condition = SVEO[i] <= MSV[i]
                
            if condition:
                deleted_operations_list.append(Operation(**EO)) # append to the list a copy of the operation
                HB.remove(EO) 
                if dbg>=1:
                    print "Site %s; garbage collector; removing %s"%(self.site_index, EO)
    
            else:
                break # stop scanning HB
                
        if dbg>=1:
            print "Site %s; after garbage collector; HB %s"%(self.site_index, map(lambda x: "{from S%i%s}"%(x["source_site"], x["timestamp"]) , HB))
            
        return deleted_operations_list

    
    def update_SVT(self, site_index, state_vector):
        """
        update_StateVectorTable
        
        sun98achievings.pdf, page 19 paragraph 2.
        If one site happens to be silent for an unusually long period of time, other sites will not know what its state is [a 'mostly observer' site]. Therefore, it is required for a site to broadcast a short state message containing its state vector when it has not generated an operation for a certain period of time and/or after executing a certain number of remote operations. Upon receiving a state message from a remote site r, site k simply updates its rth statve vecor in SVTk withe the piggybacked state vector.
        ---
        This function is used as a remote call to broadcast the state message.
        """
        
        self.state_vector_table[site_index] = state_vector
        
        return
    
    def generate_operation(self, type, pos, data, **kws):
        """
        The site generate an operation, and apply it locally.
        """
        
        t_SV = list(self.state_vector) # copy the list
        t_SV[self.site_index] += 1
        
        t_op = Operation(type, pos, data, t_SV, self.site_index)
        
        for k in kws.keys():
            t_op[k] = kws[k]
            
        if dbg>=1:
            print "Site %s; generating %s"%(self.site_index, t_op)
        
        self.receive_op(t_op)
        
        return t_op
    
    def gen_op(self, type, pos, data, **kws):
        """
        Alias of generate_operation.
        """
        return self.generate_operation(type, pos, data, **kws)
        
        
    def gen_Op(self, type, data, pos, **kws):
        """
        Alias with another parameters order.
        """
        
        return self.gen_op(type, pos, data, **kws)
    

# Function defined over the operation that return boolean values

def is_causally_ready(t_O, t_site):
    """
    Definition 5: Conditions for executing remote operations

    Let O be an operation generated at site s and timestamped by SVo . O is causally-ready for execution at site d (d != s) with a state vector SVd only if the following conditions are satisfied:
        1. SVo [s] = SVd [s] + 1, and
        2. SVo [i] <= SVd [i], for all i in {0,1, ..., N - 1} and i != s.
    """
    
    SVd = t_site.state_vector
    SVo = t_O["timestamp"]
    s   = t_O["source_site"]
    
    assert len(SVd) == len(SVo), "State vectors are not comparable (len(SVd) == %i, len(SVo) == %i; SVd: local site state_vector %s, SVo: operation timestamp %s)"%(len(SVd), len(SVo), SVd, t_O)
      
    assert len(SVd) == len(SVo), "State vectors are not comparable (len(SVd) == %i, len(SVo) == %i)"%(len(SVd), len(SVo)) 
    assert type(s) is int, "The operation has no source site (%s)"%(t_O)
    
    # 1.
    condition1 = ( SVo[s] == SVd[s] + 1 )
    
    #2.
    condition2 = 1
    for i in xrange(len(SVd)):
        if i == s: continue
        condition2 = condition2 and (SVo[i] <= SVd[i])
    
    
    return condition1 and condition2

def check_total_ordering(Oa, Ob):
    """
    Check if Oa => Ob.
    Definition 6: Total ordering relation "=>"
    
    Given two operations Oa and Ob, generated at sites i and j and timestamped by SVOa and SVOb, respectively, then Oa => O b, iff:
        1. sum(SVOa) < sum(SVOb), or
        2. i < j when sum(SVOa) = sum(SVOb),
    
    where sum(SV) = $\sum_{i=0}^{N-1} SV[i]$.	
    """
    
    sum = lambda t_list: reduce(lambda x,y: x+y, t_list)
    
    SVOa = Oa["timestamp"]
    SVOb = Ob["timestamp"]
    
    assert SVOa and SVOb, "can not check operations without timestamp. (Oa:%s; Ob:%s)"%(Oa, Ob)
    
    # 1.
    condition1 = sum(SVOa) < sum(SVOb)
    
    #2.
    i = Oa["source_site"]
    j = Ob["source_site"]
    
    condition2 = (sum(SVOa) == sum(SVOb)) and (i < j)
        
    return condition1 or condition2
# Definition 1: Causal ordering relation "->"
# 
# Given two operations Oa and Ob , generated at sites i and j, then Oa -> Ob , 
# iff:
#     1. i = j and the generation of Oa happened before the generation of Ob , 
# or
#     2. i != j and the execution of Oa at site j happened before the 
# generation of Ob , or
#     3. there exists an operation Ox, such that Oa -> Ox and Ox -> Ob.
# 
# Definition 2: Dependent and independent operations
# 
# Given any two operations Oa and Ob.
#     1. Ob is said to be dependent on Oa iff Oa -> Ob.
#     2. Oa and Ob are said to be independent (or concurrent) iff neither Oa 
# -> Ob , nor Ob -> Oa , which is expressed as Oa || Ob.
# 
# (nor == not or; 0,0 => 1 , 0 else)
# 

def are_dependent(Oa,Ob):
    """
    Implement a less than strict check. Will return true if (Oa->Ob) or if there is a Ox such as (Oa->Ox and Ox->Ob)
    
    After reading in detail the papers I propose:
    Oa -> Ob iff :
        if i==j: return SVoa[i] < SVob[i]
        else:    return SVoa[i] <= SVob[i]
    """
    
    i = Oa["source_site"]
    j = Ob["source_site"]
    
    
    if i == j:
        return Oa["timestamp"][i] <  Ob["timestamp"][i]
    else:
        return Oa["timestamp"][i] <= Ob["timestamp"][i]
    
    return
    

def are_concurrent(Oa,Ob):
    """
    Check if both operations are independent (or concurrent)
    
    return Oa->Ob nor Ob->Oa
    (nor == not or; 0,0 => 1 , 0 else)
    """	
    return not (are_dependent(Oa,Ob) or are_dependent(Ob,Oa) )
    
    
are_independent = are_concurrent # just an alias

def GOT( Onew, HB):
    """ 
    GOT: Generic Operation Transform
    Algorithm 2: The GOT control scheme (sun98generic)

    Given a new causally-ready operation Onew , and HB = [EO1 , EO2, ..., EOm ]. The following steps are executed to obtain EOnew :
    
    1. Scanning the HB from left to right to find the first operation EOk such that EOk || Onew (EOk and Onew are concurrent (or independent)). If no such an operation EOk is found, then EOnew := Onew.
    
    2. Otherwise, search the range of HB[k+1,m] to find all operations which are causally preceding Onew, and let EOL denote these operations. If EOL = [ ], then EOnew := LIT (Onew , HB[k,m]).
    
    3. Otherwise, suppose EOL = [EOc1, ..., EOcr ], the following steps are executed:
        (a) Get EOL' = [EO'c1, ..., EO'cr ] as follows:
            i. EO'c1 := LET (EOc1, reverse(HB[k, c1 - 1]) ):
            ii. For 2 <= i <= r,
                TO := LET (EOci , reverse(HB[k, ci - 1]) );
                EO'ci := LIT (TO, [EO'c1, ..., EO'ci-1]).
        (b) O'new := LET (Onew, reverse(EOL') ).
        (c) EOnew := LIT (O'new, HB[k,m]).
    """
    
    EOnew = Onew # the default result
    
    for k in xrange(len(HB)):
        EOk = HB[k]
        if are_concurrent(EOk, Onew): 
            EOL = HB[k+1:]; c1 = k+1 
            if EOL == []:
                EOnew = LIT(Onew, HB[k:])
            else:
                # (a) i.
                r = len(EOL) 
                
                EOLl = range(r) # EOLl <=> EOL'
                #print "GOT (a) i.; r %s; (k,c1 - 1) %s; len(HB) %s"%(r, (k,c1 - 1), len(HB)) # just for debugging
                
                EOLl[0] = LET(EOL[0], reverse(HB[k:c1 - 1 +1])) # +1 because in paper notation ranges are incluse, incluse ('[]'); while python they are incluse, exclusive ('[)')
                
                # (a) ii.
                for i in xrange(1,r):
                    TO = LET(EOL[i], reverse(HB[k: c1 + i - 1 + 1]))
                    EOLl[i] = LIT(TO, EOLl[1:i-1+1])
                
                # (b)
                Oonew = LET(Onew, reverse(EOLl))
                
                # (c)
                EOnew = LIT(Oonew, HB[k:])
            
    return EOnew

def LIT(O, OL):
    """
    Inclusion transform over a list
    """
    if OL==[]:
        Oo = O
    else:
        Oo = LIT(IT(O, OL[0]), OL[1:])
    
    return Oo
    
def LET(O, OL):
    """
    Exclusion transform over a list
    """
    if OL==[]:
        Oo = O
    else:
        Oo = LET(ET(O, OL[0]), OL[1:])
    
    return Oo
    

def reverse(in_list):
    """
    Helper function used to have a compact notation.
    """
    
    t_list = list(in_list) # create a copy
    t_list.reverse() # in place operator
    
    return t_list


def IT (Oa, Ob):
    """
    Inclusion Transform.
    Return a transformed Oa, named Ooa, such that the impact of the independent operation Ob (against Oa) is efectively included into Oa.
    Also define the timestamp of the virtual operation.
    """
    
    if Check_RA(Oa):
         #print "Check_BO(\n\t%s, \n\t%s \n)\t\t=> %s"%(Oa, Ob, Check_BO(Oa, Ob)) # just for debugging
         if Check_BO(Oa, Ob):
              Ooa = Convert_AA(Oa, Ob)
         else:
              Ooa = Oa 
    elif T(Oa) == "Insert" and T(Ob) == "Insert":
         Ooa = IT_II(Oa, Ob)
    elif T(Oa) == "Insert" and T(Ob) == "Delete":
         Ooa = IT_ID(Oa, Ob)
    elif T(Oa) == "Delete" and T(Ob) == "Insert":
         Ooa = IT_DI(Oa, Ob)
    else: # if T(Oa) == "Delete" and T(Ob) == "Delete"
         Ooa = IT_DD(Oa, Ob)
         
    
    Ooa["source_site"] = Oa["source_site"]
    Ooa["timestamp"]   = list(Oa["timestamp"]) # copy
    
    if dbg>=2:	
        print "IT(\n\t%s, \n\t%s\n)\t\t=> %s;"%(Oa, Ob,Ooa) # just for debugging
        
    return Ooa


def IT_II(Oa, Ob):

    if P (Oa) < P (Ob):
        Ooa = Oa
    else:
        Ooa = Op( "Insert", S(Oa), P(Oa) + L(Ob) )
        
    return Ooa


def IT_ID(Oa, Ob):

    if P(Oa) <= P(Ob):
        Ooa = Oa 
    elif P(Oa) > ( P(Ob) + L(Ob) ):
        Ooa = Op( "Insert",  S(Oa), P(Oa) - L(Ob) )
    else:
        Ooa = Op( "Insert",  S(Oa), P(Ob) )
        
        Save_LI(Ooa, Oa, Ob )
        
    return Ooa

def IT_DI(Oa, Ob):

    if P(Ob) >= (P(Oa) + L(Oa)):
        Ooa = Oa 
    elif P(Oa) >= P(Ob):
        Ooa = Op( "Delete",  L(Oa), P(Oa) + L(Ob) )
    else: 
        Ooa = Splitted( 
                        Op( "Delete", P(Ob) - P(Oa)          , P(Oa)         ),
                        Op( "Delete", L(Oa) - (P(Ob) - P(Oa)), P(Ob) + L(Ob) ) )
    return Ooa

def IT_DD(Oa, Ob):

    if P (Ob) >= (P(Oa) + L(Oa)):
        Ooa = Oa 
    elif P(Oa) >= (P(Ob) + L(Ob)):
        Ooa = Op( "Delete", L(Oa), P(Oa) - L(Ob) )
    else:
        if P(Ob) >= P(Oa) and (P(Oa) + L(Oa)) <= (P(Ob) + L(Ob)):
            Ooa = Op( "Delete", 0, P(Oa) )
        elif P(Ob) <= P(Oa) and (P(Oa) + L(Oa)) > (P(Ob) + L(Ob)):
            Ooa = Op( "Delete", P(Oa) + L(Oa) - (P(Ob)+ L(Ob)), P (Ob) )
        elif P(Ob) > P(Oa) and (P(Ob) + L(Ob)) >= (P(Oa) + L(Oa)):
            Ooa = Op( "Delete", P(Ob) - P (Oa), P(Oa) )
        else:
            Ooa = Op( "Delete", L(Oa) - L(Ob), P(Oa) )
            
        Save_LI(Ooa, Oa, Ob) # this is in the first 'else' # this is a guess
            
    return Ooa



def ET(Oa, Ob):
    """
    Exclusion Transform.
    Transform Oa against its causally preceding operation Ob to produce Ooa in such a way that Ob's impact on Oa is excluded.
    Also define the timestamp of the virtual operation.
    """
    
    if Check_RA(Oa):
        Ooa = Oa
    elif T(Oa) == "Insert" and T(Ob) == "Insert":
        Ooa = ET_II(Oa, Ob)
    elif T(Oa) == "Insert" and T(Ob) == "Delete":
        Ooa = ET_ID(Oa, Ob)
    elif T(Oa) == "Delete" and T(Ob) == "Insert":
        Ooa = ET_DI(Oa, Ob)
    else: # if T(Oa) == "Delete" and T(Ob) == "Delete":
        Ooa = ET_DD(Oa, Ob)
        
    
    Ooa["source_site"] = Oa["source_site"]
    Ooa["timestamp"]   = list(Oa["timestamp"]) # copy
    
    if dbg>=2:		
        print "ET(\n\t%s, \n\t%s\n)\t\t=> %s;"%(Oa, Ob,Ooa) # just for debugging
    
    return Ooa

def ET_II(Oa, Ob):

    if P(Oa) <= P(Ob) :
        Ooa = Oa
    elif P(Oa) >= (P(Ob) + L(Ob)):
        Ooa = Op( "Insert",  S(Oa), P(Oa) - L(Ob) )
    else:
        Ooa = Op( "Insert",  S(Oa), P(Oa) - P(Ob) )
        Save_RA(Ooa, Ob)
        
    return Ooa

def ET_ID(Oa, Ob):

    if Check_LI(Oa, Ob):
        Ooa = Recover_LI(Oa)
    elif P(Oa) <= P(Ob):
        Ooa= Oa
    else:
        Ooa= Op( "Insert", S(Oa), P(Oa) + L(Ob) )

    return Ooa
    
    
def ET_DI(Oa, Ob):

    if(P(Oa) + L(Oa)) <= P(Ob):
        Ooa = Oa
    elif P(Oa) >= (P(Ob) + L(Ob)):
        Ooa = Op( "Delete", L(Oa), P(Oa) - L(Ob) )
    else:
        if P(Ob) <= P(Oa) and (P(Oa) + L(Oa))  <= (P(Ob) + L(Ob)):
            Ooa = Op( "Delete", L(Oa), P(Oa) - P(Ob) )
        elif P(Ob) <= P(Oa) and ((P(Oa) + L(Oa)) > (P(Ob) + L(Ob))):
            Ooa = Splitted ( Op( "Delete",  P(Ob) + L(Ob) - P(Oa)         ,(P(Oa) - P(Ob)) ),
                                         Op( "Delete", (P(Oa) + L(Oa))-(P(Ob) + L(Ob)), P(Ob)          ) )
        elif P(Oa) < P(Ob) and ((P(Ob) + L(Ob)) <= (P(Oa) + L(Oa))):
            Ooa = Splitted( Op( "Delete", L(Ob)        , 0     ), 
                            Op( "Delete", L(Oa) - L(Ob), P(Oa) ) )
        else:
            Ooa = Splitted( Op( "Delete", P(Oa) + L(Oa) - P(Ob), 0     ), 
                            Op( "Delete", P(Ob) - P(Oa)        , P(Oa) ) )
        
        Save_RA(Ooa, Ob) # this is in the first 'else' # this is a guess
            
    return Ooa



def ET_DD(Oa, Ob):

    if Check_LI(Oa, Ob):
        Ooa = Recover_LI(Oa)
    elif P(Ob) >= (P(Oa) + L(Oa)):
        Ooa = Oa
    elif P(Oa) >= P(Ob) :
        Ooa = Op( "Delete", L(Oa), P(Oa) + L(Ob))
    else :
        Ooa = Splitted( Op( "Delete", P(Ob) - P(Oa)         , P(Oa)         ),
                        Op( "Delete", L(Oa) -(P(Ob) - P(Oa)), P(Ob) + L(Ob) ) )
    return Ooa

class Operation(dict):
    """
    simple object that encapsulate the information and methods related to the operations.
    it is a dictionary with extra methods.
    """
    
    def __init__(self, _type=None, pos=None, data=None, timestamp=None, source_site=None, **kws):
        
        d = self
        
        d["type"] = str(_type)
        d["pos"]  = pos
        assert type(data) in [unicode, int], "Data has to be unicode or integer."
        d["data"] = data # text or len
            
        d["timestamp"]   = timestamp
        d["source_site"] = source_site
        
        for k in kws.keys():
            d[k] = kws[k]
                    

    def __eq__(self, other): 
        """
        The papers do not explain how to manage the TimeStamp of the operations during transforms and do not explain which operations are considered to be equivalents.
        Studying in detail the sequence of transformations that the example generate:
            LIT(ET(O4, ET(EO2, EO1)), [EO1, EO2])
        I deduce that the first approach of using Operations class instances is wrong. Doing that Transformation mutate the operators passed is wrong too.
        If during transform the timestamp are preserved then timestamp and source_site are the unique identifiers of a operation. Then IT(EO, EOx) == ET(EO, EOx) == EO; this is not intuitive but it works.
        ----
        x==y calls x.__eq__(y)
        """
        
        assert isinstance(other, Operation), "Only operations instances can be compared (was comparing %s with %s)"%(self, other)
        
        return (self["source_site"] == other["source_site"]) and (self["timestamp"] == other["timestamp"])

    def __repr__(self):
        """
        """
        return "%s"%(str(self))
        
    def __str__(self):
        """
        """
        
        t_keys = filter(lambda x: x not in ["type", "pos", "data", "source_site", "timestamp"], self.keys())
        
        t_string = ""
        
        if self.has_key("source_site") and self.get("timestamp") :
            t_string += "from S%s%s "%(self["source_site"], self["timestamp"])
            
        if type(self["data"]) is unicode:
            t_data = "'%s'"%(self["data"].encode("utf-8", "replace")) # utf-8 ? are you crazy hardcoding this ?
        else:
            t_data = self["data"]
            
        t_string += "%s@%s:%s"%(self["type"], self["pos"], t_data)
         
        for k in t_keys:
            t_data = self[k]
            if type(t_data) is unicode:
                t_data = t_data.encode("utf-8", "replace") # utf-8 ? are you crazy hardcoding this ?
            t_string += ", %s:'%s'"%(k, t_data)
            
        return "{%s}"% t_string
        
    def set_timestamp(self, t_SV):
        """
        Save a state vector as the timestamp.
        """
        
        self["timestamp"] = t_SV
        return
        
    def get_timestamp(self):
        """
        return the state vector used as the timestamp.
        """
        return self.get("timestamp")
    
        
# end of class Operation

# Dummy function to shortcut the code.

def Op(type, data, pos): # this one has a diferent parameters order
    """
    Return an instance of the Operation Object.
    """
    return Operation(type, pos, data)
    
def op(type, pos, data):
    """
    Return an instance of the Operation Object.
    """
    return Operation(type, pos, data)


# Simple function used in the algorithm (enhance readability and paper 
# notation matching)

def T(O):
    """
    Return the type of operation ("Insert" or "Delete")
    """
    return O["type"]
        
    
def P(O):
    """
    Return the position where the operation is executed.
    """
    return O["pos"]


def L(O):
    """
    Return length of the deletion operation.
    For safness if the operation is no a deletion it return the length of the inserted text. (stricly it should raise an error...)
    """
    
    data = O["data"] # speed-up
    assert data != None, "Operation has no data! (%s in %s)"%(data, O)
    
    if type(data) is int:
        return data
    else:
        return len(data)


def S(O):
    """
    Return the string that the insert operation is trying to insert.
    """
    
    assert type(O["data"]) is unicode, "S(O) is only valid for Insertion operation."
        
    return O["data"]
    

def Splitted(O1, O2):
    """
    Return an operation that is splitted. (this should considered in function 'execute' and 'undo')
    """
    
    assert T(O1) == T(O2), "Splitted operations are of different types, this is not sane."
    assert not (O1.get("is_splitted") or O1.get("is_splitted") ), "Recursive splitted operation not yet supported" 
        
    Oo = Operation(T(O1))
    Oo["is_splitted"] = 1
    Oo["splitted_head"] = O1
    Oo["splitted_tail"] = O2
    
    
    if P(O1) < P(O2):
        Oo["pos"] =  P(O1)
        Oo["data"] =  ( P(O2) + L(O2) ) - P(O1)
    elif P(O1) > P(O2):
        Oo["pos"] = P(O2)
        Oo["data"] = ( P(O1) + L(O1) ) - P(O2)
    else:
        raise "Weird split P(O1) == P(O2) (%s,%s)"%(O1, O2)
        
    return Oo



# LI refers to "Lost Information".
        
    
def Check_LI(Oa, Ob):
    """
    Ob was involved in a information lossing operation that afected Oa ?
    """
    
    return 	Oa.get("LI_base_op") == Ob
    
    
def Save_LI(Oaa, Oa, Ob):
    """
    Store in Oaa the information related to the paremeters of Oa and the reference to Ob.
    
    One operation can only store one and only one information lose.
    """
    
    copy_Oa = op(Oa["type"], Oa["pos"], Oa["data"] )
    
    Oaa["lost_information"]     = copy_Oa
    Oaa["LI_base_op"]      = Ob
    
    return


def Recover_LI(Oa):
    """
    >>>>>>>>>>>>>>>>>DID NOT FOUND SPECIFICATION (this could cause horrible errors)<<<<<<<<<<<<<<<<<<
    """
    
    return 	Oa["lost_information"]
    
def Check_RA(Oa):
    """
    Is Oa relatively addressed ?
    """
    
    return Oa.has_key("relatively_addressed") and Oa["relatively_addressed"]
    
    
def Save_RA(Oa, Ob):
    """
    Stores the information to mark Oa as having a relative address to over Ob.
    """
    
    #print "called Save_RA(%s, %s)"%(Oa, Ob) # just for debugging
    
    Oa["relatively_addressed"] = 1
    Oa["base_operation"] = Ob
    Oa["delta_pos"] = P(Oa) - P(Ob) # Abis = P(Obbis) + A.delta_pos
    
    return
    
def Check_BO(Oa, Ob):
    """
    Ob is the base operation of Oa ? (in the relative address context)
    """
    
    #Ox = Oa.get("base_operation")
    #return (Ox["source_site"] == Ob["source_site"]) and (Ox["timestamp"] == Ob["timestamp"])
    
    return Ob == Oa.get("base_operation") # look at the definition of __eq__ in the Operation class
    

def Convert_AA(Oa, Ob):
    """
    Obtain Oaa, which is an absolute address operation based on Oa, over the relative position of Ob.
    """
    
    assert Check_BO(Oa,Ob), "Convert_AA: Ob is not the base_operation of Oa"
    
    #print "called Convert_AA(%s, %s)"%(Oa, Ob) # just for debugging
    
    Oaa = op( Oa["type"],	Oa["delta_pos"] + Ob["pos"], Oa["data"] )
    
    return Oaa

