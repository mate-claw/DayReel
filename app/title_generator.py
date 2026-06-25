from .qwen_client import QwenClient

class TitleGenerator:
    def __init__(self):
        self.qwen = QwenClient()

    def generate(self, clips, mood):
        return self.qwen.generate_title(clips, mood)
