import subprocess
import os
import unittest
import requests
import time
from typing import List, Dict, Optional
from dotenv import load_dotenv
from deepseek import DeepseekClient as DeepseekAI
import logging
from git import Repo, GitCommandError
from pathlib import Path
import psutil
import shutil
from repository_manager import RepositoryManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DevelopmentAgent:
    def __init__(self, api_key: str = None):
        # Initialize with API key and load config
        api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.repo_url = os.getenv('repo_url')
        
        if not api_key:
            raise ValueError("DeepSeek API key is required")
            
        # Format API key
        api_key = str(api_key).strip()
        if api_key.startswith('Bearer '):
            api_key = api_key[7:]
        if api_key.startswith('sk-'):
            api_key = api_key[3:]
            
        # Initialize services
        self.llm = DeepseekAI(api_key=f"sk-{api_key}")
        self.repo_manager = RepositoryManager()
        
        logger.debug(f"Development agent initialized with API key: sk-{api_key[:5]}...")

    def set_repository(self, repo_url: str = None) -> bool:
        """Setup repository with provided URL or from environment"""
        try:
            # Use provided URL or fallback to env
            self.repo_url = repo_url or self.repo_url
            if not self.repo_url:
                raise ValueError("Repository URL not provided")
                
            return self.repo_manager.initialize_repository(self.repo_url)
            
        except Exception as e:
            logger.error(f"Repository setup failed: {e}")
            return False

    def _safe_cleanup(self) -> bool:
        """Safely remove repository directory"""
        if not self.repo_path.exists():
            return True

        for attempt in range(self.max_retries):
            try:
                if self.repo_path.exists():
                    shutil.rmtree(self.repo_path, ignore_errors=True)
                time.sleep(self.retry_delay)
                return True
            except Exception as e:
                logger.warning(f"Cleanup attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    return False
                time.sleep(self.retry_delay)
        return False

    def _kill_processes_using_path(self, path: Path) -> None:
        """Kill all processes accessing the given path."""
        for proc in psutil.process_iter(['pid', 'name', 'open_files']):
            try:
                for file in proc.open_files():
                    if str(path) in str(file.path):
                        proc.kill()
                        time.sleep(0.5)  # Allow process to terminate
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def _force_remove_directory(self, path: Path) -> bool:
        """Force remove directory with process termination."""
        if not path.exists():
            return True

        try:
            # First try normal removal
            shutil.rmtree(path, ignore_errors=True)
            time.sleep(1)
            
            if path.exists():
                # Kill processes if directory still exists
                self._kill_processes_using_path(path)
                time.sleep(1)
                
                # Force remove with system command
                subprocess.run(['cmd', '/c', f'rmdir /S /Q "{path}"'], check=True)
                time.sleep(1)
                
            return not path.exists()
            
        except Exception as e:
            logger.error(f"Failed to remove directory: {e}")
            return False

    def generate_code(self, prompt: str, project_type: str = "node") -> Optional[str]:
        """Generate code using Deepseek AI with structured prompts.
        
        Args:
            prompt: Base prompt for code generation
            project_type: Type of project (node, python, etc.)
        Returns:
            str: Generated code or None if failed
        """
        try:
            # Enhance prompt with structure and best practices
            enhanced_prompt = f"""
            Create production-ready code following best practices:
            - Include error handling
            - Add input validation
            - Use proper logging
            - Follow {project_type} conventions
            - Add comments and documentation
            
            Requirements:
            {prompt}
            """
            
            response = self.llm.generate(
                prompt=enhanced_prompt,
                model="deepseek-chat",
                max_tokens=2000
            )
            
            if not response or not response.text:
                logger.error("Empty response from AI")
                return None
                
            return response.text
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return None

    def review_code(self, code: str) -> List[str]:
        """Review code using comprehensive criteria.
        
        Args:
            code: Source code to review
        Returns:
            List[str]: List of review comments
        """
        try:
            review_prompt = f"""
            Review this code for:
            1. Code quality and best practices
            2. Security vulnerabilities
            3. Performance considerations
            4. Error handling
            5. Input validation
            6. Documentation
            7. Testing coverage
            
            Code to review:
            {code}
            """
            
            response = self.llm.generate(prompt=review_prompt)
            if not response or not response.text:
                return ["Code review failed: No response from AI"]
                
            # Filter empty lines and format comments
            return [
                comment.strip() 
                for comment in response.text.split('\n') 
                if comment.strip()
            ]
            
        except Exception as e:
            logger.error(f"Code review failed: {e}")
            return [f"Code review error: {str(e)}"]

class TestingAgent:
    def __init__(self, api_key: str = os.getenv('DEEPSEEK_API_KEY')):
        self.llm = DeepseekAI(api_key=api_key)
        self.test_suite = unittest.TestSuite()

    def generate_tests(self, code: str) -> Optional[str]:
        try:
            prompt = f"Generate unit tests for:\n{code}"
            response = self.llm.generate(prompt=prompt)
            return response.text if response else None
        except Exception as e:
            logger.error(f"Test generation failed: {e}")
            return None

    def add_test(self, test_case):
        self.test_suite.addTest(test_case)

    def run_tests(self) -> bool:
        runner = unittest.TextTestRunner()
        result = runner.run(self.test_suite)
        return result.wasSuccessful()

class DeploymentAgent:
    def __init__(self, script_path: str, api_key: str = os.getenv('DEEPSEEK_API_KEY')):
        self.llm = DeepseekAI(api_key=api_key)
        self.script_path = script_path

    def validate_deployment(self, config: Dict) -> bool:
        try:
            prompt = f"Validate deployment config:\n{config}"
            response = self.llm.generate(prompt=prompt)
            return "valid" in response.text.lower() if response else False
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False

    def deploy(self) -> bool:
        try:
            script_path = Path(self.script_path).resolve()
            result = subprocess.run(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-File', str(script_path)],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return False

class MonitoringAgent:
    def __init__(self, health_url: str, api_key: str = os.getenv('DEEPSEEK_API_KEY')):
        self.llm = DeepseekAI(api_key=api_key)
        self.health_url = health_url
        self.max_retries = 3
        self.retry_delay = 2

    def check_health(self) -> bool:
        for attempt in range(self.max_retries):
            try:
                response = requests.get(self.health_url)
                if response.status_code == 200:
                    return True
                time.sleep(self.retry_delay)
            except requests.RequestException as e:
                logger.error(f"Health check failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        return False