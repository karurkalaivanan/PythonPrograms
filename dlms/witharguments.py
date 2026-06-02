import threading
import time

def print_numbers(start, end):
    for i in range(start, end):
        time.sleep(1)
        print(f"Thread: {i}")

# Number of threads
num_threads = 3

# Create an array to hold thread instances
threads = []

# Start and end values for each thread
start_values = [1, 6, 11]
end_values = [6, 11, 16]

# Create threads and store them in the array
for i in range(num_threads):
    thread = threading.Thread(target=print_numbers, args=(start_values[i], end_values[i]))
    threads.append(thread)

# Start all threads
for thread in threads:
    thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()

print("All threads have finished.")
