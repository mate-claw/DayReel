import os, requests

class TitleGenerator:
    def generate(self, clips):

        prompt = f"Create viral short video title:\n{clips}"

        r = requests.post(
            os.getenv('QWEN_BASE_URL') + "/chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('QWEN_API_KEY')}"},
            json={
                "model": os.getenv('QWEN_TEXT_MODEL'),
                "messages": [{"role":"user","content":prompt}]
            }
        )

        return r.json()["choices"][0]["message"]["content"]
