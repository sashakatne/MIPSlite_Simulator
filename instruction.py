class Instruction(object):
    """
    Represents a CPU instruction with methods to decode it from hexadecimal format.

    Attributes:
        hex_instr (str): Hexadecimal string representing the instruction.
        opcode_dict (dict): Maps binary opcode strings to their mnemonic.
        r_type (list): List of mnemonics that are of R-type format.
        hex (str): Hexadecimal representation of the instruction.
        opcode (str): Mnemonic of the opcode.
        type (str): Type of the instruction ('R' for register, 'I' for immediate).
        rs, rt, rd (int): Source, target, and destination register numbers.
        reg_rs, reg_rt, reg_rd (int): Actual register numbers after decoding.
        imm (int): Immediate value for I-type instructions.
        x_addr (int): Address for branch instructions.
        frwd_rs, frwd_rt (bool): Flags indicating if forwarding is applied to rs and rt registers.
    """

    def __init__(self, hex_instr):
        """
        Initializes a new Instruction instance.

        Args:
            hex_instr (str): Hexadecimal string of the instruction.
        """
        self.opcode_dict = {
            '000000': 'Add', '000001': 'Addi', '000010': 'Sub', '000011': 'Subi',
            '000100': 'Mul', '000101': 'Muli', '000110': 'Or', '000111': 'Ori',
            '001000': 'And', '001001': 'Andi', '001010': 'Xor', '001011': 'Xori',
            '001100': 'Ldw', '001101': 'Stw', '001110': 'Bz', '001111': 'Beq',
            '010000': 'Jr', '010001': 'Halt'
        }
        self.r_type = ['Add', 'Sub', 'Mul', 'Or', 'And', 'Xor']
        self.hex = hex_instr
        self.opcode = None
        self.type = None
        self.rs = self.rt = self.rd = 0
        self.reg_rs = self.reg_rt = self.reg_rd = None
        self.imm = self.x_addr = None
        self.frwd_rs = self.frwd_rt = False

    def __repr__(self):
        """
        Returns a string representation of the instruction.
        """
        return f'Instr({self.hex},{self.opcode},R{self.reg_rs}:{self.rs},R{self.reg_rt}:{self.rt},R{self.reg_rd}:{self.rd},imm:{self.imm},addr:{self.x_addr},rs_f:{self.frwd_rs},rt_f:{self.frwd_rt})'

    def decode(self):
        """
        Decodes the instruction from its hexadecimal representation.
        """
        if self.hex is None:
            return
        # Convert hex to a 32-bit binary string
        bin_inst = '{0:032b}'.format(int.from_bytes(bytes.fromhex(self.hex), byteorder='big', signed=True))
        opcode = bin_inst[:6]
        if opcode in self.opcode_dict:
            self.opcode = self.opcode_dict[opcode]
            if self.opcode in self.r_type:  # Decode R-type instruction
                self.type = 'R'
                self.reg_rs = int(bin_inst[6:11], 2)
                self.reg_rt = int(bin_inst[11:16], 2)
                self.reg_rd = int(bin_inst[16:21], 2)
            else:  # Decode I-type instruction
                self.type = 'I'
                if self.opcode == 'Halt':
                    return
                self.reg_rs = int(bin_inst[6:11], 2)
                if self.opcode == 'Jr':
                    return
                if self.opcode == 'Bz':
                    self.x_addr = int('{0:016b}'.format(int.from_bytes(bytes.fromhex(self.hex[-4:]), byteorder='big', signed=True)), 2)
                    return
                self.reg_rt = int(bin_inst[11:16], 2)
                self.imm = int('{0:016b}'.format(int.from_bytes(bytes.fromhex(self.hex[-4:]), byteorder='big', signed=True)), 2)
