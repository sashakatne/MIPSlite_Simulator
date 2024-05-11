import copy
import memory
from instruction import Instruction

class Processor(object):
    '''
    Simulates a 5-stage pipelined MIPS-lite 32 architecture processor. This class allows running a trace of instructions
    and printing processor statistics. It supports instruction forwarding to mitigate data hazards between the EX (Execute)
    and MEM (Memory) stages. 
    
    Attributes:
    - memory_image: An instance of the Memory class containing the instruction trace.
    - forwarding: Enables full-forwarding if set to True. Defaults to False.
    - debug: Enables verbose logging of pipeline stages if set to True. Defaults to False.
    '''
    def __init__(self,memory_image,forwarding=False,debug=False):
        '''
        Instantiate a new processor.
        '''
        self.mem_image = copy.deepcopy(memory_image)
        self.original_mem = memory_image
        self.forwarding = forwarding
        self.debug=debug
        self.frwrd_dict = dict()
        self.regs = memory.registers()
        self.data_list = [0,Instruction(None),Instruction(None),Instruction(None),Instruction(None)]
        self.pc = 0
        self.arith_opcode = ['Add','Addi','Sub','Subi','Mul','Muli']
        self.logic_opcode = ['Or','Ori','And','Andi','Xor','Xori']
        self.ld_opcode = ['Ldw','Stw']
        self.ctrl_opcode = ['Bz','Beq','Jr','Halt']
        self.r_type = ['Add','Sub','Mul','Or','And','Xor']
        self.reg_change={}
        self.ari_count = 0
        self.logic_count = 0
        self.ctrl_count = 0
        self.ld_count = 0
        self.stall_cycle=0
        self.num_instructions = 0
        self.branch_penalties = 0
        self.branches_taken = 0
        self.total_branches = 0
        self.hazards = 0
        self.st_count = []
        self.Halt = False
        self.cycles=0
        
    def run(self,):
        ''' 
        Runs the complete trace of instructions
        '''
        self.cycles = 0
        while self.data_list[4].opcode!='Halt':
            self.Write_back()
            self.Memory_op()
            self.Execute()
            self.Instruction_decode()
            self.Fetch()
            self.data_list[0]=self.pc 
            self.cycles += 1
        self.cycles += 1
        return

    def print_stats(self):
        '''
        Prints execution statistics, including cycle count, instruction counts by type,
        and information on stalls and hazards.
        '''
        print("\nSimulating the MIPS-lite processor with Forwarding: " + str(self.forwarding) + "\n")
        print("*" * 5 + " PC, Memory and Register state " + "*" * 5 + "\n")
        print("Program counter state: ", self.pc)
        self.print_mem()
        self.print_reg()
        print("\n" + "*" * 5 + " Instruction Counts " + "*" * 5 + "\n")
        print("Total Instruction count: ", self.num_instructions)
        print("Arithmetic Instruction count: ", self.ari_count)
        print("Logical Instruction count: ", self.logic_count)
        print("Memory Instruction count: ", self.ld_count)
        print("Control Instruction count: ", self.ctrl_count)
        print("\n" + "*" * 5 + " Timing Simulator " + "*" * 5 + "\n")
        print("Total number of clock cycles: ", self.cycles)
        if not self.forwarding:
            print("Number of average stalls: ", sum(self.st_count) / self.hazards if self.hazards > 0 else 0)
        print("Total stall count: ", sum(self.st_count))
        print("Total number of hazards: ", self.hazards)
        print("\n" + "*" * 5 + " Branching Information " + "*" * 5 + "\n")
        print("Total number of branches: ", self.total_branches)
        print("Total number of branches taken: ", self.branches_taken)
        print("Total branch penalties: ", self.branch_penalties)
        if self.branches_taken > 0:
            print("Average branch penalty: ", (self.branch_penalties / self.branches_taken), " cycles")
        print("\n" + "*" * 5 + " Performance of MIPS-lite " + "*" * 5 + "\n")
        # Calculate and print CPI (Cycles Per Instruction) and IPC (Instructions Per Cycle)
        self.cpi = self.cycles / self.num_instructions if self.num_instructions > 0 else 0
        self.ipc = self.num_instructions / self.cycles if self.cycles > 0 else 0
        print("CPI (Cycles Per Instruction): ", self.cpi)
        print("IPC (Instructions Per Cycle): ", self.ipc)

    def store_stats(self):
        '''
        Stores execution statistics in a dictionary and returns it.
        '''
        stats = {
            "forwarding": self.forwarding,
            "program_counter": self.pc,
            "num_instructions": self.num_instructions,
            "arithmetic_instructions": self.ari_count,
            "logic_instructions": self.logic_count,
            "memory_instructions": self.ld_count,
            "control_instructions": self.ctrl_count,
            "cycles": self.cycles,
            "total_stalls": sum(self.st_count),
            "hazards": self.hazards,
            "total_branches": self.total_branches,
            "branches_taken": self.branches_taken,
            "branch_penalties": self.branch_penalties,
            "average_branch_penalty": self.branch_penalties / self.total_branches if self.total_branches > 0 else 0,
            "cpi": self.cpi,
            "ipc": self.ipc
        }
        if not self.forwarding:
            stats["average_stalls"] = sum(self.st_count) / self.hazards if self.hazards > 0 else 0
        
        return stats

    def print_mem(self):
        '''
        Prints the state of memory locations that have changed during execution, each on a new line.
        '''
        keys = [k for k in self.original_mem.mem_trace if self.mem_image.mem_trace[k] != self.original_mem.mem_trace[k]]
        changed_memory = {k: self.mem_image.mem_trace[k] for k in keys}
        print("\nChanged memory state:")
        for address, value in changed_memory.items():
            print(f"Address {address}: {value}")
    
    def print_reg(self):
        '''
        Prints the current state of the processor's registers in ascending order.
        '''
        print("\nRegister State:")
        for reg in sorted(self.reg_change.keys(), key=lambda x: int(x[1:])):
            print(f"{reg}: {self.reg_change[reg]}")

    def _check_target(self,instr):
        '''
        Checks stalls in the Instruction Decode stage.
        Input: instr: object of class Instruction
        '''
        if instr.opcode=='Halt':
            return
        if self.forwarding and ((instr.type=='R') or (instr.opcode in ['Beq','Stw'])):
            for obj in self.data_list[3:]:
                if obj.type=='I' and obj.opcode!='Ldw':
                    if obj.reg_rt==instr.reg_rs:
                        instr.rs = obj.rt
                        instr.frwd_rs = True
                    elif obj.reg_rt==instr.reg_rt:
                        instr.rt = obj.rt
                        instr.frwd_rt = True
                    elif obj.reg_rt==instr.reg_rs==instr.reg_rt:
                        instr.rs = obj.rt
                        instr.frwd_rs = True
                        instr.rt = obj.rt
                        instr.frwd_rt = True
                elif obj.type=='R':
                    if obj.reg_rd==instr.reg_rs:
                        instr.rs = obj.rd
                        instr.frwd_rs = True
                    elif obj.reg_rd==instr.reg_rt:
                        instr.rt = obj.rd
                        instr.frwd_rt = True
                    elif obj.reg_rd==instr.reg_rs==instr.reg_rt:
                        instr.rs = obj.rd
                        instr.frwd_rs = True
                        instr.rt = obj.rd
                        instr.frwd_rt = True
                elif obj.opcode=='Ldw':
                    if obj.reg_rt==instr.reg_rs:
                        if self.data_list[3:].index(obj)==1:
                            instr.rs = obj.rt
                            instr.frwd_rs = True
                        else:
                            self.stall_cycle = len(self.data_list[3:]) - self.data_list[3:].index(obj)-1
                            return
                    elif obj.reg_rt==instr.reg_rt:
                        if self.data_list[3:].index(obj)==1:
                            instr.rt = obj.rt
                            instr.frwd_rt = True
                        else:
                            self.stall_cycle = len(self.data_list[3:]) - self.data_list[3:].index(obj)-1
                            return
                    elif obj.reg_rt==instr.reg_rs==instr.reg_rt:
                        if self.data_list[3:].index(obj)==1:
                            instr.rs = obj.rt
                            instr.frwd_rs = True
                            instr.rt = obj.rt
                            instr.frwd_rt = True
                        else:
                            self.stall_cycle = len(self.data_list[3:]) - self.data_list[3:].index(obj)-1
                            return
                    
        elif self.forwarding and instr.type=='I':
            for obj in self.data_list[3:]:
                if obj.type=='I'and obj.opcode!='Ldw':
                    if obj.reg_rt==instr.reg_rs:
                        instr.rs = obj.rt
                        instr.frwd_rs =True
                        break
                elif obj.type=='R':
                    if obj.reg_rd==instr.reg_rs:
                        instr.rs = obj.rd
                        instr.frwd_rs =True
                        break
                elif obj.opcode=='Ldw':
                    if obj.reg_rt==instr.reg_rs:
                        if self.data_list[3:].index(obj)==1:
                            instr.rs = obj.rt
                            instr.frwd_rs = True
                        else:
                            self.stall_cycle = len(self.data_list[3:]) - self.data_list[3:].index(obj)-1
                            return
        elif (instr.type=='R') or (instr.opcode in ['Beq','Stw']):
            for obj in self.data_list[3:]:
                if obj.type=='I':
                    if obj.reg_rt in [instr.reg_rs,instr.reg_rt]:
                        self.stall_cycle = len(self.data_list[3:]) - self.data_list[3:].index(obj) 
                        return
                elif obj.type=='R':
                    if obj.reg_rd in [instr.reg_rs,instr.reg_rt]:
                        self.stall_cycle = len(self.data_list[3:]) - self.data_list[3:].index(obj)
                        return
        elif instr.type=='I':
            for obj in self.data_list[3:]:
                if obj.type=='I':
                    if obj.reg_rt==instr.reg_rs:
                        if self.forwarding:
                            instr.rs = obj.rt
                            instr.frwd_rs =True
                            break
                        else:
                            self.stall_cycle = len(self.data_list[3:]) - self.data_list[3:].index(obj) 
                        return
                elif obj.type=='R':
                    if obj.reg_rd==instr.reg_rs:
                        if self.forwarding:
                            instr.rs = obj.rd
                            instr.frwd_rs =True
                            break
                        else:
                            self.stall_cycle = len(self.data_list[3:]) - self.data_list[3:].index(obj)
                        return
        return

    def _getSignedNum(self,num, bitLength):
        '''
        Returns signed number.
        Inputs: num: number
        bitlength: number of bits for signed number
        '''
        mask = (2 ** bitLength) - 1
        if num & (1 << (bitLength - 1)):
            return num | ~mask
        else:
            return num & mask
        
    def Fetch(self,):
        '''
        Instruction Fetch stage of the processor. Fetches address of instruction from the program counter.
        '''
        if self.debug:
            print("In IF stage: ",self.data_list[0])
        if self.Halt:
            return
        if self.data_list[0]==None:
            self.data_list[1] = Instruction(None)
            return
        if self.stall_cycle>0:
            self.stall_cycle = self.stall_cycle - 1
            if self.debug:
                print('stall cycles in IF: ',self.stall_cycle)
            return
        for inst in self.data_list[1:]:
            if (self.data_list[0] == inst.x_addr) and inst.opcode=='Stw':
                if self.forwarding:
                    self.data_list[1] = Instruction(hex(inst.rt)[2:])
                    self.pc +=4
                    return
                else:
                    self.hazards += 1
                    self.stall_cycle = len(self.data_list[1:])-self.data_list[1:].index(inst)
                    self.st_count.append(self.stall_cycle)
        if self.stall_cycle>0:
            if self.debug:
                print('stall cycles in IF: ',self.stall_cycle)
            return
        instr = self.mem_image.read_word(self.data_list[0])
        self.data_list[1] = Instruction(instr)
        self.pc += 4
        return
        
    def Instruction_decode(self,):
        '''
        Instruction Decode stage of the processor. Decodes the instruction from the IF stage.
        '''
        instr = self.data_list[1]
        instr.decode()
        if self.debug:
            print("In ID stage: ",instr)
        if instr.opcode==None:
            self.data_list[2] = instr
            return
        if self.Halt:
            self.data_list[2] = Instruction(None)
            return
        if self.stall_cycle>0:
            if self.debug:
                print('stall cycles in ID: ',self.stall_cycle)
            self.data_list[2] = Instruction(None)
            return
        self._check_target(instr)
        if self.stall_cycle>0:
            if self.debug:
                print('stall cycles in ID: ',self.stall_cycle)
            self.hazards += 1
            self.st_count.append(self.stall_cycle)
            self.data_list[2] = Instruction(None)
            return
        if instr.opcode in self.arith_opcode:
            self.ari_count += 1
        elif instr.opcode in self.logic_opcode:
            self.logic_count += 1
        elif instr.opcode in self.ctrl_opcode:
            self.ctrl_count += 1
        elif instr.opcode in self.ld_opcode:
            self.ld_count += 1
        if instr.opcode=='Halt':
            self.Halt = True
            self.data_list[2] = instr
            return
        if instr.frwd_rs==False:
            instr.rs = self.regs.read_reg(instr.reg_rs) if instr.opcode in self.logic_opcode else self._getSignedNum(self.regs.read_reg(instr.reg_rs),32)        
        if instr.opcode in ['Jr','Bz']:
            self.data_list[2] = instr
            return
        if instr.frwd_rt==False:
            if instr.opcode in self.r_type:
                instr.rt = self._getSignedNum(self.regs.read_reg(instr.reg_rt), 32)
            else:
                if instr.opcode in ['Stw','Beq']:
                    instr.rt = self.regs.read_reg(instr.reg_rt)
        self.data_list[2] = instr
        return

    def Execute(self,):
        '''
        Instruction Execute stage of the processor. It executes the instruction.
        '''
        instr = self.data_list[2]
        if self.debug:
            print("In EX stage: ",instr)
        if instr.opcode==None:
            self.num_instructions = self.num_instructions
            self.data_list[3] = instr
            return
        else:
            self.num_instructions += 1            
        if instr.opcode=='Halt':
            self.data_list[3] = instr
            return
        if self.Halt:
            return
        if instr.opcode in ['Jr', 'Bz', 'Beq']:
            self.total_branches += 1
            branch_taken = False
            if instr.opcode == 'Jr':
                self.pc = instr.rs
                branch_taken = True
            elif instr.opcode == 'Bz' and instr.rs == 0:
                self.pc = self.pc - 8 + 4 * instr.x_addr
                branch_taken = True
            elif instr.opcode == 'Beq' and instr.rs == instr.rt:
                self.pc = self.pc - 8 + 4 * instr.imm
                branch_taken = True

            if branch_taken:
                self.branches_taken += 1
                self.branch_penalties += 2  # Assuming a fixed penalty of 2 cycles for taken branches

            # Clear the pipeline if a branch is taken
            if branch_taken:
                self.data_list[1] = Instruction(None)
                self.data_list[0] = None
        if instr.opcode=='Add':
            instr.rd = self._getSignedNum(instr.rs + instr.rt,32)
        elif instr.opcode=='Addi':
            instr.rt = self._getSignedNum(instr.rs + instr.imm,32)
        elif instr.opcode=='Sub':
            instr.rd = self._getSignedNum(instr.rs - instr.rt,32)
        elif instr.opcode=='Subi':
            instr.rt = self._getSignedNum(instr.rs - instr.imm,32)
        elif instr.opcode=='Mul':
            instr.rd = self._getSignedNum(instr.rs * instr.rt,32)
        elif instr.opcode=='Muli':
            instr.rt = self._getSignedNum(instr.rs * instr.imm,32)
        elif instr.opcode=='Or':
            instr.rd = instr.rs | instr.rt
        elif instr.opcode=='Ori':
            instr.rt = instr.rs | instr.imm
        elif instr.opcode=='And':
            instr.rd = instr.rs & instr.rt
        elif instr.opcode=='Andi':
            instr.rt = instr.rs & instr.imm
        elif instr.opcode=='Xor':
            instr.rd = instr.rs ^ instr.rt
        elif instr.opcode=='Xori':
            instr.rt = instr.rs ^ instr.imm
        elif instr.opcode=='Ldw':
            instr.x_addr = self._getSignedNum(instr.rs + instr.imm,32)
        elif instr.opcode=='Stw':
            instr.x_addr = self._getSignedNum(instr.rs + instr.imm,32)
        self.data_list[3] = instr
        return

    def Memory_op(self,):
        '''
        Memory stage of the processor. It loads or stores data from the memory.
        '''
        instr = self.data_list[3]
        if self.debug:
            print('In Mem stage: ',instr)
        if instr.opcode==None:
            self.data_list[4] = instr
            return
        if instr.opcode=='Ldw':
            addr = instr.x_addr
            instr.rt = int('{0:032b}'.format(int.from_bytes(bytes.fromhex(self.mem_image.read_word(addr)),byteorder='big',signed=True)),2)
        elif instr.opcode=='Stw':
            addr = instr.x_addr
            data = instr.rt
            self.mem_image.write_word(addr,data)           
        self.data_list[4] = instr
        return
        
    def Write_back(self,):
        '''
        Write Back stage of the processor. It writes the generated data back to the registers.
        '''
        instr = self.data_list[4]
        if self.debug:
            print('In WB stage: ',instr)
        if instr.opcode==None:
            pass
            return
        if (instr.opcode in ['Stw','Jr','Halt','Bz','Beq']):
            pass
        else:
            if instr.opcode in self.r_type:
                self.reg_change['R'+str(instr.reg_rd)] = instr.rd
                self.regs.write_reg(instr.reg_rd,instr.rd)
            else:
                self.reg_change['R'+str(instr.reg_rt)] = instr.rt
                self.regs.write_reg(instr.reg_rt,instr.rt)
        return
