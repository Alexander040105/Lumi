import os

# Force in-memory quota and suppress Redis for route tests.
os.environ["USE_REDIS_CACHE"] = "false"
