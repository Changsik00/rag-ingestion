# 011-youtube-strategy: Intel Mac Optimization & Deployment

본 문서는 Spec 047(YouTube Knowledge Scraper)의 원활한 운영을 위해 로컬(Intel Mac) 및 배포 환경에서의 하드웨어 가속 및 운영 전략을 정의합니다.

---

## 💻 로컬 환경 (Intel Mac) 최적화 가이드

사용자 환경: **Macbook Pro (Intel Core i9-9880H)**

### 1. Whisper 엔진 및 가속 전략
- **라이브러리**: `faster-whisper`
- **전략**: Intel CPU의 **AVX/AVX2 명령어 세트**를 활용한 고효율 연산.
- **최적화 설정**:
    - `compute_type="int8"`: 가중치를 8비트로 양자화하여 메모리 사용량을 절반으로 줄이고, i9 CPU에서의 추론 속도를 약 2~3배 향상시킴.
    - `cpu_threads`: 실제 물리 코어 수에 맞게 설정 (i9의 경우 8코어 16스레드이므로, 부하 관리를 위해 6~8개 스레드 할당 권장).

### 2. 필수 시스템 의존성
- **FFmpeg**: 오디오 추출 및 포맷 변환을 위해 필수.
    ```bash
    brew install ffmpeg
    ```

### 3. 로컬 실행 시 주의사항
- Whisper `medium` 모델 로드 시 약 1.5GB의 메모리가 필요합니다.
- STT 실행 중에는 CPU 점유율이 일시적으로 높아질 수 있으므로 `compute_type="int8"` 설정을 반드시 유지해야 합니다.

---

## 🚢 배포 환경 (Cloud/Server) 가이드

배포 환경에서는 로컬과 달리 안정성과 확장성에 집중합니다.

### 1. GPU 배포 (권장)
- **환경**: NVIDIA GPU (CUDA 지원)
- **설정**:
    ```python
    model = WhisperModel("medium", device="cuda", compute_type="float16")
    ```
- **이점**: 로컬 CPU 대비 10배 이상의 처리 속도 확보.

### 2. 가상화 (Docker) 고려사항
- **FFmpeg 설치**: Dockerfile에 `ffmpeg` 설치 구문 포함 필수.
    ```dockerfile
    RUN apt-get update && apt-get install -y ffmpeg
    ```
- **모델 캐싱**: 컨테이너 시작 시마다 모델을 다운로드하지 않도록, 모델 파일을 볼륨으로 마운트하거나 이미지 빌드 시 미리 포함 처리.

---

## 💰 비용 및 API Key 요구사항

| 기능 | 사용 기술 | API Key 필요 여부 | 비용 |
| :--- | :--- | :--- | :--- |
| **자막 수집** | `youtube-transcript-api` | **아니오** (내부 엔드포인트 활용) | 무료 |
| **음성 인식 (STT)** | `faster-whisper` | **아니오** (로컬 CPU/GPU 활용) | 무료 (로컬 자원) |
| **지식 구조화** | LLM (Gemini, GPT 등) | **예** (`.env` 설정 키 사용) | 모델별 유료/할당량 소모 |

---

### 3. 외부 API Fallback 전략
- 로컬/서버 리소스가 부족할 경우 `OpenAI Whisper API` 또는 `Google Speech-to-Text`를 호출하는 어댑터로 확장 가능하도록 인터페이스 유지.

---

## 🧠 지식 추출 (LLM) 전략
- **맥락 보존**: 자막은 문장 마침표가 없는 경우가 많으므로, LLM에게 전달 전 반드시 "자연스러운 문장으로 복원"해달라는 페르소나를 부여함.
- **타임라인 분할**: `topic segmentation`을 통해 긴 영상도 의미 단위로 쪼개어 RAG 검색 결과의 정확도를 향상시킴.
