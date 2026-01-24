from typing import Any, Dict, List, Set
from dataclasses import dataclass
from app.domain.interfaces.document_repository import DocumentRepository

@dataclass
class DriftReport:
    total_primary: int
    total_target: int
    missing_count: int
    missing_ids: Set[str]
    orphan_count: int
    orphan_ids: Set[str]

class StorageIntegrityService:
    def __init__(self, primary_repo: Any, target_repo: Any):
        """
        Args:
            primary_repo: Source of truth (Neo4j)
            target_repo: Target index (Chroma)
        """
        self.primary_repo = primary_repo
        self.target_repo = target_repo

    def get_drift_report(self) -> Dict[str, Any]:
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
            "drift_ratio": (len(missing_ids) / len(primary_ids)) if primary_ids else 0
        }

    def get_document_drift_report(self) -> List[Dict[str, Any]]:
        """문서별 인덱싱 현황 리포트 생성 (N+1 Query 최적화 버전)"""
        # 1. 모든 인덱싱된 청크 ID 확보 (Chroma)
        target_chunks_ids = self.target_repo.get_all_chunk_ids()
        
        # 2. 모든 청크의 ID와 부모 ID를 한 번에 확보 (Neo4j)
        # 이 작업은 get_chunks_by_ids 처럼 bulk 조회가 필요하거나 
        # 레포지토리에 그룹화된 조회를 요청해야 함. 
        # 여기서는 primary_repo에 새로운 bulk 메서드가 없으므로 
        # 모든 청크 정보를 가져와 메모리에서 그룹화 처리.
        all_primary_chunk_info = self.primary_repo.get_all_chunk_metadata() # id, parent_id, content(샘플용) 필요
        
        chunk_groups = {}
        for chunk in all_primary_chunk_info:
            pid = chunk.get("parent_id")
            if pid not in chunk_groups:
                chunk_groups[pid] = []
            chunk_groups[pid].append(chunk)

        # 3. 문서별 통계 일괄 조회 (Neo4j)
        doc_stats = self.primary_repo.get_document_stats()
        
        report = []
        for stat in doc_stats:
            doc_id = stat["id"]
            total_chunks = stat["chunk_count"]
            if total_chunks == 0:
                continue
                
            # 메모리에 그룹화된 정보에서 가져옴
            chunks = chunk_groups.get(doc_id, [])
            indexed_count = sum(1 for c in chunks if str(c["id"]) in target_chunks_ids)
            
            # 샘플 추출
            missing_sample = ""
            if indexed_count < total_chunks:
                for c in chunks:
                    if str(c["id"]) not in target_chunks_ids:
                        missing_sample = (c.get("content") or "")[:200] + "..."
                        break

            # 보정 필요성 판단
            has_title = stat["title"] not in ["Untitled", "", None]
            if total_chunks > indexed_count:
                status = "Missing" if indexed_count == 0 else "Partial"
            elif not has_title:
                status = "Missing Title"
            else:
                status = "In Sync"

            report.append({
                "id": str(doc_id),
                "title": stat["title"],
                "url": stat["url"],
                "total_chunks": total_chunks,
                "target_chunks": indexed_count,
                "drift_ratio": (total_chunks - indexed_count) / total_chunks if total_chunks > 0 else 0,
                "status": status,
                "missing_sample": missing_sample
            })
            
        return report

    def propagate_document_metadata(self, doc_id: str) -> bool:
        """상위 문서의 제목(Title) 등을 하위 청크들로 전파"""
        doc = self.primary_repo.get(doc_id)
        if not doc:
            return False
            
        title = doc.metadata.get("title")
        if not title:
            # URL 기반 Fallback 시도 (나중에 고도화)
            source = doc.metadata.get("source", "")
            if source:
                title = source.split("/")[-1] or "Untitled"
                doc.metadata["title"] = title
                self.primary_repo.save(doc)
            else:
                return False
                
        chunks = self.primary_repo.get_chunks(doc_id)
        for chunk in chunks:
            chunk.metadata["title"] = title
            
        # Primary Repo에 업데이트 (Neo4j MERGE 지원)
        self.primary_repo.save_with_chunks(doc, chunks)
        return True

    def sync_document(self, doc_id: str) -> Dict[str, Any]:
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

    def sync_all(self, batch_size: int = 20, callback: Any = None):
        """누락된 데이터(Chunk) 및 결함 있는 메타데이터(Title)를 일괄 복구"""
        reports = self.get_document_drift_report()
        target_docs = [r for r in reports if r["status"] != "In Sync"]
        
        if not target_docs:
            if callback: callback(1.0, "Already in sync")
            return
            
        total = len(target_docs)
        for i, doc_report in enumerate(target_docs):
            doc_id = doc_report["id"]
            # sync_document는 metadata 보정과 chunk 저장을 모두 수행함
            self.sync_document(doc_id)
            
            if callback:
                progress = min((i + 1) / total, 1.0)
                callback(progress, f"Fixed {i + 1} / {total} documents ('{doc_report['title']}')")
