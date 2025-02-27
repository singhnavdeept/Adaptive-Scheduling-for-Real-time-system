import random

class Task:
    def __init__(self, id, arrival_time, execution_time, deadline, priority=1):
        self.id = id
        self.arrival_time = arrival_time
        self.execution_time = execution_time
        self.deadline = deadline
        self.remaining_time = execution_time
        self.resources = []
        self.completed = False
        self.missed_deadline = False
        self.priority = priority  # Higher = more urgent
        self.delay = random.uniform(0, 0.5)  # Simulated I/O wait

    def update_status(self, current_time):
        if self.remaining_time <= 0:
            self.completed = True
        elif current_time > self.deadline and self.remaining_time > 0:
            self.missed_deadline = True

class PeriodicTask(Task):
    def __init__(self, id, arrival_time, execution_time, deadline, period, priority=1):
        super().__init__(id, arrival_time, execution_time, deadline, priority)
        self.period = period
        self.next_arrival = arrival_time + period

class AperiodicTask(Task):
    def __init__(self, id, arrival_time, execution_time, deadline, priority=1):
        super().__init__(id, arrival_time, execution_time, deadline, priority)

class SporadicTask(Task):
    def __init__(self, id, arrival_time, execution_time, deadline, min_interarrival, priority=1):
        super().__init__(id, arrival_time, execution_time, deadline, priority)
        self.min_interarrival = min_interarrival

def generate_random_task(current_time, task_id):
    task_type = random.choice(['periodic', 'aperiodic', 'sporadic'])
    exec_time = random.randint(1, 5)
    priority = random.randint(1, 3)
    if task_type == 'periodic':
        period = random.randint(5, 15)
        deadline = current_time + exec_time + random.randint(1, 5)
        return PeriodicTask(task_id, current_time, exec_time, deadline, period, priority)
    elif task_type == 'aperiodic':
        deadline = current_time + exec_time + random.randint(1, 3)
        return AperiodicTask(task_id, current_time, exec_time, deadline, priority)
    else:
        deadline = current_time + exec_time + random.randint(1, 5)
        min_inter = random.randint(3, 10)
        return SporadicTask(task_id, current_time, exec_time, deadline, min_inter, priority)