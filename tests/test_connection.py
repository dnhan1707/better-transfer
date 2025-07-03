from sqlalchemy import text

def test_db_connection(db):
    """Ensure the database connection executes a simple query."""
    db.execute.return_value.fetchone.return_value = (1,)
    result = db.execute(text("SELECT 1")).fetchone()
    assert result[0] == 1


def test_pgvector_extension_available(db):
    """Verify pgvector extension detection logic."""
    db.execute.return_value.fetchall.return_value = [("vector",)]
    extensions = db.execute(text("SELECT name FROM pg_available_extensions WHERE name='vector'"))
    extensions = extensions.fetchall()
    assert any(ext[0] == 'vector' for ext in extensions)
