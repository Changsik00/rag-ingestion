import asyncio
import os
import sys

from tqdm import tqdm

# Add project root to path
sys.path.append(os.getcwd())

from app.domain.services.storage_integrity_service import StorageIntegrityService
from app.infrastructure.storage.chroma import ChromaVectorRepository
from app.infrastructure.storage.neo4j_document_repository import Neo4jDocumentRepository
from app.interfaces.api.dependencies import get_neo4j_driver


async def main():
    print("--- 🔍 Storage Integrity Sync Starting ---")

    # 1. Initialize dependencies
    driver = get_neo4j_driver()
    primary_repo = Neo4jDocumentRepository(driver)
    target_repo = ChromaVectorRepository()

    service = StorageIntegrityService(primary_repo, target_repo)

    # 2. Get initial report
    print("Checking current status...")
    drift = service.get_drift_report()

    print(f"Neo4j total: {drift['total_primary']}")
    print(f"Chroma total: {drift['total_target']}")
    print(f"Missing items: {drift['missing_count']}")

    if drift["missing_count"] == 0:
        print("✅ Everything is in sync!")
        driver.close()
        return

    # 3. Synchronize with tqdm progress bar
    pbar = tqdm(total=drift["missing_count"])

    def progress_callback(progress, message):
        # We need incremental update for pbar
        # But our service sends absolute progress
        # Let's just update based on message count if we can
        pass

    # Simple loop for script (instead of callback for simplicity in CLI)
    batch_size = 20
    missing_ids = list(drift["missing_ids"])

    for i in range(0, len(missing_ids), batch_size):
        batch = missing_ids[i : i + batch_size]
        chunks = primary_repo.get_chunks_by_ids(batch)
        if chunks:
            target_repo.save_chunks(chunks)
        pbar.update(len(batch))

    pbar.close()
    print("--- 🎉 Recovery Completed ---")
    driver.close()


if __name__ == "__main__":
    asyncio.run(main())
