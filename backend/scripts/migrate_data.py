#!/usr/bin/env python3
"""
Data Migration Script

Standalone script to migrate existing mission data from legacy format
to new enhanced Answer model. Run this after deploying the new code
to ensure existing data is compatible.

Usage:
    python -m backend.scripts.migrate_data
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.database import db_manager
from backend.services.data_migration_service import run_migration

async def main():
    """Main migration execution function."""
    try:
        print("=== EdTech Data Migration Script ===")
        print("Connecting to database...")
        
        # Connect to database
        db_manager.connect_to_database()
        db = db_manager.get_database()
        
        if db is None:
            print("ERROR: Could not connect to database")
            return 1
        
        print("Database connected successfully")
        
        # Run migration
        results = await run_migration(db)
        
        # Print results summary
        print("\n=== MIGRATION SUMMARY ===")
        migration = results["migration"]
        validation = results["validation"]
        
        print(f"Processed: {migration['total_processed']} missions")
        print(f"Migrated: {migration['migrated_count']} missions")
        print(f"Errors: {migration['error_count']} missions")
        
        print(f"\nValidation: {validation['valid_missions']}/{validation['total_missions']} missions valid")
        
        if validation["validation_passed"]:
            print("✅ Migration completed successfully!")
            return 0
        else:
            print("❌ Migration completed with validation errors:")
            for error in validation["invalid_missions"]:
                print(f"  - User {error['user_id']}: {error['error']}")
            return 1
            
    except Exception as e:
        print(f"CRITICAL ERROR: Migration failed - {str(e)}")
        return 1
    
    finally:
        # Close database connection
        db_manager.close_database_connection()
        print("Database connection closed")

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 