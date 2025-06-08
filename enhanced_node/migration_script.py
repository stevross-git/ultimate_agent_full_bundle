#!/usr/bin/env python3
"""
Enhanced Node Server Migration Script
Migrate from monolithic enhanced_remote_node_v345.py to modular structure
"""

import os
import sys
import shutil
import sqlite3
import json
import argparse
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MonolithMigrator:
    """Migrate from monolithic to modular Enhanced Node Server"""
    
    def __init__(self, source_dir: str, target_dir: str, backup: bool = True):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.backup = backup
        self.backup_dir = Path("migration_backup")
        
        # Ensure directories exist
        self.target_dir.mkdir(exist_ok=True, parents=True)
        if self.backup:
            self.backup_dir.mkdir(exist_ok=True)
    
    def validate_source(self) -> bool:
        """Validate source directory contains monolithic installation"""
        logger.info("Validating source directory...")
        
        # Check for monolithic script
        monolith_file = self.source_dir / "enhanced_remote_node_v345.py"
        if not monolith_file.exists():
            logger.error(f"Monolithic script not found: {monolith_file}")
            return False
        
        # Check for database
        db_file = self.source_dir / "enhanced_node_server.db"
        if not db_file.exists():
            logger.warning(f"Database not found: {db_file}")
        
        # Check for logs
        logs_dir = self.source_dir / "logs"
        if not logs_dir.exists():
            logger.warning(f"Logs directory not found: {logs_dir}")
        
        logger.info("✅ Source validation completed")
        return True
    
    def create_backup(self):
        """Create backup of existing installation"""
        if not self.backup:
            return
            
        logger.info("Creating backup of existing installation...")
        
        backup_name = f"monolith_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copytree(self.source_dir, backup_path)
            logger.info(f"✅ Backup created: {backup_path}")
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            raise
    
    def migrate_database(self):
        """Migrate database from source to target"""
        logger.info("Migrating database...")
        
        source_db = self.source_dir / "enhanced_node_server.db"
        target_db = self.target_dir / "data" / "enhanced_node_server.db"
        
        if not source_db.exists():
            logger.warning("Source database not found, creating new database")
            return
        
        # Create target data directory
        (self.target_dir / "data").mkdir(exist_ok=True)
        
        try:
            # Copy database file
            shutil.copy2(source_db, target_db)
            
            # Verify database integrity
            conn = sqlite3.connect(target_db)
            cursor = conn.cursor()
            
            # Check tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            logger.info(f"✅ Database migrated with {len(tables)} tables")
            
            # Print table summary
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                logger.info(f"  - {table[0]}: {count} records")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Database migration failed: {e}")
            raise
    
    def migrate_logs(self):
        """Migrate log files"""
        logger.info("Migrating log files...")
        
        source_logs = self.source_dir / "logs"
        target_logs = self.target_dir / "logs"
        
        if not source_logs.exists():
            logger.warning("Source logs directory not found")
            return
        
        target_logs.mkdir(exist_ok=True)
        
        try:
            # Copy all log files
            for log_file in source_logs.glob("*.log"):
                target_file = target_logs / log_file.name
                shutil.copy2(log_file, target_file)
                logger.info(f"  - Migrated: {log_file.name}")
            
            logger.info("✅ Log files migrated")
            
        except Exception as e:
            logger.error(f"❌ Log migration failed: {e}")
            raise
    
    def migrate_scripts(self):
        """Migrate agent scripts and command history"""
        logger.info("Migrating scripts and command history...")
        
        # Migrate agent scripts
        source_scripts = self.source_dir / "agent_scripts"
        target_scripts = self.target_dir / "agent_scripts"
        
        if source_scripts.exists():
            target_scripts.mkdir(exist_ok=True)
            try:
                for script_file in source_scripts.glob("*"):
                    target_file = target_scripts / script_file.name
                    shutil.copy2(script_file, target_file)
                logger.info("✅ Agent scripts migrated")
            except Exception as e:
                logger.error(f"❌ Agent scripts migration failed: {e}")
        
        # Migrate command history
        source_history = self.source_dir / "command_history"
        target_history = self.target_dir / "command_history"
        
        if source_history.exists():
            target_history.mkdir(exist_ok=True)
            try:
                for history_file in source_history.glob("*"):
                    target_file = target_history / history_file.name
                    shutil.copy2(history_file, target_file)
                logger.info("✅ Command history migrated")
            except Exception as e:
                logger.error(f"❌ Command history migration failed: {e}")
    
    def migrate_configuration(self):
        """Migrate configuration settings"""
        logger.info("Migrating configuration...")
        
        # Create environment file from defaults
        env_template = self.target_dir / ".env.example"
        env_target = self.target_dir / ".env"
        
        if env_template.exists() and not env_target.exists():
            shutil.copy2(env_template, env_target)
            logger.info("✅ Environment configuration created from template")
        
        # Extract configuration from monolithic script if possible
        monolith_file = self.source_dir / "enhanced_remote_node_v345.py"
        if monolith_file.exists():
            try:
                self.extract_config_from_monolith(monolith_file, env_target)
            except Exception as e:
                logger.warning(f"Could not extract config from monolith: {e}")
    
    def extract_config_from_monolith(self, monolith_file: Path, env_file: Path):
        """Extract configuration values from monolithic script"""
        logger.info("Extracting configuration from monolithic script...")
        
        config_values = {}
        
        with open(monolith_file, 'r') as f:
            content = f.read()
            
            # Extract common configuration values
            import re
            
            # Node configuration
            if match := re.search(r'NODE_VERSION\s*=\s*["\']([^"\']+)["\']', content):
                config_values['NODE_VERSION'] = match.group(1)
            
            if match := re.search(r'NODE_PORT\s*=\s*(\d+)', content):
                config_values['NODE_PORT'] = match.group(1)
            
            if match := re.search(r'MANAGER_HOST\s*=\s*["\']([^"\']+)["\']', content):
                config_values['MANAGER_HOST'] = match.group(1)
            
            if match := re.search(r'MANAGER_PORT\s*=\s*(\d+)', content):
                config_values['MANAGER_PORT'] = match.group(1)
            
            if match := re.search(r'NODE_ID\s*=\s*["\']([^"\']+)["\']', content):
                config_values['NODE_ID'] = match.group(1)
        
        # Update environment file
        if config_values and env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            for key, value in config_values.items():
                pattern = f'^{key}=.*$'
                replacement = f'{key}={value}'
                env_content = re.sub(pattern, replacement, env_content, flags=re.MULTILINE)
            
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            logger.info(f"✅ Extracted {len(config_values)} configuration values")
            for key, value in config_values.items():
                logger.info(f"  - {key}: {value}")
    
    def create_migration_report(self):
        """Create migration report"""
        logger.info("Creating migration report...")
        
        report = {
            "migration_date": datetime.now().isoformat(),
            "source_directory": str(self.source_dir),
            "target_directory": str(self.target_dir),
            "backup_directory": str(self.backup_dir) if self.backup else None,
            "migrated_components": [],
            "warnings": [],
            "next_steps": []
        }
        
        # Check what was migrated
        if (self.target_dir / "data" / "enhanced_node_server.db").exists():
            report["migrated_components"].append("Database")
        
        if (self.target_dir / "logs").exists() and list((self.target_dir / "logs").glob("*.log")):
            report["migrated_components"].append("Log files")
        
        if (self.target_dir / "agent_scripts").exists():
            report["migrated_components"].append("Agent scripts")
        
        if (self.target_dir / "command_history").exists():
            report["migrated_components"].append("Command history")
        
        if (self.target_dir / ".env").exists():
            report["migrated_components"].append("Configuration")
        
        # Add warnings and next steps
        report["warnings"] = [
            "Review .env configuration file and update as needed",
            "Verify database connectivity and integrity",
            "Check log file permissions",
            "Test all functionality before going live"
        ]
        
        report["next_steps"] = [
            "Install dependencies: pip install -r requirements.txt",
            "Review and update .env configuration",
            "Test the modular installation: python main.py",
            "Setup systemd service for production",
            "Configure Nginx reverse proxy",
            "Setup monitoring and backups"
        ]
        
        # Save report
        report_file = self.target_dir / "migration_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ Migration report saved: {report_file}")
        
        return report
    
    def run_migration(self):
        """Run complete migration process"""
        logger.info("Starting Enhanced Node Server migration...")
        logger.info(f"Source: {self.source_dir}")
        logger.info(f"Target: {self.target_dir}")
        
        try:
            # Validation
            if not self.validate_source():
                raise Exception("Source validation failed")
            
            # Backup
            if self.backup:
                self.create_backup()
            
            # Migration steps
            self.migrate_database()
            self.migrate_logs()
            self.migrate_scripts()
            self.migrate_configuration()
            
            # Generate report
            report = self.create_migration_report()
            
            logger.info("🎉 Migration completed successfully!")
            
            # Print summary
            print("\n" + "="*60)
            print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"📁 Target Directory: {self.target_dir}")
            print(f"📊 Migrated Components: {len(report['migrated_components'])}")
            for component in report['migrated_components']:
                print(f"   ✅ {component}")
            
            print("\n📋 Next Steps:")
            for i, step in enumerate(report['next_steps'], 1):
                print(f"   {i}. {step}")
            
            print(f"\n📄 Full report: {self.target_dir}/migration_report.json")
            
            if self.backup:
                print(f"💾 Backup: {self.backup_dir}")
            
            print("\n🚀 Ready to start modular Enhanced Node Server!")
            print("="*60)
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise


