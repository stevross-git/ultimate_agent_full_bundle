#!/usr/bin/env python3
"""
Quick fix script for import issues
Run this to fix the import paths automatically
"""

import os
import re
from pathlib import Path

def fix_import_issues():
    """Fix common import issues in the codebase"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    print("🔧 Fixing import issues...")
    
    # Fix 1: Update agent1.py ConfigManager import
    agent1_file = project_root / "ultimate_agent" / "core" / "agent1.py"
    if agent1_file.exists():
        print(f"📝 Fixing {agent1_file}")
        
        with open(agent1_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the incorrect import
        content = content.replace(
            "from ..config.settings import ConfigManager",
            "from ..config.config_settings import ConfigManager"
        )
        
        with open(agent1_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed ConfigManager import in agent1.py")
    
    # Fix 2: Check for other common import issues
    common_fixes = [
        # Fix TaskScheduler import path
        {
            'pattern': r'from \.\.tasks\.execution\.scheduler import TaskScheduler',
            'replacement': 'from ..tasks.execution.task_scheduler import TaskScheduler'
        },
        # Fix any other missing imports
    ]
    
    # Apply fixes to all Python files
    for py_file in project_root.rglob("*.py"):
        if py_file.name.startswith('__') or 'test' in py_file.name:
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            for fix in common_fixes:
                content = re.sub(fix['pattern'], fix['replacement'], content)
            
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Applied fixes to {py_file.relative_to(project_root)}")
                
        except Exception as e:
            print(f"⚠️ Could not process {py_file}: {e}")
    
    print("✅ Import fixes completed!")

if __name__ == "__main__":
    fix_import_issues()