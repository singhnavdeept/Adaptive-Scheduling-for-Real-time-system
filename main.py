from tasks import PeriodicTask, AperiodicTask, SporadicTask, generate_random_task
from schedulers import edf_scheduler, rate_monotonic_scheduler, fcfs_scheduler, priority_inheritance_scheduler, least_laxity_scheduler, adaptive_scheduler
from visualization import draw, screen, pygame, scheduler_buttons
from resources import ResourceManager
import random
import time

# Initial tasks
tasks = [
    PeriodicTask(1, 0, 3, 5, 8, 2),
    AperiodicTask(2, 1, 2, 6, 1),
    SporadicTask(3, 2, 1, 4, 5, 3)
]

# Setup
current_time = 0
scheduler = edf_scheduler
scheduler_name = "EDF"
resource_manager = ResourceManager()
task_id = 4
stats = {'completed': 0, 'missed': 0}
running = True
paused = False
speed = 1.0
log_file = open("scheduler_log.txt", "w")
history = []  # (task_id, start_time, end_time)

def log_event(event):
    log_file.write(f"[Time {current_time:.1f}] {event}\n")
    log_file.flush()

# Scheduler mapping
scheduler_map = {
    "edf_scheduler": edf_scheduler,
    "rate_monotonic_scheduler": rate_monotonic_scheduler,
    "fcfs_scheduler": fcfs_scheduler,
    "priority_inheritance_scheduler": priority_inheritance_scheduler,
    "least_laxity_scheduler": least_laxity_scheduler
}

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for btn in scheduler_buttons:
                if btn["rect"].collidepoint(event.pos):
                    scheduler = scheduler_map[btn["scheduler"]]
                    scheduler_name = btn["scheduler"]
                    log_event(f"Switched to {btn['name']}")
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                new_task = generate_random_task(current_time, task_id)
                tasks.append(new_task)
                log_event(f"Added {new_task.__class__.__name__} Task {task_id}")
                task_id += 1
            elif event.key == pygame.K_p:
                paused = not paused
                log_event("Paused" if paused else "Resumed")
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                speed = min(speed + 0.5, 3.0)
                log_event(f"Speed increased to {speed:.1f}x")
            elif event.key == pygame.K_MINUS:
                speed = max(speed - 0.5, 0.5)
                log_event(f"Speed decreased to {speed:.1f}x")

    if not paused:
        # Random task generation
        if current_time < 50 and random.random() < 0.05:
            new_task = generate_random_task(current_time, task_id)
            tasks.append(new_task)
            log_event(f"Random {new_task.__class__.__name__} Task {task_id}")
            task_id += 1

        # Schedule and execute
        current_task = adaptive_scheduler(scheduler, tasks, current_time, resource_manager)
        if current_task:
            if current_task.remaining_time == current_task.execution_time and len(current_task.resources) < 2:
                res = random.choice(['R1', 'R2', 'R3', 'R4'])
                if resource_manager.request_resource(current_task, res):
                    log_event(f"Task {current_task.id} took {res}")
            start_time = current_time if current_task.remaining_time == current_task.execution_time else start_time
            current_task.remaining_time -= (0.1 + current_task.delay) * speed
            current_task.update_status(current_time)
            if current_task.completed:
                for res in current_task.resources[:]:
                    resource_manager.release_resource(current_task, res)
                    log_event(f"Task {current_task.id} released {res}")
                history.append((current_task.id, start_time, current_time))
                tasks.remove(current_task)
                stats['completed'] += 1
                log_event(f"Task {current_task.id} completed")
            elif current_task.missed_deadline and current_task in tasks:
                tasks.remove(current_task)
                stats['missed'] += 1
                log_event(f"Task {current_task.id} missed deadline")

        # Periodic task regeneration
        for task in tasks[:]:
            if isinstance(task, PeriodicTask) and current_time >= task.next_arrival:
                new_task = PeriodicTask(task_id, current_time, task.execution_time, 
                                       current_time + (task.deadline - task.arrival_time), task.period, task.priority)
                tasks.append(new_task)
                log_event(f"Regenerated Periodic Task {task_id}")
                task_id += 1
                task.next_arrival += task.period

        # Deadlock resolution
        victim = resource_manager.resolve_deadlock(tasks)
        if victim and victim in tasks:
            tasks.remove(victim)
            stats['missed'] += 1
            log_event(f"Task {victim.id} preempted to resolve deadlock")

        current_time += 0.1 * speed

    # Draw
    draw(scheduler_name, tasks, current_time, current_task, resource_manager, stats, paused, speed, history)

log_file.close()
pygame.quit()