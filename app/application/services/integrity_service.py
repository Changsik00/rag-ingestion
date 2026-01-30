from dataclasses import dataclass
from typing import Any


@dataclass
class DriftReport:
    total_primary: int
    total_target: int
    missing_count: int
    missing_ids: set[str]
    orphan_count: int
    orphan_ids: set[str]


class IntegrityService:
    """Application Service: 데이터 무결성 검증 및 동기화"""

    def __init__(self, primary_repo: Any, target_repo: Any):
        """
        Args:
            primary_repo: Source of truth (Neo4j)
            target_repo: Target index (Chroma)
        """
        self.primary_repo = primary_repo
        self.target_repo = target_repo

    def get_drift_report(self) -> dict[str, Any]:
        primary_ids = self.primary_repo.get_all_chunk_ids()
        target_ids = self.target_repo.get_all_chunk_ids()

        missing_ids = primary_ids - target_ids
        orphan_ids = target_ids - primary_ids

        return {
            "total_primary": len(primary_ids),
            "total_target": len(target_ids),
            "missing_count": len(missing_ids),
            "missing_ids": missing_ids,
            "orphan_count": len(orphan_ids),
            "orphan_ids": orphan_ids,
            "drift_ratio": (len(missing_ids) / len(primary_ids)) if primary_ids else 0,
        }

    def get_document_drift_report(self) -> list[dict[str, Any]]:
        """문서별 인덱싱 현황 리포트 생성 (성능 최적화 및 안정화 버전)"""
        # 1. 모든 인덱싱된 청크 ID 확보 (Chroma)
        target_chunks_ids = self.target_repo.get_all_chunk_ids()

        # 2. 모든 청크의 ID와 부모 ID 확보 (Neo4j - content 제외)
        all_primary_chunk_info = self.primary_repo.get_all_chunk_metadata()

        chunk_groups = {}
        for chunk in all_primary_chunk_info:
            pid = chunk.get("parent_id")
            if pid not in chunk_groups:
                chunk_groups[pid] = []
            chunk_groups[pid].append(str(chunk.get("id")))

        # 3. 문서별 통계 일괄 조회 (Neo4j)
        doc_stats = self.primary_repo.get_document_stats()

        report = []
        for stat in doc_stats:
            doc_id = str(stat["id"])
            total_chunks = stat["chunk_count"]
            if total_chunks == 0:
                continue

            # 메모리에 그룹화된 정보에서 가져옴
            chunks = chunk_groups.get(doc_id, [])
            indexed_count = sum(1 for cid in chunks if cid in target_chunks_ids)

            # 보정 필요성 판단
            has_title = stat["title"] not in ["Untitled", "", None]

            if total_chunks > indexed_count:
                status = "Missing" if indexed_count == 0 else "Partial"
            elif not has_title:
                status = "Missing Title"
            else:
                status = "In Sync"

            # 샘플 추출 (오직 보정이나 리포트가 필요한 경우에만 추가 정보 조회 고려할 수 있으나 생략 가능)
            # 여기서는 status != 'In Sync'인 경우에만 나중에 UI에서 상세 조회하도록 유도

            report.append(
                {
                    "id": doc_id,
                    "title": stat["title"],
                    "url": stat["url"],
                    "total_chunks": total_chunks,
                    "target_chunks": indexed_count,
                    "drift_ratio": (total_chunks - indexed_count) / total_chunks if total_chunks > 0 else 0,
                    "status": status,
                    "missing_sample": "",  # UI에서 필요 시 개별 조회
                }
            )

        return report

    def get_missing_chunk_sample(self, doc_id: str) -> str:
        """특정 문서의 누락된 청크 샘플 하나를 가져옵니다."""
        target_ids = self.target_repo.get_all_chunk_ids()
        chunks = self.primary_repo.get_chunks(doc_id)
        for c in chunks:
            if str(c.id) not in target_ids:
                return c.content[:300] + "..."
        return ""

    def propagate_document_metadata(self, doc_id: str) -> bool:
        """상위 문서의 제목(Title) 등을 하위 청크들로 전파"""
        doc = self.primary_repo.get(doc_id)
        if not doc:
            return False

        title = doc.metadata.get("title")
        if not title or title == "Untitled":
            # URL 기반 Fallback 시도 (나중에 고도화)
            source = doc.metadata.get("source_url") or doc.metadata.get("source", "")
            if source:
                # URL에서 파일명 추출 시도 (trailing slash 처리 및 디코딩)
                from urllib.parse import unquote

                path = source.strip("/").split("/")[-1]
                new_title = unquote(path.split("?")[0]) or "Untitled"

                # 'Untitled'가 나오면 상위 경로 시도
                if new_title == "Untitled" and len(source.strip("/").split("/")) > 1:
                    new_title = source.strip("/").split("/")[-2]

                doc.metadata["title"] = new_title
                self.primary_repo.save(doc)
                title = new_title
            else:
                return False

        chunks = self.primary_repo.get_chunks(doc_id)
        for chunk in chunks:
            chunk.metadata["title"] = title

        # Primary Repo에 업데이트 (Neo4j MERGE 지원)
        self.primary_repo.save_with_chunks(doc, chunks)
        return True

    def sync_document(self, doc_id: str) -> dict[str, Any]:
        """특정 문서의 청크들을 ChromaDB로 강제 동기화"""
        doc = self.primary_repo.get(doc_id)
        if not doc:
            return {"success": False, "error": "Document not found"}

        chunks = self.primary_repo.get_chunks(doc_id)
        if not chunks:
            return {"success": False, "error": "No chunks found"}

        try:
            # 먼저 메타데이터 보정 (Propagate)
            self.propagate_document_metadata(doc_id)
            # 최신 청크 다시 로드
            updated_chunks = self.primary_repo.get_chunks(doc_id)

            # Target Repo (Chroma)에 저장
            self.target_repo.save_chunks(updated_chunks)
            return {"success": True, "count": len(updated_chunks)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_cleaned_context(self, doc_id: str) -> str:
        """LLM에게 전달될 정제된 컨텍스트 미리보기"""
        from app.infrastructure.rag.nodes import RAGNodes

        chunks = self.primary_repo.get_chunks(doc_id)
        if not chunks:
            return "No chunks found."

        # RAGNodes의 클리닝 로직 재사용 (Dependency injection 없이 정적 메서드처럼 활용 위해 임시 인스턴스)
        nodes = RAGNodes(None, None, None, None, None, None)
        cleaned_parts = []
        for c in chunks:
            cleaned_parts.append(nodes._clean_context_noise(c.content))

        return "\n\n---\n\n".join(cleaned_parts)

    async def enrich_knowledge_graph(self, doc_id: str, extractor_service: Any) -> dict[str, Any]:
        """특정 문서에 대해 의미 추출을 재실행하여 지식 그래프 보충"""
        doc = self.primary_repo.get(doc_id)
        if not doc:
            return {"success": False, "error": "Document not found"}

        try:
            # 1. 의미 추출 재실행
            semantic_data = await extractor_service.extract(doc.content, thread_id=f"enrich_{doc_id}")
            if not semantic_data:
                return {"success": False, "error": "Failed to extract semantic data"}

            # 2. 메타데이터 업데이트
            doc.metadata["semantic_data"] = semantic_data.model_dump()
            self.primary_repo.save(doc)

            # 3. 그래프 빌드 (IngestionService 로직과 동일하게 수행하나 여기선 직접 구성)
            # Entity 및 Relationship 저장
            if semantic_data.entities:
                for entity_type, names in semantic_data.entities.items():
                    for name in names:
                        self.primary_repo.graph.save_entity(name, entity_type)
                        self.primary_repo.graph.create_mention_relationship(str(doc_id), name)

            if hasattr(semantic_data, "relationships") and semantic_data.relationships:
                for rel in semantic_data.relationships:
                    self.primary_repo.graph.create_entity_relationship(
                        source_name=rel.source, relationship_type=rel.relationship, target_name=rel.target
                    )

            return {
                "success": True,
                "entities": len(semantic_data.entities or {}),
                "rels": len(semantic_data.relationships or []),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def sync_all(self, batch_size: int = 20, callback: Any = None):
        """누락된 데이터(Chunk) 및 결함 있는 메타데이터(Title)를 일괄 복구"""
        reports = self.get_document_drift_report()
        target_docs = [r for r in reports if r["status"] != "In Sync"]

        if not target_docs:
            if callback:
                callback(1.0, "Already in sync")
            return

        total = len(target_docs)
        for i, doc_report in enumerate(target_docs):
            doc_id = doc_report["id"]
            # sync_document는 metadata 보정과 chunk 저장을 모두 수행함
            self.sync_document(doc_id)

            if callback:
                progress = min((i + 1) / total, 1.0)
                callback(progress, f"Fixed {i + 1} / {total} documents ('{doc_report['title']}')")
