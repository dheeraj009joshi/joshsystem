#!/usr/bin/env python3
"""
Cleanup script to rename old study folders to use clean naming pattern.
This script will rename folders from study_UUID to study_clean_title format.
"""

import os
import re
import shutil
from pathlib import Path

def clean_title_for_folder(title):
    """Clean study title for folder naming."""
    # Remove special characters, keep letters, numbers, spaces, hyphens
    clean_title = re.sub(r'[^\w\s-]', '', title)
    # Replace spaces and hyphens with underscores
    clean_title = re.sub(r'[-\s]+', '_', clean_title)
    # Remove leading/trailing underscores and convert to lowercase
    clean_title = clean_title.strip('_').lower()
    return clean_title

def get_study_title_from_folder(folder_path):
    """Try to extract study title from folder contents or database."""
    # This is a placeholder - in a real implementation, you'd need to:
    # 1. Connect to your database
    # 2. Find the study by UUID
    # 3. Extract the title from the study document
    
    # For now, we'll use a simple mapping or ask user to provide titles
    print(f"📁 Found folder: {folder_path}")
    print(f"🔍 Please provide the study title for this folder:")
    title = input("Study Title: ").strip()
    return title

def cleanup_study_folders(local_uploads_dir):
    """Clean up old study folders to use clean naming."""
    print("🧹 Starting cleanup of old study folders...")
    
    if not os.path.exists(local_uploads_dir):
        print(f"❌ Directory not found: {local_uploads_dir}")
        return
    
    # Find all study folders with UUID pattern
    uuid_pattern = re.compile(r'^study_[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$')
    
    study_folders = []
    for item in os.listdir(local_uploads_dir):
        item_path = os.path.join(local_uploads_dir, item)
        if os.path.isdir(item_path) and uuid_pattern.match(item):
            study_folders.append(item)
    
    if not study_folders:
        print("✅ No old study folders found with UUID pattern.")
        return
    
    print(f"📋 Found {len(study_folders)} old study folders:")
    for folder in study_folders:
        print(f"   - {folder}")
    
    print("\n🔄 Starting cleanup process...")
    
    for old_folder_name in study_folders:
        old_path = os.path.join(local_uploads_dir, old_folder_name)
        
        try:
            # Extract UUID from folder name
            uuid_match = re.search(r'study_([a-f0-9-]{36})', old_folder_name)
            if not uuid_match:
                print(f"⚠️  Skipping {old_folder_name} - doesn't match UUID pattern")
                continue
            
            study_uuid = uuid_match.group(1)
            
            # Get study title (this would ideally come from database)
            print(f"\n📁 Processing: {old_folder_name}")
            study_title = get_study_title_from_folder(old_folder_name)
            
            if not study_title:
                print(f"⚠️  Skipping {old_folder_name} - no title provided")
                continue
            
            # Create new folder name
            clean_title = clean_title_for_folder(study_title)
            new_folder_name = f"study_{clean_title}"
            new_path = os.path.join(local_uploads_dir, new_folder_name)
            
            # Check if new folder already exists
            if os.path.exists(new_path):
                print(f"⚠️  Target folder already exists: {new_folder_name}")
                choice = input("Overwrite? (y/N): ").strip().lower()
                if choice != 'y':
                    print(f"⏭️  Skipping {old_folder_name}")
                    continue
            
            # Rename the folder
            print(f"🔄 Renaming: {old_folder_name} → {new_folder_name}")
            shutil.move(old_path, new_path)
            print(f"✅ Successfully renamed to: {new_folder_name}")
            
        except Exception as e:
            print(f"❌ Error processing {old_folder_name}: {e}")
            continue
    
    print("\n🎉 Cleanup completed!")

def main():
    """Main cleanup function."""
    print("🧹 Study Folder Cleanup Tool")
    print("=" * 50)
    
    # Default local uploads directory
    default_dir = "local_uploads"
    
    # Check if we're in the right directory
    if not os.path.exists(default_dir):
        print(f"❌ Local uploads directory not found: {default_dir}")
        print("Please run this script from the unileverImageStudy directory")
        return
    
    print(f"📂 Using directory: {os.path.abspath(default_dir)}")
    
    # Confirm before proceeding
    print("\n⚠️  This will rename study folders to use clean naming.")
    print("Make sure you have backups if needed.")
    choice = input("Continue? (y/N): ").strip().lower()
    
    if choice == 'y':
        cleanup_study_folders(default_dir)
    else:
        print("❌ Cleanup cancelled.")

if __name__ == "__main__":
    main()
