import gpt as gpt 
import numpy as np

VERBOSELTM = False  
def logLTM(msg):
    if VERBOSELTM:
        print(msg)

class LTM:
    def __init__(self):
        # ltm[0] = negative, ltm[1] = neutral, ltm[2] = positive
        self.ltm = []
    
    # TODO: Create a progression mech that resorts ltm
    def progressSession(self):
        return
    
    def cosineSimilarity(self, vec1, vec2):
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
            return 0.0
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    
    def addToLTM(self, memory):
        if(memory[0] < 5):
            return
        
        embedding = gpt.getGPTEmbedding(memory[1])
        self.ltm.append({
            "memory": memory,
            "embedding": embedding
        })

    def returnLTMRepository(self, topN=5):
        queryEmbedding = self.ltm[-1]['embedding']

        memories = []
        for item in self.ltm:
            print(type(item['embedding']))
            score = self.cosineSimilarity(queryEmbedding, item['embedding'])
            memories.append((score, item['memory']))
        
        memories.sort(reverse=True, key=lambda x: x[0])
        if len(self.ltm) > topN:
            return memories[1:topN + 1]
        return memories[1: len(self.ltm)]

    def returnLTMRepositoryToString(self):
        repo = self.returnLTMRepository()
        return "\n".join(f"{i+1}. {item[1][1]}" for i, item in enumerate(repo))
    
    def returnFullLTMRepositoryToString(self):
        return "\n".join(f"{item['memory']}" for i, item in enumerate(self.ltm))