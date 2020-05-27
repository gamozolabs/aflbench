#!/usr/bin/env python3

import os, shutil, multiprocessing, time, subprocess

# Maximum number of threads to fuzz with AFL in parallel during benchmark
MAX_THREADS = 192

def fuzz_worker(thr_id):
    os.sched_setaffinity(0, [thr_id])
    sp=subprocess.Popen([f"../AFLplusplus/afl-fuzz -i inputs/ -o outputs/ -d -S {thr_id} -- ./aflfuzzbencher @@"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    while sp.poll() == None:
        print(sp.stdout.read())
        print(sp.stderr.read())
        time.sleep(0.1)

def benchmark_afl(num_threads):
    assert num_threads > 0
            
    # Kill anything that may already have been running
    os.system("killall -9 aflfuzzbencher 2> /dev/null")
        
    # Kill active shared memory, AFL will run out and crash eventually
    # due to shmget() failures
    assert os.system("ipcrm -a") == 0

    # Set the environment variables we want so AFL behaves
    os.environ["AFL_NO_AFFINITY"] = "123"

    # Remove our input and output directories
    if os.path.exists("inputs"):
        shutil.rmtree("inputs")
    if os.path.exists("outputs"):
        shutil.rmtree("outputs")

    # Make the input and output directories
    os.mkdir("inputs")
    os.mkdir("outputs")

    # Create a test input
    with open("inputs/test_input", "wb") as fd:
        fd.write(b"A"*128)

    # Spawn threads
    threads = []
    for thr_id in range(num_threads):
        thread = multiprocessing.Process(target=fuzz_worker, args=[thr_id])
        thread.start()
        threads.append(thread)

    # Wait a bit for the benchmark
    time.sleep(5.0)

    # Kill all workers
    for thread in threads:
        thread.terminate()
        thread.join()

    # Kill the process, as `terminate` orphans processes, I'm just lazy this
    # could be done better
    os.system("killall -9 aflfuzzbencher 2> /dev/null")

    # Go through AFL status messages, pick the most recently logged line and
    # sum up the per-thread cases per second to get a total cases per second
    total_per_second = 0
    for thr_id in range(num_threads):
        with open(f"outputs/{thr_id}/plot_data", "r") as fd:
            # Get the last status line for this thread
            contents      = fd.read().splitlines()
            last_status   = contents[-1]
            iters_per_sec = float(last_status.split(",")[-1].strip())
            total_per_second += iters_per_sec

    print(f"{num_threads:6} {total_per_second:16.6f}")

# Build our test program
assert os.system("../AFLplusplus/afl-clang-fast -O2 test.c -o aflfuzzbencher > /dev/null") == 0

# Benchmark AFL performance for each number of threads
for num_threads in range(1, MAX_THREADS + 1):
    while True:
        try:
            benchmark_afl(num_threads)
            break
        except:
            continue

