#!/usr/bin/env python3
"""
Example Plugin for Ultimate Agent
Demonstrates basic plugin functionality
"""

class ExamplePlugin:
    """Example plugin that demonstrates various hooks"""
    
    def __init__(self):
        self.name = "Example Plugin"
        self.version = "1.0.0"
        self.description = "Demonstrates plugin functionality"
        self.author = "Ultimate Agent Team"
        
        # Plugin state
        self.task_count = 0
        self.start_time = None
    
    def get_metadata(self):
        """Return plugin metadata"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'hooks': ['on_agent_start', 'on_task_start', 'on_task_complete']
        }
    
    def on_agent_start(self, agent):
        """Called when agent starts"""
        import time
        self.start_time = time.time()
        print(f"🔌 {self.name}: Agent started!")
        return {'status': 'initialized', 'plugin': self.name}
    
    def on_task_start(self, task_data):
        """Called when a task starts"""
        self.task_count += 1
        task_type = task_data.get('task_type', 'unknown')
        print(f"🔌 {self.name}: Task #{self.task_count} started ({task_type})")
        return {'task_number': self.task_count, 'plugin': self.name}
    
    def on_task_complete(self, task_data):
        """Called when a task completes"""
        success = task_data.get('success', False)
        duration = task_data.get('duration', 0)
        status = "✅ succeeded" if success else "❌ failed"
        print(f"🔌 {self.name}: Task {status} in {duration:.1f}s")
        return {'plugin_response': f'Task {status}', 'plugin': self.name}
    
    def get_stats(self):
        """Return plugin statistics"""
        import time
        uptime = time.time() - self.start_time if self.start_time else 0
        return {
            'tasks_observed': self.task_count,
            'uptime_seconds': uptime,
            'plugin_name': self.name
        }

# Plugin entry point
def create_plugin():
    """Factory function to create plugin instance"""
    return ExamplePlugin()
