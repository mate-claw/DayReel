class Selector:
    def select(self, clips):
        clips = sorted(clips, key=lambda x: x["motion"] + x["energy"], reverse=True)
        if len(clips) < 3:
            clips = clips * 2
        return clips[:15]
