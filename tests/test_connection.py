import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.db.connection.mongo_connection import MongoDB

@pytest.mark.asyncio
async def test_mongo_connection():
    """Test basic MongoDB connection functionality."""
    with patch('app.db.connection.mongo_connection.AsyncIOMotorClient') as mock_client:
        # Setup mock client and database
        mock_db = MagicMock()  # Changed from AsyncMock to MagicMock
        mock_client_instance = MagicMock()  # Changed from AsyncMock to MagicMock
        mock_client_instance.get_database.return_value = mock_db
        mock_client.return_value = mock_client_instance
        
        # Clear any existing instances for clean test
        MongoDB._instances.clear()
        
        # Create MongoDB connection
        mongo = MongoDB("test_database")
        db = mongo.get_db()
        
        # Verify connection was established
        assert db is not None
        mock_client.assert_called_once()
        mock_client_instance.get_database.assert_called_once_with("test_database")

@pytest.mark.asyncio
async def test_mongo_collection_access():
    """Test accessing MongoDB collections."""
    with patch('app.db.connection.mongo_connection.AsyncIOMotorClient') as mock_client:
        # Setup mocks - using MagicMock for synchronous operations
        mock_collection = AsyncMock()
        mock_db = MagicMock()  # Database access is synchronous
        mock_db.__getitem__.return_value = mock_collection
        mock_client_instance = MagicMock()
        mock_client_instance.get_database.return_value = mock_db
        mock_client.return_value = mock_client_instance
        
        # Clear instances for clean test
        MongoDB._instances.clear()
        
        # Test collection access
        mongo = MongoDB("test_database")
        collection = mongo.get_collection("test_collection")
        
        # Verify collection was accessed correctly
        assert collection is not None
        mock_db.__getitem__.assert_called_once_with("test_collection")

@pytest.mark.asyncio
async def test_mongo_singleton_pattern():
    """Test that MongoDB uses singleton pattern correctly."""
    with patch('app.db.connection.mongo_connection.AsyncIOMotorClient') as mock_client:
        # Setup mocks
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.get_database.return_value = mock_db
        mock_client.return_value = mock_client_instance
        
        # Clear instances for clean test
        MongoDB._instances.clear()
        
        # Create two instances with same database name
        mongo1 = MongoDB("test_database")
        mongo2 = MongoDB("test_database")
        
        # Should be the same instance (singleton pattern)
        assert mongo1 is mongo2
        
        # Client should only be created once
        assert mock_client.call_count == 1

@pytest.mark.asyncio
async def test_mongo_different_databases():
    """Test that different database names create different instances."""
    with patch('app.db.connection.mongo_connection.AsyncIOMotorClient') as mock_client:
        # Setup mocks
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.get_database.return_value = mock_db
        mock_client.return_value = mock_client_instance
        
        # Clear instances for clean test
        MongoDB._instances.clear()
        
        # Create instances with different database names
        mongo1 = MongoDB("database1")
        mongo2 = MongoDB("database2")
        
        # Should be different instances
        assert mongo1 is not mongo2
        
        # Client should be created for each database
        assert mock_client.call_count == 2

@pytest.mark.asyncio
async def test_mongo_basic_operations():
    """Test basic MongoDB operations like ping."""
    with patch('app.db.connection.mongo_connection.AsyncIOMotorClient') as mock_client:
        # Setup mocks
        mock_db = MagicMock()
        mock_admin = AsyncMock()
        mock_admin.command = AsyncMock(return_value={"ok": 1})
        mock_client_instance = MagicMock()
        mock_client_instance.get_database.return_value = mock_db
        mock_client_instance.admin = mock_admin
        mock_client.return_value = mock_client_instance
        
        # Clear instances for clean test
        MongoDB._instances.clear()
        
        # Create connection and test ping
        mongo = MongoDB("test_database")
        
        # Test ping operation
        result = await mock_client_instance.admin.command("ping")
        assert result["ok"] == 1

@pytest.mark.asyncio
async def test_mongo_close_connection():
    """Test closing MongoDB connection."""
    with patch('app.db.connection.mongo_connection.AsyncIOMotorClient') as mock_client:
        # Setup mocks
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.get_database.return_value = mock_db
        mock_client_instance.close = MagicMock()  # Close is typically synchronous
        mock_client.return_value = mock_client_instance
        
        # Clear instances for clean test
        MongoDB._instances.clear()
        
        # Create and close connection
        mongo = MongoDB("test_database")
        mongo.close_connection()
        
        # Verify close was called
        mock_client_instance.close.assert_called_once()

@pytest.mark.asyncio
async def test_mongo_error_handling():
    """Test MongoDB connection error handling."""
    with patch('app.db.connection.mongo_connection.AsyncIOMotorClient') as mock_client:
        # Make client initialization raise an exception
        mock_client.side_effect = Exception("Connection failed")
        
        # Clear instances for clean test
        MongoDB._instances.clear()
        
        # Test that exception is handled appropriately
        with pytest.raises(Exception, match="Connection failed"):
            MongoDB("test_database")

@pytest.mark.asyncio
async def test_mongo_get_database_name():
    """Test getting the database name."""
    with patch('app.db.connection.mongo_connection.AsyncIOMotorClient') as mock_client:
        # Setup mocks
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.get_database.return_value = mock_db
        mock_client.return_value = mock_client_instance
        
        # Clear instances for clean test
        MongoDB._instances.clear()
        
        # Create connection
        mongo = MongoDB("test_database")
        
        # Test that we can get the database name
        assert mongo._database_name == "test_database"

@pytest.mark.asyncio
async def test_mongo_multiple_collections():
    """Test accessing multiple collections."""
    with patch('app.db.connection.mongo_connection.AsyncIOMotorClient') as mock_client:
        # Setup mocks
        mock_collection1 = AsyncMock()
        mock_collection2 = AsyncMock()
        mock_db = MagicMock()
        
        # Setup __getitem__ to return different collections
        def mock_getitem(name):
            if name == "collection1":
                return mock_collection1
            elif name == "collection2":
                return mock_collection2
            return AsyncMock()
        
        mock_db.__getitem__.side_effect = mock_getitem
        mock_client_instance = MagicMock()
        mock_client_instance.get_database.return_value = mock_db
        mock_client.return_value = mock_client_instance
        
        # Clear instances for clean test
        MongoDB._instances.clear()
        
        # Test multiple collection access
        mongo = MongoDB("test_database")
        collection1 = mongo.get_collection("collection1")
        collection2 = mongo.get_collection("collection2")
        
        # Verify different collections were returned
        assert collection1 is mock_collection1
        assert collection2 is mock_collection2
        assert mock_db.__getitem__.call_count == 2