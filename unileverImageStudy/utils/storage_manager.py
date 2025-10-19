"""
Unified Storage Manager for handling both Azure and Local file storage
"""
import os
import uuid
import shutil
from flask import current_app, send_file, abort
from werkzeug.utils import secure_filename
from utils.azure_storage import upload_to_azure, upload_to_azure_no_conversion, upload_multiple_files_to_azure, is_valid_image_file, get_file_size_mb


class StorageManager:
    """Unified storage manager that handles both Azure and local storage based on configuration."""
    
    @staticmethod
    def get_study_directory(study_id):
        """Get study-specific directory path for local storage."""
        # Check if this is a draft study (temporary)
        if study_id.startswith('draft_') or 'temp' in study_id.lower():
            return os.path.join(
                current_app.config['LOCAL_UPLOAD_FOLDER'], 
                'drafts',
                study_id  # Don't add 'draft_' prefix again
            )
        else:
            return os.path.join(
                current_app.config['LOCAL_UPLOAD_FOLDER'], 
                f"study_{study_id}"
            )
    
    @staticmethod
    def create_study_directory(study_id):
        """Create study-specific directory for local storage."""
        study_dir = StorageManager.get_study_directory(study_id)
        os.makedirs(study_dir, exist_ok=True)
        
        # Create subdirectories for organization
        subdirs = ['grid_categories', 'layers', 'default_background']
        for subdir in subdirs:
            subdir_path = os.path.join(study_dir, subdir)
            os.makedirs(subdir_path, exist_ok=True)
        
        return study_dir
    
    @staticmethod
    def upload_file(file, study_id, filename=None, subdirectory=None):
        """
        Upload file using configured storage method.
        
        Args:
            file: File object to upload
            study_id: Study ID for organizing files
            filename: Optional custom filename
            subdirectory: Optional subdirectory (grid_categories, layers, default_background)
        
        Returns:
            dict: Contains 'file_path' and 'url' keys
        """
        if not file or not file.filename:
            return None
        
        # Validate file type
        if not is_valid_image_file(file.filename):
            return None
        
        # Check file size (max 16MB)
        file_size_mb = get_file_size_mb(file)
        if file_size_mb > 16:
            return None
        
        if current_app.config.get('USE_LOCAL_STORAGE', False):
            return StorageManager._upload_local(file, study_id, filename, subdirectory)
        else:
            return StorageManager._upload_azure(file)
    
    @staticmethod
    def _upload_local(file, study_id, filename=None, subdirectory=None):
        """Upload file to local storage."""
        study_dir = StorageManager.create_study_directory(study_id)
        
        # Determine target directory
        if subdirectory:
            target_dir = os.path.join(study_dir, subdirectory)
            os.makedirs(target_dir, exist_ok=True)
        else:
            target_dir = study_dir
        
        # Generate filename
        if not filename:
            original_filename = secure_filename(file.filename)
            # Add unique prefix to avoid conflicts
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        else:
            unique_filename = filename
            
        file_path = os.path.join(target_dir, unique_filename)
        
        # Handle different file types
        if hasattr(file, 'save'):
            # Regular file object (Flask FileStorage)
            file.save(file_path)
        else:
            # BytesIO or similar object - write content to file
            with open(file_path, 'wb') as f:
                f.write(file.getvalue())
        
        # Return relative path for database storage
        # For drafts, use the actual directory structure
        if study_id.startswith('draft_') or 'temp' in study_id.lower():
            relative_path = f"drafts/{study_id}"
        else:
            relative_path = f"study_{study_id}"
        
        if subdirectory:
            relative_path += f"/{subdirectory}"
        relative_path += f"/{unique_filename}"
        
        return {
            'file_path': relative_path,
            'url': StorageManager._get_local_url(relative_path),
            'filename': unique_filename
        }
    
    @staticmethod
    def _upload_azure(file):
        """Upload file to Azure without WebP conversion."""
        azure_url = upload_to_azure_no_conversion(file)
        if azure_url:
            return {
                'file_path': azure_url,  # Azure URL is the file path
                'url': azure_url,
                'filename': secure_filename(file.filename)
            }
        return None
    
    @staticmethod
    def upload_multiple_files(files, study_id, subdirectory=None):
        """Upload multiple files with parallel processing when using Azure."""
        if not files:
            return []
        
        if current_app.config.get('USE_LOCAL_STORAGE', False):
            # Sequential local upload (already fast)
            results = []
            for file in files:
                result = StorageManager.upload_file(file, study_id, subdirectory=subdirectory)
                results.append(result)
            return results
        else:
            # Parallel Azure upload using ThreadPoolExecutor
            from concurrent.futures import ThreadPoolExecutor, as_completed
            import time
            
            results = [None] * len(files)
            
            def upload_single_file(file_with_index):
                file, index = file_with_index
                result = StorageManager.upload_file(file, study_id, subdirectory=subdirectory)
                return index, result
            
            # Use ThreadPoolExecutor for parallel uploads
            with ThreadPoolExecutor(max_workers=5) as executor:
                # Submit all upload tasks
                future_to_index = {
                    executor.submit(upload_single_file, (file, i)): i 
                    for i, file in enumerate(files)
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_index):
                    try:
                        index, result = future.result()
                        results[index] = result
                    except Exception as e:
                        index = future_to_index[future]
                        results[index] = {'error': str(e)}
                        current_app.logger.error(f"Parallel upload failed for file {index}: {str(e)}")
            
            return results
    
    @staticmethod
    def get_file_url(file_path, study_id=None):
        """Get accessible URL for file based on storage configuration."""
        if current_app.config.get('USE_LOCAL_STORAGE', False):
            return StorageManager._get_local_url(file_path)
        else:
            return file_path  # Azure URL is already accessible
    
    @staticmethod
    def _get_local_url(file_path):
        """Get local file URL for serving via Flask."""
        # file_path is already the relative path like "study_123/grid_categories/filename.jpg"
        return f"/static/uploads/{file_path}"
    
    @staticmethod
    def delete_study_files(study_id):
        """Delete all files for a study (local storage only)."""
        if current_app.config.get('USE_LOCAL_STORAGE', False):
            study_dir = StorageManager.get_study_directory(study_id)
            if os.path.exists(study_dir):
                try:
                    shutil.rmtree(study_dir)
                    print(f"✅ Deleted local files for study {study_id}")
                except Exception as e:
                    print(f"❌ Error deleting local files for study {study_id}: {e}")
    
    @staticmethod
    def move_draft_to_study(draft_id, final_study_id):
        """Move files from draft folder to final study folder."""
        if not current_app.config.get('USE_LOCAL_STORAGE', False):
            return False
        
        draft_dir = StorageManager.get_study_directory(draft_id)
        final_dir = StorageManager.get_study_directory(final_study_id)
        
        if not os.path.exists(draft_dir):
            return True  # No draft files to move
        
        try:
            # Create final study directory
            StorageManager.create_study_directory(final_study_id)
            
            # Move all files from draft to final
            for item in os.listdir(draft_dir):
                src = os.path.join(draft_dir, item)
                dst = os.path.join(final_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
            
            # Remove draft directory
            shutil.rmtree(draft_dir)
            print(f"✅ Moved draft {draft_id} to study {final_study_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error moving draft to study: {e}")
            return False
    
    @staticmethod
    def cleanup_old_drafts(max_age_hours=24):
        """Clean up old draft folders (older than max_age_hours)."""
        if not current_app.config.get('USE_LOCAL_STORAGE', False):
            return 0
        
        import time
        drafts_dir = os.path.join(current_app.config['LOCAL_UPLOAD_FOLDER'], 'drafts')
        if not os.path.exists(drafts_dir):
            return 0
        
        cleaned_count = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        try:
            for item in os.listdir(drafts_dir):
                item_path = os.path.join(drafts_dir, item)
                if os.path.isdir(item_path):
                    # Check if folder is older than max_age_hours
                    folder_age = current_time - os.path.getctime(item_path)
                    if folder_age > max_age_seconds:
                        shutil.rmtree(item_path)
                        cleaned_count += 1
                        print(f"🧹 Cleaned up old draft: {item}")
            
            print(f"✅ Cleaned up {cleaned_count} old draft folders")
            return cleaned_count
            
        except Exception as e:
            print(f"❌ Error cleaning up drafts: {e}")
            return 0
    
    @staticmethod
    def upload_multiple_files(files, study_id, subdirectory=None):
        """Upload multiple files using configured storage method."""
        if current_app.config.get('USE_LOCAL_STORAGE', False):
            return StorageManager._upload_multiple_local(files, study_id, subdirectory)
        else:
            return upload_multiple_files_to_azure(files)
    
    @staticmethod
    def _upload_multiple_local(files, study_id, subdirectory=None):
        """Upload multiple files to local storage."""
        results = []
        study_dir = StorageManager.create_study_directory(study_id)
        
        # Determine target directory
        if subdirectory:
            target_dir = os.path.join(study_dir, subdirectory)
            os.makedirs(target_dir, exist_ok=True)
        else:
            target_dir = study_dir
        
        for file in files:
            if file and file.filename and is_valid_image_file(file.filename):
                # Generate unique filename
                original_filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
                
                file_path = os.path.join(target_dir, unique_filename)
                file.save(file_path)
                
                # Return relative path for database storage
                relative_path = f"study_{study_id}"
                if subdirectory:
                    relative_path += f"/{subdirectory}"
                relative_path += f"/{unique_filename}"
                
                results.append({
                    'file_path': relative_path,
                    'url': StorageManager._get_local_url(relative_path),
                    'filename': unique_filename
                })
        
        return results
    
    @staticmethod
    def ensure_upload_directories():
        """Ensure all necessary upload directories exist."""
        if current_app.config.get('USE_LOCAL_STORAGE', False):
            # Create main local upload directory
            local_upload_dir = current_app.config['LOCAL_UPLOAD_FOLDER']
            os.makedirs(local_upload_dir, exist_ok=True)
            print(f"✅ Created local upload directory: {local_upload_dir}")
    
    @staticmethod
    def get_storage_info():
        """Get information about current storage configuration."""
        return {
            'use_local_storage': current_app.config.get('USE_LOCAL_STORAGE', False),
            'local_upload_folder': current_app.config.get('LOCAL_UPLOAD_FOLDER', 'local_uploads'),
            'azure_container': current_app.config.get('AZURE_CONTAINER_NAME', 'mf2')
        }
