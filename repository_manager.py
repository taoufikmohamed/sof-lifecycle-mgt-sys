import os
import subprocess
import time
import logging
from pathlib import Path
from git import Repo, GitCommandError
from typing import Optional

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class RepositoryManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.repo: Optional[Repo] = None
            cls._instance.repo_path = Path("repository").absolute()
        return cls._instance

    def force_cleanup(self) -> bool:
        """Force cleanup repository directory"""
        try:
            # Kill git processes
            subprocess.run('taskkill /F /IM git.exe 2>nul', shell=True)
            time.sleep(1)
            
            if self.repo_path.exists():
                # Remove read-only attributes
                subprocess.run(f'attrib -r -s -h "{self.repo_path}\\*.*" /s /d', shell=True)
                time.sleep(1)
                # Force remove directory
                subprocess.run(f'rmdir /s /q "{self.repo_path}"', shell=True, check=True)
                time.sleep(1)
            
            return not self.repo_path.exists()
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False

    def initialize_repository(self, repo_url: str) -> bool:
        """Initialize Git repository"""
        try:
            if not self.force_cleanup():
                return False
                
            logger.info(f"Cloning {repo_url}")
            self.repo = Repo.clone_from(repo_url, self.repo_path)
            
            # Setup branch
            branches = [ref.name for ref in self.repo.refs]
            if 'main' in branches:
                self.repo.git.checkout('main')
            elif 'master' in branches:
                self.repo.git.checkout('master')
            
            return True
            
        except GitCommandError as e:
            logger.error(f"Git operation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Repository initialization failed: {e}")
            return False

    def get_repository(self) -> Optional[Repo]:
        """Get repository instance"""
        return self.repo

# Make class available for import
__all__ = ['RepositoryManager']

if __name__ == "__main__":
    repo_url = os.getenv('repo_url')
    manager = RepositoryManager()
    if manager.initialize_repository(repo_url):
        print("Repository setup successful")
    else:
        print("Repository setup failed")