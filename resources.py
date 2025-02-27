class ResourceManager:
    def __init__(self):
        self.resources = {'R1': None, 'R2': None, 'R3': None, 'R4': None}  # Includes R4
        self.wait_graph = {}  # task -> resources it waits for

    def request_resource(self, task, resource):
        if self.resources[resource] is None:
            self.resources[resource] = task
            task.resources.append(resource)
            if task in self.wait_graph:
                del self.wait_graph[task]
            return True
        else:
            if task not in self.wait_graph:
                self.wait_graph[task] = []
            self.wait_graph[task].append(resource)
            return False

    def release_resource(self, task, resource):
        if resource in task.resources:
            self.resources[resource] = None
            task.resources.remove(resource)

    def detect_deadlock(self, tasks):
        for t1 in tasks:
            if t1 in self.wait_graph:
                for res in self.wait_graph[t1]:
                    holder = self.resources[res]
                    if holder and holder in self.wait_graph and any(r in holder.resources for r in t1.resources):
                        return True
        return False

    def resolve_deadlock(self, tasks):
        if self.detect_deadlock(tasks):
            deadlocked = [t for t in tasks if t in self.wait_graph or t.resources]
            victim = min(deadlocked, key=lambda x: x.priority)  # Preempt lowest priority
            for res in victim.resources[:]:
                self.release_resource(victim, res)
            if victim in self.wait_graph:
                del self.wait_graph[victim]
            return victim
        return None