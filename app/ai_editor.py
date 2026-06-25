import random

class AIEditor:

    def analyze(self, videos):
        """
        模拟视频理解：
        给每个视频打标签
        """

        analyzed = []

        for v in videos:
            analyzed.append({
                "url": v,
                "motion_score": random.uniform(0, 1),   # 动态程度
                "importance": random.uniform(0, 1),     # 重要性
                "scene": random.choice(["morning", "day", "night"])
            })

        return analyzed