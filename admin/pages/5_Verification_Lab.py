import asyncio

import streamlit as st

from admin.utils.di_helper import get_manual_rag_service

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
    async def run_test():
        rag_service = await get_manual_rag_service()
        # Spec 063: Call service with correct signature (str, list, etc.)
        return await rag_service.retrieve_and_generate(
            query=question, 
            history=[], 
            thread_id=conv_id
        )

    with st.spinner("🚀 RAG Pipeline 실행 중... (Retrieval -> Rerank -> Generation)"):
        try:
            # Streamlit runs in a loop, so asyncio.run might fail if we are already in one?
            # Streamlit pages usually run in a thread.
            # Using asyncio.run() is safe here as long as no other loop is active in this thread.
            result = asyncio.run(run_test())

            # 1. Answer Display
            st.subheader("💡 Answer")
            st.info(result.answer)

            # 2. Verification Status
            st.subheader("✅ Verification Status")
            if expected_keyword:
                if expected_keyword in result.answer:
                    st.success(f"SUCCESS: 키워드 '{expected_keyword}'가 답변에 포함되어 있습니다.")
                else:
                    st.error(f"FAILED: 키워드 '{expected_keyword}'를 답변에서 찾을 수 없습니다.")
            else:
                st.info("검증 키워드가 입력되지 않아 검증을 건너뛰었습니다.")

            # 3. Sources
            with st.expander("📚 참조 문서 (Sources)", expanded=True):
            # 3. Sources
            with st.expander("📚 참조 문서 (Sources)", expanded=True):
                # Prefer vector_chunks for content
                if result.vector_chunks:
                    for idx, chunk in enumerate(result.vector_chunks):
                        st.markdown(f"**{idx+1}. Chunk {chunk.index}** (Parent ID: `{chunk.parent_id}`)")
                        st.text(chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content)
                        st.divider()
                elif result.citations:
                    for idx, doc in enumerate(result.citations):
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
st.caption("Note: 이 기능은 `app.application.services.rag.RAG` 서비스를 직접 호출합니다. DB 연결 설정(.env)이 필요합니다.")
