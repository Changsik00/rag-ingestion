import sys
from pprint import pprint
from src.application.workflow import create_workflow

def main():
    """
    Rag Ingestion Pipeline Entry Point
    """
    print("🚀 Starting Rag Ingestion Pipeline...")
    
    # 1. 초기 URL 설정 (Test input)
    inputs = {
        "urls": [
            "https://www.youtube.com/watch?v=example1",
            "https://medium.com/example-article"
        ]
    }
    print(f"📥 Input URLs: {inputs['urls']}")

    # 2. Workflow 생성 및 실행
    try:
        app = create_workflow()
        result = app.invoke(inputs)
        
        # 3. 결과 출력
        print("\n✅ Pipeline Finished Successfully!")
        print(f"📊 Final Status: {result.get('status')}")
        print(f"📚 Processed Sources: {len(result.get('sources', []))}")
        
        print("\n--- [Output Detail] ---")
        for idx, source in enumerate(result.get("sources", [])):
            print(f"[{idx+1}] URL: {source.url}")
            print(f"    Chunks: {len(source.chunks)} EA")
            print(f"    Title: {source.title}")
            
    except Exception as e:
        print(f"\n❌ Execution Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
