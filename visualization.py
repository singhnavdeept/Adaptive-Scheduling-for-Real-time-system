import pygame

pygame.init()
WIDTH, HEIGHT = 1000, 700  # Wider and taller for more space
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Adaptive Scheduler Simulation")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (50, 50, 50)
LIGHT_BLUE = (173, 216, 230)

font = pygame.font.SysFont(None, 24)
small_font = pygame.font.SysFont(None, 18)

# Scheduler buttons
scheduler_buttons = [
    {"name": "EDF", "rect": pygame.Rect(10, 10, 60, 30), "scheduler": "edf_scheduler"},
    {"name": "RM", "rect": pygame.Rect(80, 10, 60, 30), "scheduler": "rate_monotonic_scheduler"},
    {"name": "FCFS", "rect": pygame.Rect(150, 10, 60, 30), "scheduler": "fcfs_scheduler"},
    {"name": "PI", "rect": pygame.Rect(220, 10, 60, 30), "scheduler": "priority_inheritance_scheduler"},
    {"name": "LLF", "rect": pygame.Rect(290, 10, 60, 30), "scheduler": "least_laxity_scheduler"},
]

def draw(scheduler_name, tasks, current_time, current_task, resource_manager, stats, paused, speed, history):
    screen.fill(DARK_GRAY)  # Darker background for contrast

    # Header: Scheduler buttons and time
    for btn in scheduler_buttons:
        color = LIGHT_BLUE if btn["scheduler"] == scheduler_name else GRAY
        pygame.draw.rect(screen, color, btn["rect"])
        pygame.draw.rect(screen, BLACK, btn["rect"], 1)
        text = small_font.render(btn["name"], True, BLACK)
        screen.blit(text, (btn["rect"].x + 10, btn["rect"].y + 5))
    
    status = "Paused" if paused else "Running"
    time_text = font.render(f"Time: {current_time:.1f} | {status} | Speed: {speed:.1f}x", True, WHITE)
    screen.blit(time_text, (360, 15))

    # Task list (scrollable area)
    pygame.draw.rect(screen, WHITE, (10, 50, 480, 400))  # Task area
    pygame.draw.rect(screen, BLACK, (10, 50, 480, 400), 2)
    task_label = font.render("Current Tasks", True, BLACK)
    screen.blit(task_label, (15, 55))
    
    mouse_pos = pygame.mouse.get_pos()
    for i, task in enumerate(tasks[:8]):  # Limit to 8 visible
        y = 80 + i * 40
        width = task.execution_time * 20
        remaining_width = max(task.remaining_time * 20, 0)
        color = GREEN if task == current_task else BLUE
        if task.completed:
            color = GRAY
        elif task.missed_deadline:
            color = RED
        pygame.draw.rect(screen, color, (20, y, remaining_width, 20))
        pygame.draw.rect(screen, BLACK, (20, y, width, 20), 1)
        task_info = f"T{task.id}: D:{task.deadline:.1f} P:{task.priority}"
        if hasattr(task, 'period'):
            task_info += f" Per:{task.period}"
        task_text = small_font.render(task_info, True, BLACK)
        screen.blit(task_text, (20, y + 25))
        
        # Tooltip on hover
        if 20 <= mouse_pos[0] <= 20 + width and y <= mouse_pos[1] <= y + 20:
            tooltip = f"Resources: {task.resources}"
            tip_text = small_font.render(tooltip, True, BLACK)
            pygame.draw.rect(screen, LIGHT_BLUE, (mouse_pos[0] + 10, mouse_pos[1] + 10, 150, 20))
            screen.blit(tip_text, (mouse_pos[0] + 15, mouse_pos[1] + 15))

    # Gantt chart (history)
    pygame.draw.rect(screen, WHITE, (500, 50, 490, 200))  # Gantt area
    pygame.draw.rect(screen, BLACK, (500, 50, 490, 200), 2)
    gantt_label = font.render("Task History (Gantt)", True, BLACK)
    screen.blit(gantt_label, (505, 55))
    for entry in history[-20:]:  # Last 20 executed tasks
        task_id, start, end = entry
        x = 510 + (start * 20)
        width = (end - start) * 20
        if x + width > 980:
            width = 980 - x
        y = 80 + (task_id % 5) * 30
        pygame.draw.rect(screen, GREEN, (x, y, width, 20))

    # Dashboard
    pygame.draw.rect(screen, WHITE, (10, 460, 980, 230))  # Dashboard area
    pygame.draw.rect(screen, BLACK, (10, 460, 980, 230), 2)
    dash_label = font.render("Dashboard", True, BLACK)
    screen.blit(dash_label, (15, 465))
    
    stats_text = font.render(f"Tasks: {len(tasks)} | Completed: {stats['completed']} | Missed: {stats['missed']}", True, BLACK)
    screen.blit(stats_text, (15, 495))
    wait_text = font.render(f"Waiting: {len(resource_manager.wait_graph)} | Resources: {dict(resource_manager.resources)}", True, BLACK)
    screen.blit(wait_text, (15, 525))
    controls = "Space: Add Task | P: Pause | +/-: Speed | Q: Quit | Click buttons to switch schedulers"
    controls_text = small_font.render(controls, True, BLACK)
    screen.blit(controls_text, (15, 555))
    
    if resource_manager.detect_deadlock(tasks):
        deadlock_text = font.render("DEADLOCK DETECTED", True, YELLOW)
        screen.blit(deadlock_text, (WIDTH // 2 - 50, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(30 / speed if speed > 0 else 30)