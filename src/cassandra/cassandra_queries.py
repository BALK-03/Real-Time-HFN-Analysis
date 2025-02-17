class CassandraQueries:
    CREATE_KEYSPACE = """
    CREATE KEYSPACE IF NOT EXISTS {keyspace}
    WITH replication = {{'class': 'SimpleStrategy', 'replication_factor' : '1'}};
    """

    CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS prediction_results (
        id UUID,
        text TEXT,
        prediction TEXT,
        subreddit TEXT,
        timestamp TIMESTAMP,
        PRIMARY KEY ((prediction), timestamp, id)
    );
    """

    INSERT_PREDICTION = "INSERT INTO prediction_results (id, text, prediction, subreddit, timestamp) VALUES (%s, %s, %s, %s, %s);"
