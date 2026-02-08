import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver

# 1. DB 연결 (현재 경로의 checkpoints.sqlite 사용)
conn = sqlite3.connect("checkpoints.sqlite")
checkpointer = SqliteSaver(conn)

# 2. 저장된 모든 thread_id 확인
with conn:
    cursor = conn.cursor()
    # checkpoints 테이블에서 고유한 thread_id 추출
    cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
    threads = [row[0] for row in cursor.fetchall()]

print(f"📌 저장된 대화/작업 스레드 목록: {threads}")

if threads:
    # 가장 최근 스레드 하나 선택하여 상태 확인
    target_id = threads[-1]
    print(f"\n🔍 '{target_id}' 스레드의 최신 상태(State)를 가져옵니다...")

    config = {"configurable": {"thread_id": target_id}}
    snapshot = checkpointer.get(config)

    if snapshot:
        # snapshot.values는 RAGGraphState 또는 IngestionGraphState의 딕셔너리입니다.
        state = snapshot.values
        print("✅ 최신 스냅샷 데이터:")
        for key, value in state.items():
            # 데이터가 너무 길면 잘라서 출력
            val_str = str(value)
            if len(val_str) > 200:
                val_str = val_str[:200] + "..."
            print(f"  - {key}: {val_str}")
    else:
        print("❌ 해당 스레드에 스냅샷이 없습니다.")
else:
    print("❌ 저장된 데이터가 없습니다.")
