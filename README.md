# 🏫 School Announcement ChatBot (리팩토링 중)

## 🚀 프로젝트 개요
학교 공지사항 챗봇 프로젝트는 학생들이 학과 및 학교 공지사항을 빠르고 정확하게 확인할 수 있도록 지원하는 AI 기반 챗봇 시스템입니다.  
현재는 **학과 단위 공지사항 크롤링**을 시작으로 단계적으로 확장 중이며, 이번 리팩토링의 목표는 **검색 정확도 향상과 응답 속도 최적화**입니다.

---

## ✨ 주요 리팩토링 사항

### 1. 학과 공지사항 크롤링
- 경북대학교 전체 학과 공지사항 데이터를 수집하는 단계.
- 크롤링 데이터 기반으로 Qdrant에 벡터화 및 저장 예정.

### 2. 벡터 데이터베이스
- **Qdrant** 사용.
- 하이브리드 검색 기능(BM25 기반 sparse + 임베딩 기반 dense) 지원.
- 빠른 검색과 정확한 결과 제공 가능.

### 3. 임베딩 모델
- **Upstage 모델** 사용.
- 학과 공지사항 텍스트를 임베딩하여 의미 기반 검색 수행.

### 4. 하이브리드 검색
- Qdrant의 하이브리드 검색 기능 활용.
- Sparse(BM25) + Dense(임베딩) 벡터 결합을 통해 키워드와 의미 기반 검색 수행.
- 필요에 따라 re-rank 등 추가 최적화 적용 가능.

### 5. 평가지표
- LLM judge 또는 자동 평가지표 도입 예정.
- 목표: 테스트셋 기준 90% 이상의 검색 정확도 달성.

---

## ⚡️ 기대 성능 향상
- **응답 시간**: 기존 3~10초 → Qdrant + streaming 응답 적용으로 체감 속도 개선.
- **검색 정확도**: 기존 80~85% → 목표 90% 이상.
- 사용자 경험: 답변 생성 중 실시간 스트리밍 표시로 지연 체감 최소화.

---

## 🛠 향후 계획
1. 학과 단위 크롤링 완료 후, 학교 전체 공지사항 확장.
2. Qdrant 기반 검색 최적화 및 성능 모니터링.
3. 가중치 학습 및 경량화된 re-rank 방식 적용 검토.
4. 지속적인 LLM 및 검색 성능 개선.

---

## 📂 기술 스택

- **LLM & 임베딩**: Upstage 모델
- **Vector DB**: Qdrant (하이브리드 검색 지원)
- **검색 기법**: Qdrant 하이브리드 검색
- **평가**: 자동 평가지표(LMM Judge, 커스텀 메트릭)

---
---

## 26.01.06 현재 상황 점검

1. 학과 단위 공지사항 크롤링 완료(2025.01.01 이후의 데이터)
2. bge-m3 (ONNX INT8) + Qdrant(SQ INT8) + Kiwi+ BM25 기반으로 한 sprase +dense  hybrid RAG 구축 완료
3. neo4j 활용한 graph rag 구축 중 일단 vllm qwen 2.5 -32b structed awq 활용하여 graph 1차 구축 완료
4. rerank 또한 bge-m3-reranker-based ONNX INT8로 하여 재순위화 비교해 볼 예정.

--- 
## 평가 기준
### **QA 셋에 활용한 동일한 문서를 Question만 보고 RAG 시스템은 제대로 검색했는가를 기준으로 판단함**
  
- **단순 rerank 없이 검색한 결과(355개)** + **BM25와 가중치 단순 도입**
<img width="780" height="282" alt="image" src="https://github.com/user-attachments/assets/55d234a0-c189-4f7d-abf4-9cb4d4542065" />

- **BM25 +Kiwi+weights 도입 이후**
<img width="758" height="314" alt="image" src="https://github.com/user-attachments/assets/bd5709a3-aca0-4c99-b9b4-02a23c931d48" />



