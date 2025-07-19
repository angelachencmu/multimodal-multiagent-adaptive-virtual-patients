import gpt as gpt 
import numpy as np

VERBOSELTM = False  
def logLTM(msg):
    if VERBOSELTM:
        print(msg)

class LTM:
    def __init__(self):
        # ltm[0] = negative, ltm[1] = neutral, ltm[2] = positive
        self.sessionltm = []
        self.ltm = []

    def returnSessionSummary(self, session):
        sessionIndex = session - 2
        if sessionIndex >= 0:
            return "\n".join(f"{i+1}. {item}" for i, item in enumerate(self.sessionltm[sessionIndex]))
        else:
            return "N/A"

    def progressSession(self, summaryHistory):
        sessionDiscussion = []
        for i in range(len(summaryHistory)):
            messages = [{"role" : "system",
            "content": f"You are provided checkpoint {i + 1} for therapy session {len(self.sessionltm) + 1} of a patient. Reword the following checkpoint simular to 'At checkpoint {i+1} of therapist session {len(self.sessionltm) + 1} with your therapist you talked about ... and it effected you in ... leading to ...' ",
            }]
            summarized, messages = gpt.queryGPT(
                messages,
                message=f"Rewrite the following memory in second person (you pronouns) keep main concepts:\n\n{summaryHistory[i]}"
            )
            sessionDiscussion.append(summarized)

            print(f"session discussion: {sessionDiscussion}")
            embedding = gpt.getGPTEmbedding(sessionDiscussion)

            self.ltm.append({
                "importance": 8,
                "memory": summarized,
                "embedding": embedding,
            })
        self.sessionltm.append(sessionDiscussion)
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
        
        messages = [{"role" : "system",
            "content":"summarize the memory in one sentence by preserving the main ideas",
            }]
        summarized, messages = gpt.queryGPT(
            messages,
            message=f"Summarize the following memory in second person (you pronouns) keep main concepts:\n\n{memory[1]}"
        )
                
        embedding = gpt.getGPTEmbedding(summarized)
        self.ltm.append({
            "importance": memory[0],
            "memory": summarized,
            "embedding": embedding,
        })

    def returnLTMRepository(self, topN=5):
        if (len(self.ltm) > 0):
            queryEmbedding = self.ltm[-1]['embedding']
        else:
            return []

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
        return "\n".join(f"{i+1}. {item[1]}" for i, item in enumerate(repo))
    
    def returnFullLTMRepositoryToString(self):
        return "\n".join(f"{item['memory']}" for i, item in enumerate(self.ltm))