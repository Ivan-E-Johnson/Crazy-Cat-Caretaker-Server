import time
import argparse

# Define the argument parser
parser = argparse.ArgumentParser(description='Emulating the Laser')

# Add arguments
parser.add_argument('-t', '--time', type=int, required=True,
                    help='time to run program')
parser.add_argument('-m', '--mode', type=str, required=False,
                    help='mode to run program with')

# Parse the arguments
args = parser.parse_args()

# Access the values of the arguments
duration = args.time
mode = args.mode


start_time = time.time()
while time.time() - start_time < duration:
    print(f"Running mode {mode}")

print(f"Program finished after {duration} seconds.")
