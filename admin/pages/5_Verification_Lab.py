import asyncio  # Not strictly needed if we don't use async code directly, but kept for compatibility


import streamlit as st

from admin.utils.api_client import get_api_client

st.set_page_config(page_title="Verification Lab", page_icon="🧪", layout="wide")
st.title("🧪 Verification Lab")
st.markdown("RAG Pipeline을 스크립트 기반으로 검증하는 실험실입니다.")

# --- Form Section ---
with st.form("verification_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        question = st.text_input("질문 (Question)", value="네오사피엔스 주식매수선택권 계약의 행사가격은 얼마인가요?")
    with col2:
        # Conversation ID는 테스트 격리를 위해 매번 변경하거나 고정 가능
        conv_id = st.text_input("Conversation ID", value="verify-lab-test")

    expected_keyword = st.text_input("검증 키워드 (Expected Keyword / Optional)", value="500원", help="답변에 포함되어야 할 필수 키워드입니다.")

    submitted = st.form_submit_button("🧪 Run Verification", type="primary")

# --- Execution Section ---
if submitted:
    api_client = get_api_client()

    with st.spinner("🚀 RAG Pipeline 실행 중... (Retrieval -> Rerank -> Generation)"):
        try:
            # Call API
            payload = {
                "message": question,
                "filters": {},
                "hitl_enabled": False,
                # Force top_k=5 for retrieval context visibility
                "advanced_settings": {"top_k": 5}
            }
            
            # API endpoint: POST /sessions/{id}/ask
            # returns ChatResponse
            resp = api_client.post(f"/sessions/{conv_id}/ask", json=payload)

            if resp:
                # 1. Answer Display
                # ChatResponse.messages -> Last message is assistant's answer
                messages = resp.get("messages", [])
                answer = ""
                if messages and messages[-1]["role"] == "assistant":
                    answer = messages[-1]["content"]

                st.subheader("💡 Answer")
                st.info(answer if answer else "No answer generated.")

                # 2. Verification Status
                st.subheader("✅ Verification Status")
                if expected_keyword:
                    if expected_keyword in answer:
                        st.success(f"PASS: Keyword '{expected_keyword}' found in answer.")
                    else:
                        st.error(f"FAIL: Keyword '{expected_keyword}' NOT found.")
                else:
                    st.caption("검증 키워드가 입력되지 않았습니다.")

                # 3. Sources
                # ChatResponse.context_data contains 'vector_chunks' or 'citations'
                context_data = resp.get("context_data", {})
                
                with st.expander("📚 참조 문서 (Sources)", expanded=True):
                    # Prefer vector_chunks for detailed content
                    vector_chunks = context_data.get("vector_chunks", [])
                    citations = context_data.get("citations", [])
                    
                    if vector_chunks:
                        for idx, chunk in enumerate(vector_chunks):
                            # chunk is a dict here (from JSON response)
                            idx_label = chunk.get("index", idx)
                            parent_id = chunk.get("parent_id", "Unknown")
                            content = chunk.get("content", "")
                            
                            st.markdown(f"**{idx+1}. Chunk {idx_label}** (Parent ID: `{parent_id}`)")
                            st.text(content[:200] + "..." if len(content) > 200 else content)
                            st.divider()
                    
                    elif citations:
                        for idx, doc in enumerate(citations):
                            title = doc.get("title", "No Title")
                            doc_id = doc.get("source", "Unknown ID") 
                            st.markdown(f"**{idx+1}. {title}** (Source: `{doc_id}`)")
                            st.divider()
                    else:
                        st.warning("참조된 문서가 없습니다.")

        except Exception as e:
            st.error(f"실행 중 오류가 발생했습니다: {str(e)}")
            st.exception(e)

st.divider()
st.caption("Note: 이 기능은 Backend API (`/sessions/{id}/ask`)를 호출하여 동작합니다.")
