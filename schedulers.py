def edf_scheduler(tasks, current_time):
    ready_tasks = [t for t in tasks if t.arrival_time <= current_time and t.remaining_time > 0]
    if not ready_tasks:
        return None
    critical = [t for t in ready_tasks if t.deadline - current_time < 2]
    return min(critical or ready_tasks, key=lambda x: x.deadline)

def rate_monotonic_scheduler(tasks, current_time):
    ready_tasks = [t for t in tasks if t.arrival_time <= current_time and t.remaining_time > 0]
    if not ready_tasks:
        return None
    periodic_tasks = [t for t in ready_tasks if hasattr(t, 'period')]
    if periodic_tasks:
        return min(periodic_tasks, key=lambda x: x.period)
    return ready_tasks[0]

def fcfs_scheduler(tasks, current_time):
    ready_tasks = [t for t in tasks if t.arrival_time <= current_time and t.remaining_time > 0]
    if not ready_tasks:
        return None
    return min(ready_tasks, key=lambda x: x.arrival_time)

def priority_inheritance_scheduler(tasks, current_time, resource_manager):
    ready_tasks = [t for t in tasks if t.arrival_time <= current_time and t.remaining_time > 0]
    if not ready_tasks:
        return None
    for task in ready_tasks:
        for res, holder in resource_manager.resources.items():
            if holder == task:
                for other in ready_tasks:
                    if res in other.resources and other.priority > task.priority:
                        return other
    return max(ready_tasks, key=lambda x: x.priority)

def least_laxity_scheduler(tasks, current_time):
    ready_tasks = [t for t in tasks if t.arrival_time <= current_time and t.remaining_time > 0]
    if not ready_tasks:
        return None
    # Laxity = time to deadline - remaining time
    return min(ready_tasks, key=lambda x: (x.deadline - current_time) - x.remaining_time)

def adaptive_scheduler(base_scheduler, tasks, current_time, resource_manager, workload_threshold=5):
    workload = len([t for t in tasks if t.remaining_time > 0])
    if workload > workload_threshold:
        return priority_inheritance_scheduler(tasks, current_time, resource_manager)
    return base_scheduler(tasks, current_time)