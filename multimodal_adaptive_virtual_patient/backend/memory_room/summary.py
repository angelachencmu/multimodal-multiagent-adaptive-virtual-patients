import gpt as gpt

class Summary:
    def __init__(self):
        self.summaryHistory = []
    
    # a new summary is created every 6 turns 
    def createSummary(self, history):
        messages = [{"role" : "system",
        "content":"You are an expert psychotherapy observer. Summarize the key changes in the virtual patient's emotional state "
        "and describe how the therapist's actions influenced them.\n\n"
        "2-3 sentence summary only.\n\n",
        }]
        summary, messages = gpt.queryGPT(
            messages,
            message=f"Return a couple sentence summary of the current conversation: {self.recentMemories}"
        )
        self.summaryHistory.append(summary)

    # returns and formats the summary as a string:
    # Checkpoint 1: ...
    # Checkpoint 2: ...
    # Checkpoint n: ...
    def toString(self):
        summaryString = ""
        for i in range(len(self.summaryHistory)):
            summaryString += f"Checkpoint {i}: {self.summaryHistory[i]} \n"
        return summaryString