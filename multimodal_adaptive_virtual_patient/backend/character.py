from memory_room.memory_room import MemoryRoom

class character:
    def __init__(self, name, identity, keyBackground, personality, system, context):
        # static
        self.name = name
        self.identity = identity
        self.keyBackground = keyBackground
        self.personality = personality
        self.system = system

        # dynamic
        self.memory_room = MemoryRoom()

        # updated between each session 
        self.ogContext = context
        self.context = context

    def updateSystem(self):
        base_rules = f"""
            You are participating in a therapist-patient communication training simulation. Your
            task is to act as a patient in a realistic and difficult communication scenario. This
            simulation aims to create challenging situations for training therapists in effective
            patient communication.

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
            {self.system}

            To generate your response, follow these steps:

            1. Review the patient profile carefully, ensuring your response aligns with the
            described demographic characteristics and communication style.

            2. Think about how this patient would internally react and externally respond based
            on their profile and the current situation.

            Here is a summarized current state of the patient:
            {self.memory_room.summary.toString()}

            Here are some memories that the patient can draw upon:
            {self.memory_room.ltm.returnLTMRepository(self.memory_room.SEM.emotion)}

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
        
        #TODO: add SEM components into prompt
        #The following is a simulated psychotherapy session between a therapist and a virtual patient.\n\n
        # Latest Empathy Evaluation Result:\n{char.getEmpathy()}\n\n
        # The current rapport level between therapist and client:\n{char.getRapport()}\n\n
        # f"Empathy Score History (Emotional Reactions, Interpretation, Explorations):\n{empathy_score_history}\n"
        # f"Latest Empathy Evaluation Result:\n{json.dumps(empathy_score, indent=2)}\n\n"
        # f"Rapport Score History:\n{rapport_score_history}\n"
        # f"The current rapport level between therapist and client:\n{json.dumps(rapport_score, indent=2, sort_keys=True)}\n\n"
        return base_rules
    
    def getCharacterCard(self):
        return f"""
            Character Persona: \n
            Name: {self.name} \n 
            Identiy: {self.identity} \n 
            Key Background: {self.keyBackground} \n 
            Personality: {self.personality} \n
            Context: {self.context}
        """
    
    def resetCharacter(self):
        self.memory_room = memory.MemoryRoom()
        self.context = self.ogContext