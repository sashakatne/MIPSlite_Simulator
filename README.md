# MIPS-lite Simulator

This repository contains a Python-based simulator for a simplified MIPS architecture, referred to as MIPS-lite. The simulator is designed to execute a trace of instructions, simulate their effects on memory and registers, and support basic pipelining with optional forwarding. Below is an overview of the modules and instructions on how to run the simulator.

## Modules Overview
### 1. Memory

This module simulates the memory component of the MIPS-lite architecture. It supports reading and writing words and bytes to memory, as well as initializing the memory state from a trace file.

- **Initialization**: Loads a trace file and stores its contents in a dictionary.
- **Reading and Writing**: Supports read_word, read_byte, write_word, and write_byte operations.

### 2. Instruction

Defines the Instruction class, which represents a MIPS-lite instruction. It includes methods to decode an instruction from its hexadecimal representation into its constituent parts, such as opcode, registers, and immediate values.

- **Decoding**: Extracts opcode, register identifiers, and immediate values from the instruction's binary representation.

### 3. Processor

Simulates a 5-stage pipelined processor with optional forwarding. It orchestrates the fetching, decoding, execution, memory access, and write-back stages for instructions.

- **Pipelining**: Implements a basic 5-stage instruction pipeline.
- **Forwarding**: Optionally supports forwarding to mitigate data hazards.

### 4. Registers

A part of the memory module, it simulates the register file of the MIPS-lite architecture, supporting read and write operations to registers.

- **Register Operations**: Allows reading from and writing to 32 general-purpose registers.

## Running Instructions

1. **Prepare Trace Files**: Ensure you have a trace file containing the memory image and instructions you wish to simulate.

2. **Run the Simulator**: Execute the main.py script to start the simulation. You can modify the path to the trace file within main.py to point to your specific trace file.

```bash
python main.py <path to trace file>
```

3. **View Results**: After execution, the simulator prints statistics about the execution, including the number of arithmetic, logic, control, and load/store instructions executed, as well as any changes to the memory and register state.

### Example Command

```bash
python main.py
```

This command runs the simulator using the trace file specified in `main.py`. Ensure you have Python installed on your system to execute this command.

## Conclusion

This MIPS-lite simulator provides a basic framework for simulating a simplified MIPS architecture, including memory, instruction decoding, and a pipelined processor with optional forwarding. It's a useful tool for educational purposes and for understanding the basics of MIPS architecture and instruction pipelining.
