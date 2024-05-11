import os

class Memory(object):
    '''
    A class to simulate memory operations based on a trace file.
    It supports reading and writing both words and bytes to memory locations.
    '''
    def __init__(self, path):
        '''
        Initializes the memory with the contents of a trace file.
        
        :param path: The file path to the trace file.
        '''
        self.mem_trace = dict()
        if os.path.exists(path):
            index = 0
            with open(path, 'r+') as trace:
                lines = trace.readlines()
                for line in lines:
                    # Store each line from the trace file into the memory trace dictionary.
                    # The line's content is stored at 'index', simulating a memory address.
                    self.mem_trace[index] = line.strip('\n')
                    index += 4  # Increment index by 4 for the next memory address.
    
    def read_word(self, index):
        '''
        Reads and returns a word from a specified memory location.
        
        :param index: The memory address to read from.
        :return: The word at the specified memory address.
        '''
        return self.mem_trace[index]
    
    def read_byte(self, index):
        '''
        Reads and returns a single byte from a specified memory location.
        
        :param index: The memory address to read from.
        :return: The byte at the specified memory address.
        '''
        offset = index % 4
        word = self.mem_trace[index - offset]
        # Convert the word from hex to binary, extract the relevant byte, and return it as an integer.
        byte = int('{0:032b}'.format(int.from_bytes(bytes.fromhex(word), byteorder='big', signed=True))[offset*8:offset*8+8])
        return byte
    
    def write_byte(self, index, word):
        '''
        Writes a byte to a specified memory location.
        
        :param index: The memory address to write to.
        :param word: The byte (in hex) to write.
        '''
        offset = index % 4
        current_word = self.mem_trace[index - offset]
        current_word_bin = '{0:032b}'.format(int.from_bytes(bytes.fromhex(current_word), byteorder='big', signed=True))
        new_byte_bin = '{0:08b}'.format(int.from_bytes(bytes.fromhex(word), byteorder='big', signed=True))
        # Replace the relevant byte in the current word with the new byte.
        word_write = current_word_bin[:offset*8] + new_byte_bin + current_word_bin[offset*8+8:]
        self.mem_trace[index - offset] = hex(int(word_write, 2))[2:]
    
    def write_word(self, index, word):
        '''
        Writes a word to a specified memory location.
        
        :param index: The memory address to write to.
        :param word: The word to write.
        '''
        self.mem_trace[index] = word

class registers(object):
    '''
    Simulates a set of 32 registers for a processor.
    '''
    def __init__(self):
        '''
        Initializes 32 registers, setting each to 0.
        '''
        self.regs = dict()
        for index in range(32):
            self.regs[index] = 0  # Initialize all registers to 0.
    
    def read_reg(self, index):
        '''
        Returns the value of a specified register.
        
        :param index: The register number to read from.
        :return: The value of the specified register.
        '''
        return self.regs[index]
    
    def write_reg(self, index, word):
        '''
        Writes a value to a specified register.
        
        :param index: The register number to write to.
        :param word: The value to write to the register.
        '''
        self.regs[index] = word
