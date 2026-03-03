"""
SnapQ TOEIC V2 - 사후 진단 테스트
연구 종료 후 최종 평가
"""

import streamlit as st
import json
from datetime import datetime

class PosttestSystem:
    """사후 진단 시스템"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.posttest_file = f"data/research_logs/{user_id}_posttest.json"
    
    def save_posttest_results(self, survey_data, p5_score, p7_score):
        """사후 테스트 결과 저장"""
        results = {
            "user_id": self.user_id,
            "timestamp": datetime.now().isoformat(),
            "survey": survey_data,
            "p5_posttest": p5_score,
            "p7_posttest": p7_score
        }
        
        with open(self.posttest_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    def show_posttest_survey(self):
        """사후 설문 조사"""
        st.markdown("### 📋 학습 경험 설문")
        st.success("20일간 수고하셨습니다! 마지막 설문입니다.")
        
        with st.form("posttest_survey"):
            st.markdown("#### 1. 학습 만족도")
            satisfaction = st.slider(
                "플랫폼 만족도 (1-5점)",
                1, 5, 4
            )
            
            fun_level = st.slider(
                "재미 정도 (1-5점)",
                1, 5, 4
            )
            
            st.markdown("#### 2. 게임 요소 평가")
            timer_helpful = st.slider(
                "타이머가 도움이 되었나요? (1-5점)",
                1, 5, 4
            )
            
            armory_helpful = st.slider(
                "무기고가 도움이 되었나요? (1-5점)",
                1, 5, 4
            )
            
            st.markdown("#### 3. 자기 평가")
            confidence_after = st.slider(
                "현재 토익 자신감 (1-5점)",
                1, 5, 4
            )
            
            speed_improved = st.slider(
                "순발력이 향상되었나요? (1-5점)",
                1, 5, 4
            )
            
            concentration_improved = st.slider(
                "집중력이 향상되었나요? (1-5점)",
                1, 5, 4
            )
            
            st.markdown("#### 4. 자유 의견")
            good_points = st.text_area(
                "좋았던 점",
                placeholder="자유롭게 작성해주세요"
            )
            
            improvements = st.text_area(
                "개선이 필요한 점",
                placeholder="자유롭게 작성해주세요"
            )
            
            submitted = st.form_submit_button("제출하고 최종 테스트 시작")
            
            if submitted:
                survey_data = {
                    "satisfaction": satisfaction,
                    "fun_level": fun_level,
                    "timer_helpful": timer_helpful,
                    "armory_helpful": armory_helpful,
                    "confidence_after": confidence_after,
                    "speed_improved": speed_improved,
                    "concentration_improved": concentration_improved,
                    "good_points": good_points,
                    "improvements": improvements
                }
                return survey_data
        
        return None
