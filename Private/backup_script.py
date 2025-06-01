#!/usr/bin/env python3
"""
Backup Script for Sovereignty AI Agent System
Creates timestamped backups of all 4 critical agents
"""

import os
import shutil
from datetime import datetime

def create_agent_backups():
    """Create timestamped backups of all AI agents"""
    
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Define agent files to backup
    agent_files = [
        "data_intelligence_agent.py",
        "behavior_insights_agent.py", 
        "ai_philosophy_agent.py",
        "email_composer_agent.py"
    ]
    
    # Base paths - use current directory since we're running from Private folder
    current_dir = os.getcwd()
    backup_folder = os.path.join(current_dir, "backups")
    
    # Create backup directory if it doesn't exist
    os.makedirs(backup_folder, exist_ok=True)
    
    print(f"🔄 Creating AI Agent Backups - {timestamp}")
    print(f"📁 Looking in: {current_dir}")
    print("=" * 50)
    
    for agent_file in agent_files:
        source_path = os.path.join(current_dir, agent_file)
        
        if os.path.exists(source_path):
            # Create backup filename with timestamp
            backup_filename = f"{agent_file.replace('.py', '')}_{timestamp}.py"
            backup_path = os.path.join(backup_folder, backup_filename)
            
            # Copy file
            shutil.copy2(source_path, backup_path)
            print(f"✅ Backed up: {agent_file} → {backup_filename}")
        else:
            print(f"❌ Not found: {agent_file}")
    
    print("=" * 50)
    print(f"🚀 Backup complete! Files saved to: {backup_folder}")
    
    # List all backup files
    backup_files = [f for f in os.listdir(backup_folder) if f.endswith('.py')]
    backup_files.sort()
    
    print(f"\n📁 Current backup files ({len(backup_files)}):")
    for backup_file in backup_files[-10:]:  # Show last 10 backups
        print(f"   {backup_file}")
    
    return backup_folder

def test_agent_imports():
    """Test that all agent files can be imported"""
    print(f"\n🧪 Testing Agent Imports...")
    print("=" * 30)
    
    agents_to_test = [
        ("data_intelligence_agent", "DataIntelligenceAgent"),
        ("behavior_insights_agent", "BehavioralInsightsAgent"),
        ("ai_philosophy_agent", "SovereigntyPhilosophyAgent"),
        ("email_composer_agent", "EmailComposerAgent")
    ]
    
    # No need to add path since we're already in the Private folder
    for module_name, class_name in agents_to_test:
        try:
            module = __import__(module_name)
            agent_class = getattr(module, class_name)
            print(f"✅ {class_name}: Import successful")
        except ImportError as e:
            print(f"❌ {class_name}: Import failed - {e}")
        except AttributeError as e:
            print(f"⚠️  {class_name}: Class not found - {e}")
        except Exception as e:
            print(f"❌ {class_name}: Error - {e}")
    
    print("=" * 30)

if __name__ == "__main__":
    # Create backups
    backup_folder = create_agent_backups()
    
    # Test imports
    test_agent_imports()
    
    print(f"\n🛡️  Your AI Agent system is backed up and ready!")
    print(f"Backup location: {backup_folder}")
    print("Now you can safely iterate on the Wilber integration!")