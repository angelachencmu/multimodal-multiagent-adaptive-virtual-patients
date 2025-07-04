from .ltm import LTM
from .summary import Summary
from .SEM import SEM
import gpt as gpt 

class MemoryRoom:
    def __init__(self):
        self.ltm = LTM()
        self.summary = Summary()
        self.sem = SEM()
        self.history = []

    def progressSession(self):
        self.resetSession()
        self.ltm.progressSession()

    def resetSession(self):
        self.summary = Summary()
        self.sem = SEM()
        self.history = []

    def processMemory(self, vpResponse, userInput):
        importanceScore = self.score(vpResponse)
        self.ltm.addToLTM((importanceScore, vpResponse))
        if userInput != "InitiateMem801":
            self.history.append((f"Therapist: {userInput}"))
            self.history.append((f"Patient: {vpResponse}"))
            if len(self.history)  == 6:
                print("Starting checkpoint updates")
                self.summary.createSummary(self.history)
                self.history = []
    
    def score(self, conversation):
        messages = [{"role":"system",
            "content" : (
                "You are an intelligent assistant that evaluates the psychological impact of experiences. "
                "Return ONLY a numerical value from 1 to 10 based on how much the memory is likely to affect "
                "a person's personality, emotions, and long-term behaviors. "
                "Score 1 if the memory is mundane or has no lasting effect (e.g., brushing teeth, small talk, talking about the weather), "
                "and 10 if the memory is deeply meaningful and transformative (e.g., falling in love, getting married, developing depression)."
                "Return ONLY a number. Do not include any explanation or words."
            )}]
        score, messages = gpt.queryGPT(
            messages,
            message=f"On a scale from 1 to 10, rate the likely long-term psychological impact of the following memory:\n\n{conversation}"
        )
        try:
            score = int(score.strip())
            if not (1 <= score <= 10):
                print("[ERROR] Chat didn't score correctly.")
        except ValueError:
            print("[ERROR] Invalid score format received from GPT.")
            score = 0

        return score