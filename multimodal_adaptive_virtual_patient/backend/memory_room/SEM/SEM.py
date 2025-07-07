import re

from flask import json
import gpt

class SEM:

    # TODO after SiWei implements SEM adjustments
    def __init__(self):
        self.emotion = []
        self.depression = []
        self.empathy = []
        return
    
    def get_empathy_evaluation(self, vp_empathy_context, therapist_input):
        prompt = (
            "You are a professional evaluator specializing in assessing therapist empathy. Your evaluations are based on clinical best practices, focusing on accuracy, nuance, and consistency."
            " Evaluate the therapist's response for empathy based on the virtual patient's speech. Assign ratings for 3 empathy mechanisms Emotional Reactions, Interpretations, and Explorations based on their definitions and criteria.\n\n"

            "3 Empathy Mechanisms Definitions & Evaluation Criteria:\n"
            "- Emotional Reactions: Showing warmth or concern.\n"
            "  - Strong:  Explicitly specifies emotions (e.g., 'I feel really sad for you').\n"
            "  - Weak: Vague reassurance (e.g., 'It'll be fine').\n"
            "  - None: No emotional reaction.\n"
            "- Interpretations: Understanding of the client's emotions.\n"
            "  - Strong: Infers specific feelings or shared experiences.\n"
            "  - Weak: Generic acknowledgment (e.g., 'I understand').\n"
            "  - None: Ignores the client’s emotions.\n"
            "- Explorations: Encouraging deeper reflection.\n"
            "  - Strong: Direct, labeled questions (e.g., 'Are you feeling alone?').\n"
            "  - Weak: Generic questions (e.g., 'What happened?').\n"
            "  - None: No inquiry.\n"

            "Please return your analysis in the following JSON format:\n"
            "{\n"
            '  "explanation": "Justify your ratings in ≤ 70 words using evidence from the utterance.",\n'
            '  "emotional_reactions": 0 | 1 | 2,\n'
            '  "interpretations": 0 | 1 | 2,\n'
            '  "explorations": 0 | 1 | 2\n'
            "}\n\n"
        )

        messages = [{"role" : "system",
            "content": prompt,
            }]
        empathy, messages = gpt.queryGPT(
            messages,
            message= f"Context:\n{vp_empathy_context}\n\n Therapist says: \"{therapist_input}\"\n\n"
        )

        parsedEmpathy = self.parse_empathy_json(empathy)
        self.empathy.append(parsedEmpathy)
    

    def parse_empathy_json(self, response_text):
        """
        Safely parse the JSON returned by the LLM for empathy evaluation.

        Parameters:
            response_text (str): The raw LLM output (expected JSON format)
        Returns:
            dict: Parsed JSON with empathy scores and explanation,
                or a fallback dictionary if parsing fails.
        """
        try:
            cleaned = re.sub(r"^```(?:json)?|```$", "", response_text.strip(), flags=re.MULTILINE)
            parsed = json.loads(cleaned)

            required_keys = {"explanation", "emotional_reactions", "interpretations", "explorations"}
            if not required_keys.issubset(parsed.keys()):
                raise ValueError("Missing required empathy keys")
            for key in ["emotional_reactions", "interpretations", "explorations"]:
                if parsed[key] not in [0, 1, 2]:
                    raise ValueError(f"Invalid score for {key}: {parsed[key]}")

            return parsed

        except Exception as e:
            return {
                "error": "Failed to parse empathy evaluation JSON.",
                "raw_response": response_text,
                "exception": str(e)
            }
        
    def detect_depression(self, vp_text):
        """
        Detect depression from a virtual patient's response.
        """

        messages = [{"role" : "system",
            "content":"Based on the emotional tone and language of the following virtual patient response, categorize their level of depression using one of the following labels only: None, Low, Moderate, High, Severe.",
            }]
        depression, messages = gpt.queryGPT(
            messages,
            message=f"Response: \"{vp_text}\" Depression Level:"
        )

        self.depression.append(depression)

    
    def detect_emotion(self, vp_text):
        """
        Detect emotion from a virtual patient's response.
        """

        messages = [{"role" : "system",
            "content":"Identify the emotional tone in the following virtual patient response. Return only one word",
            }]
        emotion, messages = gpt.queryGPT(
            messages,
            message=f"Response: \"{vp_text}\"\n\nEmotion:"
        )

        self.emotion.append(emotion)