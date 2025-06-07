import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from mock_github import MockGitHubAPI
    logger.info("Successfully imported MockGitHubAPI")
except ImportError as e:
    logger.error("Failed to import MockGitHubAPI: {}".format(e))

try:
    from resources import GitHubAPIResource
    
    # Set mock mode
    os.environ['GITHUB_USE_MOCK'] = 'true'
    
    # Create resource
    github = GitHubAPIResource()
    
    # Check if mock was initialized
    if github._mock_api is not None:
        logger.info("Mock API was successfully initialized")
    else:
        logger.error("Mock API was not initialized")
        
except Exception as e:
    logger.error("Error testing GitHubAPIResource: {}".format(e))

if __name__ == "__main__":
    logger.info("Import test complete") 
