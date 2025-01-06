import os
import subprocess
import psutil
import time
import logging
from pathlib import Path
from git import Repo, GitCommandError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def cleanup_and_clone_repository(repo_url: str, branch: str = "main") -> bool:
    """Clean existing repo and clone fresh copy"""
    repo_path = Path("repository").absolute()
    
    # Step 1: Force cleanup
    try:
        if repo_path.exists():
            # Kill processes using directory
            for proc in psutil.process_iter(['pid', 'name', 'open_files']):
                try:
                    if any(str(repo_path) in str(f.path) for f in proc.open_files()):
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            time.sleep(1)
            
            # Force remove directory
            subprocess.run(
                ['cmd', '/c', f'rd /s /q "{repo_path}"'],
                shell=True,
                check=True
            )
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return False
        
    # Step 2: Clone repository
    try:
        logger.info(f"Cloning repository: {repo_url}")
        repo = Repo.clone_from(repo_url, repo_path)
        repo.git.checkout(branch)
        return True
        
    except GitCommandError as e:
        logger.error(f"Git operation failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Clone failed: {e}")
        return False

if __name__ == "__main__":
    repo_url = "https://github.com/taoufikmohamed/demo.git"
    if cleanup_and_clone_repository(repo_url):
        print("Repository setup successful")
    else:
        print("Repository setup failed")