import random
import simpy

INIT_TASKS = 4
N_MACHINES = 3
MAX_SIM_TIME = 100
TASK_DURATION = 10
TASK_CREATION = 3
TASK_CREATION_SPREAD = 2

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
        return TASK_DURATION

    def __str__(self):
        return f"{self.name}"

def process_task(env, task, server):

    print(f"{task} added to server at {env.now}. Queue length: {server.queue_length}")
    with server.machine.request() as request:
        yield request

        print(f"{task} is being processed at {env.now}")
        yield env.process(server.run_task(task))
        print(f"{task} is completed at {env.now}")

def setup(env, n_machines):

    server = Server(env, n_machines)

    for i in range(INIT_TASKS):
        env.process(process_task(env, Task(f"Task {i}"), server))

    while True:
        yield env.timeout(random.randint(TASK_CREATION - TASK_CREATION_SPREAD, TASK_CREATION + TASK_CREATION_SPREAD))
        i += 1
        env.process(process_task(env, Task(f"Task {i}"), server))

def main():

    env = simpy.Environment()
    env.process(setup(env, N_MACHINES))
    env.run(until=MAX_SIM_TIME)

if __name__ == "__main__":
    main()