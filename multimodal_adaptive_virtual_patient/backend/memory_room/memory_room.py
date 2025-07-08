from .ltm import LTM
from .summary import Summary
from .SEM.SEM import SEM
import gpt as gpt 
from memory_room.SEM.constants import DEFAULT_CONFIG


class MemoryRoom:
    def __init__(self):
        self.ltm = LTM()
        self.summary = Summary()
        self.sem = SEM()
        self.history = []
        self.config = DEFAULT_CONFIG
    
    def updateConfig(self, newConfig):
        self.config = newConfig

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
            self.utteranceAnalysis(vpResponse, userInput)
            if len(self.history)  == 6:
                print("Starting checkpoint updates")
                self.summary.createSummary(self.history)
                self.sem.get_rapport_evaluation(self.history)
                self.history = []

    def utteranceAnalysis(self, vpResponse, userInput):
        # 1. Evaluate empathy
        latestEmpathy = self.sem.get_empathy_evaluation(self.getTherapistResponses(), userInput)

        # 2. Retrieve latest rapport for VP conditioning
        past_rapport_scores = self.sem.rapport

        # Flag to skip rapport blending if none exists yet
        rapport_available = len(past_rapport_scores) > 0
        latest_rapport = past_rapport_scores[-1] if rapport_available else {
            "explanation": "No rapport score yet."
        }

        behavior_states = self.sem.compute_behavior_states(latestEmpathy, latest_rapport, self.config)

        depression_state = behavior_states["depression_state"]
        anxiety_state = behavior_states["anxiety_state"]
        self_disclosure_state = behavior_states["self_disclosure_state"]
        blended_rapport = behavior_states["blended_rapport"]
        empathy_rapt_score = behavior_states["empathy_rapt_score"]

        #TODO: Figure out what this does because it isn't used in Siwei's code?
        weighted_empathy = behavior_states["weighted_empathy"]

        self.sem.setBlendedRapport(empathy_rapt_score, blended_rapport)
        self.sem.setBehaviorState(depression_state, anxiety_state, self_disclosure_state)

        self.sem.detect_emotion(vpResponse)
        self.sem.detect_depression(vpResponse)
        self.history.append((f"Therapist: {userInput}"))
        self.history.append((f"Patient: {vpResponse}"))
        

    def getTherapistResponses(self):
        if len(self.history) <= 2:
            return []
        
        evenIndexed = [self.history[i] for i in range(len(self.history)) if i % 2 == 0]
        
        if len(evenIndexed) >= 2:
            return evenIndexed[-2:]
        else:
            return evenIndexed
    
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