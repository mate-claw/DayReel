import random

class VisionAI:
    def analyze(self,urls):
        out=[]
        for u in urls:
            out.append({'url':u,'motion':random.random(),'energy':random.random(),'aesthetic':random.random(),'scene':random.choice(['hook','build','peak','end'])})
        return out

    def rank(self,clips):
        return sorted(clips,key=lambda x:x['motion']+x['energy']+x['aesthetic'],reverse=True)[:8]
