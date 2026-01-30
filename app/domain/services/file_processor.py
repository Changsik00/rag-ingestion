import logging
from collections.abc import Generator
from typing import Any

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class FileProcessor:
    """PDF, TXT, MD 파일로부터 텍스트를 추출하고 표준 마크다운으로 변환하는 서비스"""

    def extract_text(self, content: bytes, filename: str) -> str:
        """기존 호환성을 위한 메서드: 모든 세그먼트를 하나로 합쳐서 반환"""
        segments = list(self.extract_segments(content, filename))
        return "\n\n".join([text for text, _ in segments])

    def extract_segments(
        self, content: bytes, filename: str, batch_size: int = 10
    ) -> Generator[tuple[str, dict[str, Any]], None, None]:
        """파일을 분할하여 (텍스트, 메타데이터) 쌍을 생성하는 제너레이터"""
        ext = filename.split(".")[-1].lower()

        if ext == "pdf":
            yield from self._iter_pdf(content, filename, batch_size)
        elif ext in ["txt", "md"]:
            yield from self._iter_text(content, filename)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    def _iter_pdf(
        self, content: bytes, filename: str, batch_size: int
    ) -> Generator[tuple[str, dict[str, Any]], None, None]:
        """PDF를 페이지 묶음 단위로 처리"""
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            total_pages = len(doc)

            for i in range(0, total_pages, batch_size):
                batch_text = []
                if i == 0:
                    batch_text.append(f"# {filename}\n")

                end_idx = min(i + batch_size, total_pages)
                for page_num in range(i, end_idx):
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    batch_text.append(f"## Page {page_num + 1}")
                    batch_text.append(page_text)

                metadata = {
                    "filename": filename,
                    "pages": f"{i + 1}-{end_idx}",
                    "total_pages": total_pages,
                    "segment_index": i // batch_size,
                }
                yield "\n\n".join(batch_text), metadata

            doc.close()
        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {str(e)}")
            raise

    def _iter_text(self, content: bytes, filename: str) -> Generator[tuple[str, dict[str, Any]], None, None]:
        """일반 텍스트 및 마크다운 처리 (현재는 단일 세그먼트로 처리하되 인터페이스 통일)"""
        try:
            # UTF-8 시도, 실패 시 다양하게 시도할 수 있으나 기본은 UTF-8
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                text = content.decode("cp949")

            header = f"# {filename}\n\n" if not filename.lower().endswith(".md") else ""
            metadata = {"filename": filename, "segment_index": 0}
            yield f"{header}{text}", metadata

        except Exception as e:
            logger.error(f"Error decoding text file {filename}: {str(e)}")
            raise
