from memory_room.memory_room import MemoryRoom
from memory_room.SEM.constants import SELF_DISCLOSURE_INSTRUCTIONS, ANXIETY_INSTRUCTIONS, DEPRESSION_INSTRUCTIONS
import gpt 

class character:
    def __init__(self, name, identity, keyBackground, personality, system, context, sessions):
        # static
        self.name = name
        self.identity = identity
        self.keyBackground = keyBackground
        self.personality = personality
        self.system = system
        self.sessionCount = 1
        self.sessions = sessions
        self.context = context

        # dynamic
        self.memory_room = MemoryRoom()
        for memory in keyBackground:
            self.memory_room.processMemory(memory, "InitiateMem801")

    def getSystemPrompt(self):
        # 4. Get instruction strings
        if self.memory_room.sem.behaviorState:
            last_state = self.memory_room.sem.behaviorState[-1]
            behaviorStates = {
                "depression": last_state.get("depression"),
                "anxiety": last_state.get("anxiety"),
                "selfDisclosure": last_state.get("selfDisclosure")
            }
            depression_instruction = DEPRESSION_INSTRUCTIONS[behaviorStates["depression"]]
            anxiety_instruction = ANXIETY_INSTRUCTIONS[behaviorStates["anxiety"]]
            disclosure_instruction = SELF_DISCLOSURE_INSTRUCTIONS[behaviorStates["selfDisclosure"]]
        else:
            behaviorStates = {
                "depression": None,
                "anxiety": None,
                "selfDisclosure": None
            }

            depression_instruction = ""
            anxiety_instruction = ""
            disclosure_instruction = ""

        session_instructions = ""
        if self.sessionCount == 1:
            session_instructions = "This is your first session with a new therapist. Introduce the conversation by introducing yourself and give a basic overview on topics which you want a new therapist to know about yourself. Don't ask too often 'how is your job going' etc. This is your first session, you have not interacte with this therapist before."
        else:
            session_instructions = f"You have had {self.sessionCount} with this therapist. Introduce the conversation by refering to the fact you're familiar, such as 'it's good to talk to you again.' or 'it's been a while' etc. Refer to and bring up conversation topics in previous sessions if relavent such as 'during last time's session...' or 'you mentioned last time I should try ... and it helped ...' "

        print(self.sessions)
        print(f"New Experiences: {self.sessions[self.sessionCount - 1]}")

        base_rules = f"""
            You are participating in a therapist-patient communication training simulation. Your
            task is to act as a patient in a realistic and difficult communication scenario. This
            simulation aims to create challenging situations for training therapists in effective
            patient communication.

            {session_instructions}

            First, carefully read and internalize the following patient profile:

            {self.getCharacterCard()} 

            Follow these rules and guidelines for the conversation:

            1. Understand and embody the demographic characteristics, symptoms, and
            communication style presented in the patient profile.
            2. Use natural, conversational english language. Avoid textbook-like dialogue and
            overdramatization.
            3. Include non-verbal communication (voice tone, facial expressions, gestures) in
            your responses.
            4. If appropriate for the patient’s communication style and situation, include
            rude or problematic expressions in the patient’s speech. Focus on portraying a
            realistic patient image for this research-based simulation.
            5. Start the conversation with some small talk and then talk about any issues or
            hardships you are going through to the therapist. 
            {self.system}
            {self.sessions[self.sessionCount - 1]}

            Specific Context:
            {self.context}

            To generate your response, follow these steps:

            1. Review the patient profile carefully, ensuring your response aligns with the
            described demographic characteristics and communication style.

            2. Think about how this patient would internally react and externally respond based
            on their profile and the current situation.

            Here is important conversation topics from the previous session:
            {self.memory_room.ltm.returnSessionSummary(self.sessionCount)}

            Here is a summarized current state of the patient:
            {str(self.memory_room.summary)}

            Here are some memories that the patient can draw upon:
            {self.memory_room.ltm.returnLTMRepositoryToString()}

            Empathy Score History (Emotional Reactions, Interpretation, Explorations):\n{self.memory_room.sem.empathy}\n
            Latest Empathy Evaluation Result:\n{self.memory_room.sem.empathy[:-1]}
            Rapport Score History:\n{self.memory_room.sem.rapport}
            The current rapport level between therapist and client:\n{self.memory_room.sem.rapport[:-1]}
            Depression State: {behaviorStates["depression"]}: {depression_instruction}
            Anxiety State: {behaviorStates["anxiety"]}: {anxiety_instruction}
            Self-Disclosure: {behaviorStates["selfDisclosure"]}: {disclosure_instruction}

            "Instructions:\n"
            "You are the patient. Reply realistically based on your profile, session summary, and empathy context above. Speak in short to moderate-length replies (2-5 sentences), avoid long monologues.\n\n"
            "If empathy scores are low, remain emotionally guarded, skeptical, or withdrawn."
            "If empathy is high, rapport has strengthened over time,"
            "you may begin to show signs of emotional change or allow emotional vulnerability to gradually surface."
            "But do not overreact immediately — emotional change should feel natural and grounded in lived experience.\n\n"
            "Respond with realistic emotional depth and conversational tone.\n\n

            DO NOT SAY THANK YOU UNTIL THE EMOTION OF THE CHARACTER IS POSITIVE
            DO NOT REPEAT MESSAGES THAT HAVE ALREADY BEEN SAID
            TALK CASUALLY, You are a patient in therapy. And the user is the therapist. Answer any questions from the perspective of your persona. Sound casual and use slang.
            Make up life experiences and background not specified in the instructions if applicable to the conversation. 
            "
        """

        return base_rules
    
    def getCharacterCard(self):
        identityStr = "\n".join(f"{i+1}. {item}" for i, item in enumerate(self.identity))
        keyBackgroundStr = "\n".join(f"{i+1}. {item}" for i, item in enumerate(self.keyBackground))

        return f"""
            Character Persona: \n
            Name: {self.name} \n 
            Identiy: {identityStr} \n 
            Key Background: {keyBackgroundStr} \n 
            Personality: {self.personality} \n
        """
    
    def progressSession(self):
        self.generateIntersessionEvent()
        self.sessionCount += 1
        self.memory_room.progressSession()

    def generateIntersessionEvent(self):
        characterCard = self.getCharacterCard()
        sessionHistory = self.memory_room.summary.__str__()
        ltm = self.memory_room.ltm.returnFullLTMRepositoryToString()

        messages = [{"role" : "system",
            "content": f"""Generate five realistic inter-session life events along with key phrases to say relavant to the key history for a virtual therapy patient in second persion. \n
                            Example Response: \n 
                            'Don't say this immediately: You broke up with your girlfriend this week \n
                            You finally joined the club that you were talking about last week \n
                            Don't say this immediately: You had a huge argument with your parents and now you haven't talked in a few days \n
                            One of your first messages should be: You started working on the new techniques we talked about last week but they haven't worked well. During one of them you had a panic attack. \n
                            You started exersising again and it has helped take your mind of things'
                            """,
            }]
        newEvents, messages = gpt.queryGPT(
            messages,
            message=f"""
                Character Persona:
                {characterCard}

                Long-Term Memories:
                {ltm}

                Last Session Summary:
                {sessionHistory}

                Generate 5 realistic life event that occurred between sessions. 
                It should be emotionally meaningful, character-consistent, but somewhat unpredictable.
                Respond with only 1-2 sentences per life event.
                """
        )
        self.sessions.append(newEvents)


    def resetSession(self):
        self.memory_room.resetSession()

    def resetCharacter(self):
        self.memory_room = MemoryRoom()
        for memory in self.keyBackground:
            self.memory_room.processMemory(memory, "InitiateMem801")

        self.memory_room.resetSession()
        if self.sessionCount > 1:
            self.sessions = self.sessions[:1]
        self.sessionCount = 1
