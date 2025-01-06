from dotenv import load_dotenv
import os
import logging
import unittest 
from deepseek import DeepseekClient
from software_lifecycle import DevelopmentAgent, TestingAgent, DeploymentAgent, MonitoringAgent

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def initialize_deepseek():
    """Initialize DeepSeek client with proper API key format"""
    load_dotenv()
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
    
    # Format API key
    api_key = str(api_key).strip()
    if not api_key.startswith('sk-'):
        api_key = f"sk-{api_key}"
        
    # Initialize client
    try:
        client = DeepseekClient(api_key=api_key)
        logger.info("DeepSeek client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize DeepSeek client: {e}")
        raise

def main():
    # Load environment
    load_dotenv()
    api_key = os.getenv('DEEPSEEK_API_KEY')
    repo_url = os.getenv('repo_url')
    
    if not api_key or not repo_url:
        raise ValueError("Missing required environment variables")
        
    try:
        # Initialize agents
        dev_agent = DevelopmentAgent(api_key)
        test_agent = TestingAgent(api_key)
        deploy_agent = DeploymentAgent("deploy.ps1", api_key)
        monitor_agent = MonitoringAgent("http://localhost:3000/health", api_key)

        # Development Phase
        print("\n=== Development Phase ===")
        if not dev_agent.set_repository(repo_url):
            logger.error("Failed to setup repository")
            return

        # Generate API code
        code = dev_agent.generate_code(
            prompt="""
            Create a Node.js Express API with:
            - Health check endpoint
            - Basic error handling
            - Logging middleware
            """,
            project_type="node"
        )

        if not code:
            logger.error("Code generation failed")
            return

        print("\nGenerated Code:")
        print(code)

        # Code Review
        print("\n=== Code Review Phase ===")
        review = dev_agent.review_code(code)
        print("\nCode Review Results:")
        for suggestion in review:
            print(f"- {suggestion}")

        # Testing Phase
        print("\n=== Testing Phase ===")
        tests = test_agent.generate_tests(code)
        print("\nGenerated Tests:")
        print(tests)

        # Create a simple test case
        class SampleTest(unittest.TestCase):
            def test_example(self):
                self.assertTrue(True)
        
        test_agent.add_test(SampleTest('test_example'))
        test_agent.run_tests()

        # Deployment Phase
        print("\n=== Deployment Phase ===")
        config = {
            "port": 3000,
            "environment": "development",
            "healthCheckEndpoint": "/health"
        }
        if deploy_agent.validate_deployment(config):
            deploy_agent.deploy()

        # Monitoring Phase
        print("\n=== Monitoring Phase ===")
        monitor_agent.check_health()

    except Exception as e:
        logger.error(f"Application error: {e}")

if __name__ == "__main__":
    main()