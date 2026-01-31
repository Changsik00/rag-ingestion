import asyncio
import json
import logging
import multiprocessing
import os
from typing import Any

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

from app.domain.interfaces.scraper import ScraperInterface
from app.interfaces.api.schemas.ingest import IngestResponse

logger = logging.getLogger(__name__)


class YouTubeScraper(ScraperInterface):
    """
    YouTube 영상 정보를 고품질 지식으로 변환하는 스크래퍼.
    1. 자막 수집 (Transcript API)
    2. 저품질/부재 시 STT (Faster-Whisper Fallback)
    3. LLM 기반 지식 구조화 (Summary, Claims, Topics)
    """

    def __init__(self, llm=None):
        self.llm = llm
        self.whisper_model = None

    async def scrape(self, url: str) -> IngestResponse:
        logger.info(f"YouTube 스크래핑 시작: {url}")
        video_id = self._extract_video_id(url)

        # 1. 자막 수집 시도
        transcript_text = await self._get_transcript(video_id)

        # 2. 자막 부재 시 Whisper Fallback
        if not transcript_text:
            logger.info("자막 데이터를 찾을 수 없어 Whisper STT Fallback을 실행합니다.")
            audio_path = await self._extract_audio(url)
            try:
                whisper_segments = await asyncio.to_thread(self._run_whisper, audio_path)
                transcript_text = " ".join([s["text"] for s in whisper_segments])
            finally:
                if audio_path and os.path.exists(audio_path):
                    os.remove(audio_path)

        if not transcript_text:
            raise ValueError("YouTube 영상에서 텍스트 콘텐츠를 추출하는 데 실패했습니다.")

        # 3. LLM 기반 지식 구조화 및 정제
        knowledge = await self._extract_knowledge_with_llm(transcript_text)

        # 4. IngestResponse 생성
        markdown_content = self._format_as_markdown(knowledge)
        metadata = {
            "title": knowledge.get("title", f"YouTube Video: {video_id}"),
            "source": url,
            "video_id": video_id,
            "knowledge": knowledge,
        }

        return IngestResponse(url=url, markdown=markdown_content, metadata=metadata)

    def _extract_video_id(self, url: str) -> str:
        import re

        # 다양한 YouTube URL 패턴 대응 (escaped characters 포함)
        patterns = [
            r"[vV](?:=|\\{1,2}=)([0-9A-Za-z_-]{11})",  # v=ID 또는 v\=ID 또는 v\\=ID
            r"(?:be\/|embed\/|v\/|shorts\/)([0-9A-Za-z_-]{11})",  # youtu.be/ID, shorts/ID 등
            r"(?:\/)([0-9A-Za-z_-]{11})(?:[\?&]|$)",  # /ID?query 또는 /ID
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        raise ValueError(f"유효하지 않은 YouTube URL입니다: {url}")

    async def _get_transcript(self, video_id: str) -> str | None:
        try:
            # 우선순위: 수동 자막 -> 자동 자막
            transcript_list = YouTubeTranscriptApi().list(video_id)
            try:
                # 한국어 또는 영어 수동 자막 시도
                transcript = transcript_list.find_transcript(["ko", "en"])
            except Exception:
                # 아무 자막이나 가져오기 (자동 생성 포함)
                transcript = transcript_list.find_generated_transcript(["ko", "en"])

            data = transcript.fetch()
            # 딕셔너리 형태와 객체 형태(FetchedTranscriptSnippet) 모두 대응
            return " ".join([d["text"] if isinstance(d, dict) else getattr(d, "text", "") for d in data])
        except Exception as e:
            logger.warning(f"Transcript 수집 실패: {e}")
            return None

    async def _extract_audio(self, url: str) -> str:
        temp_audio_path = f"temp_audio_{self._extract_video_id(url)}"
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": temp_audio_path + ".%(ext)s",
            "quiet": True,
        }

        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return temp_audio_path + ".mp3"

        return await asyncio.to_thread(download)

    def _run_whisper(self, audio_path: str) -> list[dict[str, Any]]:
        from faster_whisper import WhisperModel

        # [Intel Core i9 최적화]
        # device="cpu", compute_type="int8" (Quantization) 적용
        if self.whisper_model is None:
            logger.info("Whisper 모델 로드 중 (Intel i9 CPU 최적화 모드)...")
            self.whisper_model = WhisperModel(
                "medium", device="cpu", compute_type="int8", cpu_threads=max(1, multiprocessing.cpu_count() - 2)
            )

        segments, info = self.whisper_model.transcribe(audio_path, beam_size=5)

        results = []
        for segment in segments:
            results.append({"start": segment.start, "end": segment.end, "text": segment.text.strip()})
        return results

    async def _extract_knowledge_with_llm(self, transcript: str) -> dict[str, Any]:
        if not self.llm:
            return {"summary": transcript, "sections": [], "claims": [], "tone": "N/A", "intent": "N/A"}

        prompt = f"""
다음은 유튜브 영상의 자막 스크립트입니다. 이를 바탕으로 고품질 지식 문서를 생성해주세요.
반드시 아래 JSON 형식을 지켜주세요.

[스크립트 시작]
{transcript[:8000]}  # 텍스트가 너무 길면 잘라서 전달
[스크립트 끝]

분석 요청사항:
1. summary: 영상의 핵심 내용을 3-4문장으로 요약
2. sections: 주제가 전환되는 지점을 식별하여 타임라인별 주제 요약 (start, end 시간 정보는 스크립트에 없을 경우 제외 가능)
3. claims: 영상에서 사실로 주장하는 핵심 내용들 추출
4. tone: 영상의 전반적인 어조 (예: 객관적, 비판적, 교육적 등)
5. intent: 영상의 제작 의도
6. title: 영상을 대표하는 제목

응답 형식 (JSON):
{{
  "title": "...",
  "summary": "...",
  "sections": [
    {{"topic": "...", "start_time": "...", "end_time": "..."}}
  ],
  "claims": [
    {{"text": "...", "reasoning": "..."}}
  ],
  "tone": "...",
  "intent": "..."
}}
"""
        try:
            response_text = await self.llm.agenerate(prompt)
            # JSON 추출 (Markdown 코드 블록 제거 등)
            import re

            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"summary": transcript, "sections": [], "claims": [], "tone": "N/A", "intent": "N/A"}
        except Exception as e:
            logger.error(f"LLM 지식 추출 실패: {e}")
            return {"summary": transcript, "sections": [], "claims": [], "tone": "N/A", "intent": "N/A"}

    def _format_as_markdown(self, knowledge: dict[str, Any]) -> str:
        md = f"# {knowledge.get('title', 'Video Knowledge Document')}\n\n"
        md += f"## 📝 핵심 요약\n{knowledge.get('summary', '')}\n\n"

        if knowledge.get("sections"):
            md += "## 📂 주제별 타임라인\n"
            for sec in knowledge["sections"]:
                md += f"- **{sec.get('topic')}**\n"
            md += "\n"

        if knowledge.get("claims"):
            md += "## 🎯 주요 주장 및 사실\n"
            for claim in knowledge["claims"]:
                md += f"- {claim.get('text')}\n"
            md += "\n"

        md += "## 🔍 분석 데이터\n"
        md += f"- **어조**: {knowledge.get('tone')}\n"
        md += f"- **의도**: {knowledge.get('intent')}\n"

        return md
