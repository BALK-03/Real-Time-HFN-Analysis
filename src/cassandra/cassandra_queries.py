class CassandraQueries:
    CREATE_KEYSPACE = """
    CREATE KEYSPACE IF NOT EXISTS {keyspace}
    WITH replication = {{'class': 'SimpleStrategy', 'replication_factor' : '1'}};
    """

    CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS prediction_results (
        id UUID PRIMARY KEY,
        text TEXT,
        prediction TEXT
    );
    """

    INSERT_PREDICTION = "INSERT INTO prediction_results (id, text, prediction) VALUES (%s, %s, %s);"
