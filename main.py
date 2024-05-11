from processor import Processor
from memory import Memory
import sys
import os

def main():
	if len(sys.argv) < 2:
		print("Usage: python main.py <memory_image_file>")
		sys.exit(1)

	image_file = sys.argv[1]

	# Check if the file exists
	if not os.path.exists(image_file):
		print(f"Error: The file '{image_file}' does not exist. Please provide a correct file.")
		sys.exit(1)  # Exit if the file does not exist

	mem_image = Memory(image_file)

	print("\n" + "*" * 10 + "ECE586 Spring 2024 Final Project Team 6" + "*" * 10)
	# Start the processor with forwarding disabled
	p1 = Processor(mem_image, forwarding=False, debug=False)
	p1.run()
	p1.print_stats()
	stats_without_forwarding = p1.store_stats()

	# Start the processor with forwarding enabled
	p2 = Processor(mem_image, forwarding=True)
	p2.run()
	p2.print_stats()
	print("\n************************************\n")
	stats_with_forwarding = p2.store_stats()

	# Extract total cycles from stats
	cycles_without_forwarding = stats_without_forwarding['cycles']
	cycles_with_forwarding = stats_with_forwarding['cycles']

	# Extract IPC from stats
	ipc_without_forwarding = stats_without_forwarding['ipc']
	ipc_with_forwarding = stats_with_forwarding['ipc']

	# Calculate speedup
	if cycles_with_forwarding > 0:
		speedup = cycles_without_forwarding / cycles_with_forwarding
	else:
		speedup = float('inf')  # Avoid division by zero

	print("*" * 5 + " Forwarding vs. Non-Forwarding Comparison " + "*" * 5 + "\n")
	print(f"Total clock cycle count without forwarding: {cycles_without_forwarding}")
	print(f"Total clock cycle count with forwarding: {cycles_with_forwarding}")
	print(f"Speedup due to forwarding: {speedup:.2f}x")
	print(f"Total IPC lift (%) due to forwarding: {(ipc_with_forwarding - ipc_without_forwarding) * 100:.2f}%")
	print("\n************************************\n")

if __name__ == "__main__":
    main()
