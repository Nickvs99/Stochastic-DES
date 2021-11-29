import math
import numpy as np
import random
import simpy

INIT_TASKS = 4
N_MACHINES = 1
MAX_SIM_TIME = 100000
TASK_DURATION = 10
TASK_CREATION = 3
TASK_CREATION_SPREAD = 2

MARKOV_TASK_DURATION = 1
MARKOV_TASK_ARRIVAL = 0.9

data = {
    "wait_times": [],
    "process_times": [],
}

class Server():

    def __init__(self, env, n_machines):
        self.env = env
        self.machine = simpy.Resource(env, n_machines)

    def run_task(self, task):
        yield self.env.timeout(task.get_task_duration())

    @property
    def queue_length(self):
        return len(self.machine.queue)

class Task():

    def __init__(self, name):
        self.name = name

    def get_task_duration(self):
        return generate_random_markov(MARKOV_TASK_DURATION)

    def __str__(self):
        return f"{self.name}"

def process_task(env, task, server):

    #print(f"{task} added to server at {env.now}. Queue length: {server.queue_length}")
    time_at_queue = env.now
    with server.machine.request() as request:
        yield request

        #print(f"{task} is being processed at {env.now}")
        time_start_process = env.now
        yield env.process(server.run_task(task))
        #print(f"{task} is completed at {env.now}")
        time_end_process = env.now

    data["wait_times"].append(time_start_process - time_at_queue)
    data["process_times"].append(time_end_process - time_start_process)

def setup(env, n_machines):

    server = Server(env, n_machines)

    for i in range(INIT_TASKS):
        env.process(process_task(env, Task(f"Task {i}"), server))

    while True:
        yield env.timeout(generate_random_markov(MARKOV_TASK_ARRIVAL))
        i += 1
        env.process(process_task(env, Task(f"Task {i}"), server))

def generate_random_markov(lamda):
    """
    Markov CDF: y = 1 - e^(-lamda t)
    The y value has a range of 0 to 1, which we can sample.
    Thus we can obtain a random t value by sampling y

    t = - ln(1 - y) / lamda
    """

    r = random.random()
    return -math.log(1 - r) / lamda


def main():

    env = simpy.Environment()
    env.process(setup(env, N_MACHINES))
    env.run(until=MAX_SIM_TIME)

    print(f"Avg wait time: {np.mean(data['wait_times'])}")
    print(f"Avg process time: {np.mean(data['process_times'])}")

if __name__ == "__main__":
    main()