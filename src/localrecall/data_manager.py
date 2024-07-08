import os
import json
from .utils import ensure_dir
import sqlite3
import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Optional
import chromadb
from .embedding_processor import EmbeddingStrategy

class DataManager:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.join(os.getcwd(), 'data')
        ensure_dir(self.base_dir)
        self.db_path = os.path.join(self.base_dir, 'activities.db')
        self._create_db()

    def _create_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                timestamp TEXT PRIMARY KEY,
                screenshot_path TEXT,
                active_window TEXT,
                user_apps TEXT,
                analysis TEXT,
                processed INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    def save_activity(self, screenshot_path, active_window, user_apps):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO activities (created_at, timestamp, screenshot_path, active_window, user_apps, processed)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now(timezone.utc).astimezone().isoformat(), timestamp, screenshot_path, json.dumps(active_window), json.dumps(user_apps), 0))
        conn.commit()
        conn.close()

    def get_unprocessed_activities(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM activities WHERE processed = 0')
        activities = [dict(zip(['created_at', 'timestamp', 'screenshot', 'active_window', 'user_apps', 'analysis', 'processed'], row))
                      for row in cursor.fetchall()]
        conn.close()
        return activities

    def update_activity(self, timestamp, activity_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE activities
            SET active_window = ?, user_apps = ?, analysis = ?
            WHERE timestamp = ?
        ''', (json.dumps(activity_data['active_window']),
              json.dumps(activity_data['user_apps']),
              activity_data['analysis'],
              timestamp))
        conn.commit()
        conn.close()

    def mark_activity_as_processed(self, timestamp):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE activities SET processed = 1 WHERE timestamp = ?', (timestamp,))
        conn.commit()
        conn.close()

class VectorDataManager:
    def __init__(self, embedding_strategy: EmbeddingStrategy, base_dir=None):
        self.base_dir = base_dir or os.path.join(os.getcwd(), 'vector_data')
        os.makedirs(self.base_dir, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=self.base_dir)
        self.collection = self.client.get_or_create_collection(name="activities", metadata={"hnsw:space": "cosine"})
        
        self.embedding_strategy = embedding_strategy

    def add_activity(self, timestamp: str, created_at: str, screenshot_path: str, active_window: Dict, analysis: str):
        metadata = {
            "created_at": datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%f%z").timestamp(),
            "screenshot_path": screenshot_path,
            "active_window": json.dumps(active_window),
        }
        
        embedding = self.embedding_strategy.create_embedding(analysis)
        
        self.collection.add(
            ids=[timestamp],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[analysis]
        )

    def search_activities(self, query: str, n_results: int = 5) -> List[Dict]:
        query_embedding = self.embedding_strategy.create_embedding_retrieval(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        activities = []
        for i in range(len(results['ids'][0])):
            activity = {
                "timestamp": results['ids'][0][i],
                "analysis": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i]
            }
            activities.append(activity)
        
        return activities

    def get_all_activities(self) -> List[Dict]:
        results = self.collection.get()
        
        activities = []
        for i in range(len(results['ids'])):
            activity = {
                "timestamp": results['ids'][i],
                "analysis": results['documents'][i],
                "metadata": results['metadatas'][i]
            }
            activities.append(activity)
        
        return activities

    def search_activities_with_filters(self, 
                                       query: str, 
                                       start_time: Optional[datetime] = None, 
                                       end_time: Optional[datetime] = None, 
                                       n_results: int = 5) -> List[Dict]:
        query_embedding = self.embedding_strategy.create_embedding(query)
        
        where_clause = {}
        
        # Add time filter if start_time and end_time are provided
        if start_time and end_time:
            where_clause["$and"] = [
                {"created_at": {"$gte": start_time}},
                {"created_at": {"$lte": end_time}}
            ]
                
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause if where_clause else None
        )
        
        activities = []
        for i in range(len(results['ids'][0])):
            activity = {
                "timestamp": results['ids'][0][i],
                "analysis": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i],
            }
            activities.append(activity)
        
        return activities