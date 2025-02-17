import os, sys
from cassandra.cluster import Cluster
import uuid
from cassandra.auth import PlainTextAuthProvider
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.cassandra.cassandra_queries import CassandraQueries


class CassandraManager:
    def __init__(self, host: str, keyspace: str):
        self.host = host
        self.keyspace = keyspace
        self.cluster = None
        self.session = None

    def connect(self):
        auth_provider = PlainTextAuthProvider("admin", "admin")
        self.cluster = Cluster([self.host], auth_provider=auth_provider)
        self.session = self.cluster.connect()
                
        self.session.execute(CassandraQueries.CREATE_KEYSPACE.format(keyspace=self.keyspace))
        self.session.set_keyspace(self.keyspace)

        self.session.execute(CassandraQueries.CREATE_TABLE)

    def insert_prediction(self, text: str, prediction: str, subreddit: str):
        self.session.execute(CassandraQueries.INSERT_PREDICTION, (uuid.uuid4(), text, prediction, subreddit, datetime.now()))

    def close(self):
        if self.cluster:
            self.cluster.shutdown()
