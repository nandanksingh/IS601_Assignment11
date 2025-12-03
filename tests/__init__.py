# tests/__init__.py
import os

# Ensures all tests always have a database URL BEFORE any import happens
os.environ["TEST_DATABASE_URL"] = "sqlite:///./test.db"
os.environ["ENV"] = "testing"
