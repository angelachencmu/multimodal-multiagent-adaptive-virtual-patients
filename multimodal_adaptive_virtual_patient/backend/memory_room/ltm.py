import gpt as gpt 

VERBOSELTM = False  
def logLTM(msg):
    if VERBOSELTM:
        print(msg)

class LTM:
    def __init__(self):
        # ltm[0] = negative, ltm[1] = neutral, ltm[2] = positive
        self.ltm = [[], [], []]
    
    # memory: (ranking, memory)
    def addToLTM(self, memory):
        if(memory[0] < 5):
            return
        
        messages = [{"role" : "system",
            "content":"You are an intelligent assistant. Return 0, 1, or 2. Only return the numerical equivalent one of the 3 emotion classifiers: Neutral (1), Negative (0), Positive (2)",
            }]
        emotionCategory, messages = gpt.queryGPT(
            messages,
            message=f"Classify the following memory into one of 3 different groups (Neutral (1), Negative (0), Positive (2)), rate the emotional association of the following piece of memory:\n\n{memory[1]}"
        )
        
        try:
            emotion = int(emotionCategory.strip())
            if 0 <= emotion < len(self.ltm):
                messages = [{"role" : "system",
                    "content":"summarize the memory in one sentence by preserving the main ideas",
                    }]
                summarized, messages = gpt.queryGPT(
                    messages,
                    message=f"Summarize the following memory in second person (you pronouns) but keep the main concepts:\n\n{memory[1]}"
                )
                self.ltm[emotion].append(summarized)
                logLTM(f"(emotion {emotion}): {summarized}")
            else:
                print(f"[ERROR] Invalid emotion index: {emotion}")
        except ValueError:
            print(f"[ERROR] GPT returned invalid emotion category: {emotionCategory}")  
        
        logLTM(self.printLTM())

    def returnLTMRepository(self, emotion):
        messages = [{"role" : "system",
            "content":"You are an intelligent assistant. Return 0, 1, or 2. Only return the numerical equivalent one of the 3 emotion classifiers: Neutral (1), Negative (0), Positive (2)",
            }]
        score, messages = gpt.queryGPT(
            messages,
            message=f"Classify the following memory into one of 3 different groups (Neutral (1), Negative (0), Positive (2)), rate the emotion:\n\n{emotion}"
        )
        try:
            score = int(score.strip())
            if not (0 <= score <= 2):
                print("[ERROR] Chat didn't score correctly.")
            return self.ltm[score]
        except ValueError:
            print("[ERROR] Invalid score format received from GPT.")
            score = 0 

    def printLTM(self):
        print(f"Negative: {self.ltm[0]}")
        print(f"Nuetral: {self.ltm[1]}")
        print(f"Positive: {self.ltm[2]}")