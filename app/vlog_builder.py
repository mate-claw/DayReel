class VlogBuilder:
    def build(self, video_urls, music_url=None):

        clips = []

        for url in video_urls[:5]:  # ⭐限制数量
            clips.append({
                "asset": {
                    "type": "video",
                    "src": url
                },
                "start": "auto",
                "length": 3,   # ⭐核心：统一节奏
                "transition": {
                    "in": "fade",
                    "out": "fade"
                }
            })

        timeline = {
            "tracks": [{"clips": clips}]
        }

        if music_url:
            timeline["soundtrack"] = {
                "src": music_url,
                "volume": 0.25
            }

        return {
            "timeline": timeline,
            "output": {
                "format": "mp4",
                "resolution": "1080"
            }
        }