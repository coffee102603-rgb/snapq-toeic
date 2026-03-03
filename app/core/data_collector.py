"""
SnapQ TOEIC V2 - 데이터 수집 모듈 v2 (논문용 강화판)
"""
import json, os
from datetime import datetime

class DataCollector:
    def __init__(self, user_id):
        self.user_id = user_id
        self.data_dir = "data/research_logs"
        os.makedirs(self.data_dir, exist_ok=True)

    def _write(self, filepath, entry):
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _now(self):
        now = datetime.now()
        return {
            "timestamp": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "week": now.strftime("%Y-W%W"),
            "hour": now.hour,
            "day_of_week": now.strftime("%A")
        }

    def log_activity(self, arena, question_id, answer, correct, time_taken, timestamp=None):
        """기존 호환 유지"""
        t = self._now()
        entry = {
            "user_id": self.user_id,
            "timestamp": timestamp or t["timestamp"],
            "arena": arena,
            "question_id": question_id,
            "answer": answer,
            "correct": correct,
            "time_taken": time_taken
        }
        date_str = datetime.now().strftime("%Y%m%d")
        self._write(f"{self.data_dir}/{self.user_id}_{date_str}.jsonl", entry)
        return entry

    def log_activity_v2(self, arena, question_id, answer, correct, time_taken,
                        category=None, timer_selected=None, round_num=None,
                        is_retry=False, module=None):
        """논문용 강화 로그"""
        t = self._now()
        entry = {
            "user_id": self.user_id,
            "timestamp": t["timestamp"],
            "date": t["date"],
            "week": t["week"],
            "hour": t["hour"],
            "day_of_week": t["day_of_week"],
            "module": module or arena,
            "arena": arena,
            "category": category,
            "question_id": question_id,
            "answer": answer,
            "correct": correct,
            "time_taken": round(time_taken, 2),
            "timer_selected": timer_selected,
            "round_num": round_num,
            "is_retry": is_retry
        }
        date_str = datetime.now().strftime("%Y%m%d")
        self._write(f"{self.data_dir}/{self.user_id}_{date_str}.jsonl", entry)
        return entry

    def log_session(self, arena, session_duration, questions_completed):
        """기존 호환 유지"""
        entry = {
            "user_id": self.user_id,
            "timestamp": datetime.now().isoformat(),
            "type": "session",
            "arena": arena,
            "duration": session_duration,
            "questions_completed": questions_completed
        }
        self._write(f"{self.data_dir}/{self.user_id}_sessions.jsonl", entry)

    def log_session_v2(self, module, duration_min, questions_completed,
                       result=None, timer_selected=None, category_selected=None):
        """논문용 강화 세션 로그"""
        t = self._now()
        entry = {
            "user_id": self.user_id,
            "timestamp": t["timestamp"],
            "date": t["date"],
            "week": t["week"],
            "hour": t["hour"],
            "day_of_week": t["day_of_week"],
            "type": "session_v2",
            "module": module,
            "duration_min": round(duration_min, 2),
            "questions_completed": questions_completed,
            "result": result,
            "timer_selected": timer_selected,
            "category_selected": category_selected
        }
        self._write(f"{self.data_dir}/{self.user_id}_sessions.jsonl", entry)

    def log_storage_action(self, action, module, question_id, category=None):
        """저장고 행동 로그 (save/review/delete)"""
        t = self._now()
        entry = {
            "user_id": self.user_id,
            "timestamp": t["timestamp"],
            "date": t["date"],
            "week": t["week"],
            "action": action,
            "module": module,
            "question_id": question_id,
            "category": category
        }
        self._write(f"{self.data_dir}/{self.user_id}_storage.jsonl", entry)

    def log_daily_access(self, modules_used, total_minutes):
        """일별 접속 패턴 로그"""
        t = self._now()
        entry = {
            "user_id": self.user_id,
            "date": t["date"],
            "week": t["week"],
            "day_of_week": t["day_of_week"],
            "modules_used": modules_used,
            "total_minutes": round(total_minutes, 2),
            "session_count": len(modules_used)
        }
        self._write(f"{self.data_dir}/{self.user_id}_access.jsonl", entry)

    def get_user_stats(self):
        """사용자 통계 조회"""
        logs = []
        for filename in os.listdir(self.data_dir):
            if filename.startswith(self.user_id) and filename.endswith(".jsonl"):
                filepath = os.path.join(self.data_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        try: logs.append(json.loads(line))
                        except: pass
        if not logs:
            return None
        activity_logs = [l for l in logs if l.get("type") not in ("session","session_v2")]
        if not activity_logs:
            return None
        total = len(activity_logs)
        correct = sum(1 for l in activity_logs if l.get("correct"))
        avg_time = sum(l.get("time_taken",0) for l in activity_logs) / total if total > 0 else 0
        p5 = [l for l in activity_logs if l.get("arena") == "P5"]
        p7 = [l for l in activity_logs if l.get("arena") == "P7"]
        cat_stats = {}
        for l in activity_logs:
            cat = l.get("category","unknown")
            if cat not in cat_stats:
                cat_stats[cat] = {"total":0,"correct":0}
            cat_stats[cat]["total"] += 1
            if l.get("correct"):
                cat_stats[cat]["correct"] += 1
        for cat in cat_stats:
            t2 = cat_stats[cat]["total"]
            cat_stats[cat]["accuracy"] = round(cat_stats[cat]["correct"]/t2, 3) if t2 > 0 else 0
        return {
            "total_questions": total,
            "correct_count": correct,
            "accuracy": round(correct/total, 3) if total > 0 else 0,
            "avg_time": round(avg_time, 2),
            "p5_count": len(p5),
            "p7_count": len(p7),
            "p5_accuracy": round(sum(1 for l in p5 if l.get("correct"))/len(p5), 3) if p5 else 0,
            "p7_accuracy": round(sum(1 for l in p7 if l.get("correct"))/len(p7), 3) if p7 else 0,
            "category_stats": cat_stats
        }

    def export_to_csv(self):
        """CSV 내보내기"""
        import pandas as pd
        logs = []
        for filename in os.listdir(self.data_dir):
            if filename.startswith(self.user_id) and filename.endswith(".jsonl"):
                filepath = os.path.join(self.data_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        try: logs.append(json.loads(line))
                        except: pass
        if not logs:
            return None
        import pandas as pd
        df = pd.DataFrame(logs)
        csv_path = f"{self.data_dir}/{self.user_id}_export.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        return csv_path

    @staticmethod
    def export_all_users_csv(data_dir="data/research_logs"):
        """전체 학생 데이터 일괄 CSV 내보내기 (Admin용)"""
        import pandas as pd
        logs = []
        if not os.path.exists(data_dir):
            return None
        for filename in os.listdir(data_dir):
            if filename.endswith(".jsonl"):
                filepath = os.path.join(data_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        try: logs.append(json.loads(line))
                        except: pass
        if not logs:
            return None
        df = pd.DataFrame(logs)
        date_str = datetime.now().strftime("%Y%m%d")
        csv_path = f"data/exports/all_users_{date_str}.csv"
        os.makedirs("data/exports", exist_ok=True)
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        return csv_path