def main():
    """Main migration function"""
    parser = argparse.ArgumentParser(
        description="Migrate Enhanced Node Server from monolithic to modular structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python migrate_from_monolith.py /old/enhanced-node /new/enhanced-node
  python migrate_from_monolith.py /old/enhanced-node /new/enhanced-node --no-backup
  python migrate_from_monolith.py --source /old/path --target /new/path --backup
        """
    )
    
    parser.add_argument(
        'source',
        nargs='?',
        help='Source directory containing monolithic installation'
    )
    
    parser.add_argument(
        'target', 
        nargs='?',
        help='Target directory for modular installation'
    )
    
    parser.add_argument(
        '--source',
        help='Source directory (alternative to positional argument)'
    )
    
    parser.add_argument(
        '--target',
        help='Target directory (alternative to positional argument)'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backup of source'
    )
    
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Force creating backup (default: True)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Determine source and target
    source = args.source or getattr(args, 'source', None)
    target = args.target or getattr(args, 'target', None)
    
    if not source or not target:
        parser.error("Both source and target directories are required")
    
    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine backup setting
    backup = not args.no_backup
    
    # Run migration
    try:
        migrator = MonolithMigrator(source, target, backup=backup)
        migrator.run_migration()
        
    except KeyboardInterrupt:
        print("\n❌ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
