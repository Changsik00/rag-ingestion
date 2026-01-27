import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from app.core.config import Settings
from app.domain.entities.chunk import Chunk
from app.infrastructure.storage.chroma import ChromaStorage


class TestRobustIngestion(unittest.TestCase):
    def setUp(self):
        # Mock Settings to enforce batch size of 20
        self.mock_settings = MagicMock(spec=Settings)
        # Assuming get_settings returns an instance with CHROMA_BATCH_SIZE
        # We need to patch where ChromaStorage gets its settings.
        # However, ChromaStorage calls get_settings() in __init__.
        # We can patch 'app.infrastructure.storage.chroma.get_settings'
        pass

    def test_save_chunks_batching(self):
        """Verify save_chunks splits 50 chunks into batches of 20 (3 calls)"""

        # 1. Setup Mock
        with unittest.mock.patch("app.infrastructure.storage.chroma.get_settings") as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.CHROMA_HOST = "localhost"
            mock_settings.CHROMA_PORT = 8000
            mock_settings.CHROMA_BATCH_SIZE = 20
            mock_settings.GEMINI_API_KEY = "fake_key"
            mock_get_settings.return_value = mock_settings

            with unittest.mock.patch("chromadb.HttpClient") as mock_client_cls:
                mock_client = MagicMock()
                mock_client_cls.return_value = mock_client

                mock_collection = MagicMock()
                mock_client.get_or_create_collection.return_value = mock_collection

                # Instantiate Storage
                storage = ChromaStorage()

                # Mock the collection on the instance just to be sure
                storage.collection = mock_collection

                # 2. Create Dummy Data (50 chunks)
                chunks = []
                for i in range(50):
                    chunks.append(
                        Chunk(
                            id=uuid4(),
                            content=f"Chunk content {i}",
                            metadata={"source": "test", "index": i},
                            parent_id=uuid4(),
                            index=i,
                        )
                    )

                # 3. Execute
                storage.save_chunks(chunks)

                # 4. Verification
                # Expected: 3 calls.
                # Call 1: 20 items
                # Call 2: 20 items
                # Call 3: 10 items
                self.assertEqual(mock_collection.add.call_count, 3)

                # Inspect calls
                calls = mock_collection.add.call_args_list

                # Batch 1
                args1, kwargs1 = calls[0]
                self.assertEqual(len(kwargs1["ids"]), 20)

                # Batch 2
                args2, kwargs2 = calls[1]
                self.assertEqual(len(kwargs2["ids"]), 20)

                # Batch 3
                args3, kwargs3 = calls[2]
                self.assertEqual(len(kwargs3["ids"]), 10)

                print("\n✅ Verification Passed: 50 chunks were saved in 3 batches (20, 20, 10).")


if __name__ == "__main__":
    unittest.main()
