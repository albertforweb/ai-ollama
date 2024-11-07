import queue 
from qdrant_client import QdrantClient



# import numpy as np
from qdrant_client.models import PointStruct
from qdrant_client.models import VectorParams, Distance

class QdrantAgent:
    def __init__(self, dataQueue:queue.Queue, config: dict):
        self.dataQueue = dataQueue
        self.collection = config['qdrant_collection']
        self.client = QdrantClient(config['qdrant_url'])

    def create_collection(self):
      if not self.client.collection_exists(self.collection):
        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(size=100, distance=Distance.COSINE),
        )
        

    def store(self, data: dict, vectors: list):
      # vectors = np.random.rand(100, 100)
      self.client.upsert(
        collection_name=self.collection,
        points=[
            PointStruct(
                  id=idx,
                  vector=vector.tolist(),
                  payload=data
                  # payload={"color": "red", "rand_number": idx % 10}
            )
            for idx, vector in enumerate(vectors)
        ]
      )
    
    def search(self, query_vector: list):
        # Search for similar vectors

        # query_vector = np.random.rand(100)
        hits = self.client.search(
          collection_name="my_collection",
          query_vector=query_vector,
          limit=5  # Return 5 closest points
        )
        # Search for similar vectors with filtering condition

        # from qdrant_client.models import Filter, FieldCondition, Range

        # hits = client.search(
        #   collection_name="my_collection",
        #   query_vector=query_vector,
        #   query_filter=Filter(
        #       must=[  # These conditions are required for search results
        #             FieldCondition(
        #               key='rand_number',  # Condition based on values of `rand_number` field.
        #               range=Range(
        #                   gte=3  # Select only those results where `rand_number` >= 3
        #               )
        #             )
        #       ]
        #   ),
        #   limit=5  # Return 5 closest points
        # )
        return hits