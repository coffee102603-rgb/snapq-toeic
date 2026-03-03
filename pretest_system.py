"""
SnapQ TOEIC V2 - 사전 진단 테스트
연구 시작 전 초기 평가
"""

import streamlit as st
import json
from datetime import datetime

class PretestSystem:
    """사전 진단 시스템"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.pretest_file = f"data/research_logs/{user_id}_pretest.json"
    
    def has_completed_pretest(self):
        """사전 테스트 완료 여부 확인"""
        import os
        return os.path.exists(self.pretest_file)
    
    def save_pretest_results(self, survey_data, p5_score, p7_score):
        """사전 테스트 결과 저장"""
        results = {
            "user_id": self.user_id,
            "timestamp": datetime.now().isoformat(),
            "survey": survey_data,
            "p5_pretest": p5_score,
            "p7_pretest": p7_score
        }
        
        import os
        os.makedirs("data/research_logs", exist_ok=True)
        
        with open(self.pretest_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    def show_pretest_survey(self):
        """사전 설문 조사"""
        st.markdown("### 📋 연구 참여 사전 설문")
        st.info("학습 효과 연구를 위한 설문입니다. 솔직하게 답변해주세요!")
        
        with st.form("pretest_survey"):
            # 기본 정보
            st.markdown("#### 1. 기본 정보")
            age = st.number_input("나이", min_value=15, max_value=60, value=22)
            gender = st.selectbox("성별", ["남성", "여성", "기타"])
            
            # 토익 경험
            st.markdown("#### 2. 토익 경험")
            toeic_experience = st.radio(
                "토익 시험 경험",
                ["처음", "1-2회", "3-5회", "6회 이상"]
            )
            
            current_score = st.number_input(
                "최근 토익 점수 (없으면 예상 점수)",
                min_value=0, max_value=990, value=500, step=10
            )
            
            target_score = st.number_input(
                "목표 점수",
                min_value=0, max_value=990, value=700, step=10
            )
            
            # 학습 습관
            st.markdown("#### 3. 학습 습관")
            study_hours = st.slider(
                "주당 토익 학습 시간",
                min_value=0, max_value=20, value=5
            )
            
            study_method = st.multiselect(
                "주로 사용하는 학습 방법",
                ["문제집", "인강", "학원", "앱/플랫�orm", "스터디"]
            )
            
            # 자기 평가
            st.markdown("#### 4. 자기 평가 (1-5점)")
            confidence = st.slider("토익 자신감", 1, 5, 3)
            concentration = st.slider("집중력", 1, 5, 3)
            motivation = st.slider("학습 동기", 1, 5, 3)
            
            submitted = st.form_submit_button("제출하고 진단 테스트 시작")
            
            if submitted:
                survey_data = {
                    "age": age,
                    "gender": gender,
                    "toeic_experience": toeic_experience,
                    "current_score": current_score,
                    "target_score": target_score,
                    "study_hours": study_hours,
                    "study_method": study_method,
                    "confidence": confidence,
                    "concentration": concentration,
                    "motivation": motivation
                }
                return survey_data
        
        return None
    
    def show_diagnostic_test(self, arena_type):
        """진단 테스트 (P5 또는 P7)"""
        st.markdown(f"### 💣 {arena_type} 진단 테스트")
        st.info(f"{arena_type} 10문제를 풀어주세요. 실력을 측정합니다.")
        
        # 실제로는 문제 풀이 인터페이스
        # 여기서는 간단히 점수 입력
        score = st.number_input(
            f"{arena_type} 정답 개수",
            min_value=0, max_value=10, value=5,
            help="진단 테스트 결과"
        )
        
        return score
