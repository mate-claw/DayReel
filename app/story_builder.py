class StoryBuilder:
    def build(self,clips):
        story={'hook':[],'build':[],'peak':[],'end':[]}
        for c in clips:
            story[c['scene']].append(c['url'])
        return story
