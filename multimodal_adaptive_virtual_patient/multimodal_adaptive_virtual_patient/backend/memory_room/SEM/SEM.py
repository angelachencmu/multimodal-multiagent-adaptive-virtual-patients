import copy
import re

from flask import json
import gpt
from .constants import DEFAULT_CONFIG

class SEM:

    # TODO after SiWei implements SEM adjustments
    def __init__(self):
        self.emotion = []
        self.depression = []
        self.empathy = []
        self.rapport = []
        self.rapportBlended = []
        self.behaviorState = []

    def setBehaviorState(self, depression, anxiety, selfDisclosure):
        self.behaviorState.append({"depression": depression, "anxiety": anxiety, "selfDisclosure": selfDisclosure})
    
    def setBlendedRapport(self, empathy, blended):
        self.rapportBlended.append({"empathy": empathy, "blended": blended})
    
    def get_rapport_evaluation(self, formatted_segment):
        """
        Generate a rapport evaluation prompt using at most 3 therapist–VP turn pairs (6 utterances).
        """

        prompt = (
            "Act like an expert conversation evaluator with over 20 years of experience in assessing the therapeutic alliance "
            "between clients and therapists. You are skilled in identifying subtle conversational cues and non-verbal indicators "
            "within dialogue. Your expertise includes analyzing speech patterns, emotional tone, and implicit affirmations to "
            "evaluate the depth of the bond. Your analysis must be thorough, objective, and based on specific criteria using "
            "a detailed 7-point Likert scale.\n\n"

            "You will analyze the conversation for the following four bond aspects:\n"
            "1. Mutual Liking: There is a mutual liking between the client and therapist.\n"
            "2. Confidence: The client feels confident in the therapist's ability to help the client.\n"
            "3. Appreciation: The client feels that the therapist appreciates him/her as a person.\n"
            "4. Mutual Trust: There is mutual trust between the client and therapist.\n\n"

            "Use the following 7-point Likert scale for each aspect:\n"
            "1: Very strong evidence against\n"
            "2: Considerable evidence against\n"
            "3: Some evidence against\n"
            "4: No evidence\n"
            "5: Some evidence\n"
            "6: Considerable evidence\n"
            "7: Very strong evidence\n\n"

            f"Conversation log:\n{formatted_segment}\n\n"

            "Please return your analysis in the following JSON format:\n"
            "{\n"
            '  "explanation": "your brief explanation here",\n'
            '  "overall_rating": int (1–7),\n'
            '  "mutual_liking": int,\n'
            '  "confidence": int,\n'
            '  "appreciation": int,\n'
            '  "mutual_trust": int\n'
            "}"

        )

        messages = [{"role" : "system",
            "content": prompt,
            }]
        rapport, messages = gpt.queryGPT(
            messages,
            message= f"Conversation log:\n{formatted_segment}\n\n"
        )

        parsedRapport = self.parse_rapport_json(rapport)
        self.rapport.append(parsedRapport)
    
    def parse_rapport_json(self, response_text):
        """
        Safely parse the JSON returned by the LLM for rapport evaluation.
        
        Parameters:
            response_text (str): The raw LLM output (expected JSON format)

        Returns:
            dict: Parsed JSON if valid, or error fallback with raw text.
        """
        try:
            cleaned = re.sub(r"^```(?:json)?|```$", "", response_text.strip(), flags=re.MULTILINE)
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse rapport score JSON.",
                "raw_response": response_text
            }
    
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
        return parsedEmpathy
    
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

    def compute_behavior_states(self, empathy_score, rapport_score=None, config_override=None):
        config = copy.deepcopy(config_override)
        if config_override:
            self.deep_update(config, config_override)
        
        difficulty = config.get("difficulty_coefficient", 1.0)


        ew = config["empathy_weights"]
        print("ew =", ew)
        print("type(ew) =", type(ew))

        print("em =", empathy_score)
        print("type(em) =", type(empathy_score))

        weighted_empathy = (
            ew["emotional_reactions"] * empathy_score["emotional_reactions"] +
            ew["interpretations"] * empathy_score["interpretations"] +
            ew["explorations"] * empathy_score["explorations"]
        )


        #Empathy-to-Rapport Mapping (Normalized to [1–7], centered at 4.5)
        rmw = config["rapport_mapping_weights"]
        i = empathy_score.get("interpretations", 0)
        e = empathy_score.get("explorations", 0)
        r = empathy_score.get("emotional_reactions", 0)
        max_score = 2
        total_weight = sum(rmw.values())

        if total_weight == 0:
            normalized_raw = 0  # fallback if weights are misconfigured
        else:
            normalized_raw = (
                rmw["interpretations"] * i +
                rmw["explorations"] * e +
                rmw["emotional_reactions"] * r
            ) / (total_weight * max_score)

        #center normalized score at 4.5 (Likert midpoint) scaled to [1–7]
        empathy_rapt_score = 3.0 * normalized_raw + 2
        empathy_rapt_score = max(1.0, min(7.0, empathy_rapt_score))


        #blended rapport
        llm_rapport = 4.0  # Default neutral
        if rapport_score:
            sub_scores = [
                rapport_score.get("mutual_liking"),
                rapport_score.get("confidence"),
                rapport_score.get("appreciation"),
                rapport_score.get("mutual_trust")
            ]
            valid_scores = [float(s) for s in sub_scores if isinstance(s, (int, float))]
            if valid_scores:
                llm_rapport = sum(valid_scores) / len(valid_scores)

        alpha = config.get("rapport_blend_weight", 0.7)
        blended_rapport = alpha * llm_rapport + (1 - alpha) * empathy_rapt_score
        blended_rapport = max(1.0, min(7.0, blended_rapport))

        # new mapping equation: scale * score + constant
        depr_score = config["depression_mapping"]["scale"] * blended_rapport + config["depression_mapping"]["constant"]
        anxi_score = config["anxiety_mapping"]["scale"] * blended_rapport + config["anxiety_mapping"]["constant"]
        disclosure_score = config["self_disclosure_mapping"]["scale"] * empathy_score["explorations"] + config["self_disclosure_mapping"]["constant"]

        # debug (could be removed later)
        print("[DEBUG] Behavior score mapping:")
        print(f"  Blended Rapport Score = {blended_rapport:.2f}")
        print(f"  Depression = {config['depression_mapping']['scale']} * {blended_rapport:.2f} + {config['depression_mapping']['constant']} = {depr_score:.2f}")
        print(f"  Anxiety    = {config['anxiety_mapping']['scale']} * {blended_rapport:.2f} + {config['anxiety_mapping']['constant']} = {anxi_score:.2f}")
        print(f"  Exploration Score = {empathy_score.get('explorations', 0)}")
        print(f"  Self-Disclosure = {config['self_disclosure_mapping']['scale']} * {empathy_score.get('explorations', 0)} + {config['self_disclosure_mapping']['constant']} = {disclosure_score:.2f}")

        # mapping depression, anxiety, self-disclosure states
        depression_state = self.resolve_level(depr_score, config["depression_thresholds"])
        anxiety_state = self.resolve_level(anxi_score, config["anxiety_thresholds"])
        self_disclosure_state = self.resolve_level(disclosure_score, config["self_disclosure_thresholds"])


        return {
            "depression_state": depression_state,
            "anxiety_state": anxiety_state,
            "self_disclosure_state": self_disclosure_state,
            "blended_rapport": blended_rapport,
            "empathy_rapt_score": empathy_rapt_score,
            "weighted_empathy": weighted_empathy
        }
    
    def deep_update(self, d, u):
        for k, v in u.items():
            if isinstance(v, dict) and k in d:
                self.deep_update(d[k], v)
            else:
                d[k] = v

    def resolve_level(self, value, thresholds: dict, difficulty=1.0):
        adjusted = {label: cutoff * difficulty for label, cutoff in thresholds.items()}
        for label, cutoff in adjusted.items():
            if value >= cutoff:
                return label
        return list(adjusted.keys())[-1]