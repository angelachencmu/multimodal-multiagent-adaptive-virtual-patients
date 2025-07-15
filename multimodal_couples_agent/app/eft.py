
import os
from openai import OpenAI


STAGES = [
    "Greeting",
    "Problem Raising",
    "Escalation",
    "De-escalation",
    "Enactment",
    "Wrap-up"
]

EFT_SKILLS = [
    "Cycle De-escalation",
    "Restructuring interactions",
    "Consolidation"
]

# Detailed EFT Sub-skills
EFT_SUBSKILLS = {
    "Cycle De-escalation": {
        "Step 1": {
            "name": "Assessment",
            "description": "Creating an alliance and explicating the core issues in the couple's conflict using an attachment perspective.",
            "indicators": ["building rapport", "exploring attachment needs", "identifying core issues", "creating safety", "establishing alliance"]
        },
        "Step 2": {
            "name": "Identifying the problem interactional cycle",
            "description": "Identifying the problem interactional cycle that maintains attachment insecurity and relationship distress.",
            "indicators": ["tracking patterns", "identifying cycles", "pursue-withdraw", "criticize-defend", "negative cycle", "interaction pattern"]
        },
        "Step 3": {
            "name": "Accessing underlying emotions",
            "description": "Accessing the unacknowledged emotions underlying interactional positions.",
            "indicators": ["exploring feelings", "underlying emotions", "what's underneath", "accessing emotion", "feeling behind the feeling"]
        },
        "Step 4": {
            "name": "Reframing the problem",
            "description": "Reframing the problem in terms of the cycle, the underlying emotions, and attachment needs.",
            "indicators": ["reframing", "the cycle is the problem", "attachment needs", "new perspective", "externalizing the cycle"]
        }
    },
    "Restructuring interactions": {
        "Step 5": {
            "name": "Promoting identification with disowned needs",
            "description": "Promoting identification with disowned needs and aspects of self and integrating these into relationship interactions.",
            "indicators": ["owning needs", "integrating aspects", "acknowledging needs", "self-acceptance", "disowned parts"]
        },
        "Step 6": {
            "name": "Promoting acceptance of partner's experience",
            "description": "Promoting acceptance of the partner's new construction of experience in the relationship and new responses.",
            "indicators": ["partner acceptance", "new understanding", "validating partner", "accepting change", "new responses"]
        },
        "Step 7": {
            "name": "Facilitating expression of needs",
            "description": "Facilitating the expression of specific needs and wants and creating emotional engagement.",
            "indicators": ["expressing needs", "emotional engagement", "specific wants", "direct communication", "vulnerable sharing"]
        }
    },
    "Consolidation": {
        "Step 8": {
            "name": "Facilitating new solutions",
            "description": "Facilitating the emergence of new solutions to old problematic relationship issues.",
            "indicators": ["new solutions", "problem-solving", "creative solutions", "addressing old issues", "new approaches"]
        },
        "Step 9": {
            "name": "Consolidating new positions",
            "description": "Consolidating new positions and new cycles of attachment behavior.",
            "indicators": ["consolidating change", "new positions", "new cycles", "attachment behavior", "maintaining progress"]
        }
    }
}

def get_eft_subskill_details(skill: str, step: str) -> dict:
  
    return EFT_SUBSKILLS.get(skill, {}).get(step, {})

# Use OpenAI to detect the current stage based on session history.
def detect_stage(session):

    history = session.get("history", [])
    # Use the last 5 turns for context
    context = "\n".join([
        f"Trainee: {h['trainee']}\nAlpha: {h['Alpha']}\nBeta: {h['Beta']}" for h in history[-5:]
    ])
    prompt = f"""
Given the following couple therapy conversation, identify which stage the session is currently in.

IMPORTANT: Only use "Greeting" for the very beginning of the session. Once substantive conversation has started, move to appropriate stages.
Greeting: ONLY at the very start of the session. Basic hellos, initial small talk, or opening "how are you" questions. If partners have already started discussing issues or problems, this is NOT greeting anymore.
Problem Raising: One partner introduces a complaint, stressor, or relationship issue. Partners start discussing what's wrong or what brought them to therapy. This often follows after initial greetings.
Escalation: Alpha becomes more demanding, critical, or emotional using "you always/never" statements. Beta becomes more defensive, withdrawn, or counter-attacks. Conflict is intensifying, blame is being assigned, patterns of pursue-withdraw are evident. Look for: frustration, anger, defensiveness, accusations, "you always," "you never," dismissive language, contempt, or withdrawal.
De-escalation: Trainee intervenes to calm things down. Trainee validates both sides, reframes the situation, or helps partners understand each other's perspectives. Therapist is actively managing the conflict.
Enactment: Partners are directly expressing vulnerable feelings *TO EACH OTHER* (not just to therapist). Alpha shares primary emotions like hurt or fear. Beta becomes more open and engaged. This is deeper emotional sharing between partners.
Wrap-up: Session is ending. Trainee summarizes progress, schedules next meeting, or partners express appreciation/relief about the session.

DECISION RULES:
- If partners are discussing relationship problems or issues = Problem Raising or later stages
- If there's conflict or tension = Escalation or later stages  
- If trainee is asking specific questions about the relationship = NOT Greeting
- If partners have moved past basic hellos = NOT Greeting
- If you see "you always," "you never," accusations, defensiveness, contempt, or withdrawal = Escalation
- If agents are blaming each other or being dismissive = Escalation
- If emotional intensity is high with frustration, anger, or hurt = Escalation
- If agents are talking past each other or not listening = Escalation

Choose from: {', '.join(STAGES)}.

Conversation:
{context}

Respond with only the stage name.
"""
    client = OpenAI(

        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert EFT supervisor."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=16,
        temperature=0
    )
    content = response.choices[0].message.content
    return content.strip() if content else "Greeting"

# Use OpenAI to detect which EFT skill the trainee is using in the latest message.
def detect_eft_skill(session):
  
    history = session.get("history", [])
    if not history:
        return ""
    last_trainee = history[-1]["trainee"]
    
    # Get conversation history
    context = ""
    if len(history) >= 5:
        recent_context = history[-5:]
        context = "\n".join([
            f"Trainee: {h['trainee']}\nAlpha: {h['Alpha']}\nBeta: {h['Beta']}" for h in recent_context
        ])
    elif len(history) >= 3:
        recent_context = history[-3:]
        context = "\n".join([
            f"Trainee: {h['trainee']}\nAlpha: {h['Alpha']}\nBeta: {h['Beta']}" for h in recent_context
        ])
    elif len(history) >= 2:
        recent_context = history[-2:]
        context = "\n".join([
            f"Trainee: {h['trainee']}\nAlpha: {h['Alpha']}\nBeta: {h['Beta']}" for h in recent_context
        ])
    
    prompt = f"""
You are an expert EFT (Emotionally Focused Therapy) supervisor. Analyze the trainee's intervention to identify which EFT skill is being used.

Context (recent conversation):
{context}

Current trainee intervention: "{last_trainee}"
    
EFT Skills:
1. Cycle De-escalation: 
   - Tracking and reflecting interaction patterns
   - Identifying negative cycles (pursue-withdraw, criticize-defend)
   - Slowing down escalation ("let's slow this down")
   - Pattern recognition ("I notice you both...")
   - Externalizing the cycle ("the cycle is the problem")

2. Restructuring interactions:
   - Facilitating emotional expression and engagement
   - Helping partners express needs and vulnerabilities
   - Creating new emotional experiences
   - Promoting acceptance of partner's experience
   - Integrating disowned aspects of self

3. Consolidation:
   - Recognizing and reinforcing new interaction patterns
   - Consolidating positive changes
   - Helping couples maintain progress
   - Celebrating new ways of connecting

IMPORTANT: Only identify an EFT skill if the trainee is clearly using a specific therapeutic technique. For general greetings, small talk, or basic questions without therapeutic intervention, respond with "None".

Choose from: {', '.join(EFT_SKILLS)} or "None".

Respond with only the skill name or "None".
"""
    client = OpenAI(
    
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert EFT (Emotionally Focused Therapy) supervisor with extensive experience in identifying therapeutic techniques and interventions."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=15,
        temperature=0
    )
    content = response.choices[0].message.content
    if not content:
        return ""
    content = content.strip()
    # Return empty string if the GPT says "None" or if content is not a valid EFT skill
    if content == "None" or content not in EFT_SKILLS:
        return ""
    return content

# Use OpenAI to detect which specific EFT sub-skill step the trainee is using. Returns a dictionary with skill, step, name, and description.
def detect_eft_subskill(session):
   
    history = session.get("history", [])
    if not history:
        return {}
    
    last_trainee = history[-1]["trainee"]
    
    # Get (last 5 turns) for detection
    context = ""
    if len(history) >= 5:
        recent_context = history[-5:]
        context = "\n".join([
            f"Trainee: {h['trainee']}\nAlpha: {h['Alpha']}\nBeta: {h['Beta']}" for h in recent_context
        ])
    elif len(history) >= 3:
        recent_context = history[-3:]
        context = "\n".join([
            f"Trainee: {h['trainee']}\nAlpha: {h['Alpha']}\nBeta: {h['Beta']}" for h in recent_context
        ])
    elif len(history) >= 2:
        recent_context = history[-2:]
        context = "\n".join([
            f"Trainee: {h['trainee']}\nAlpha: {h['Alpha']}\nBeta: {h['Beta']}" for h in recent_context
        ])
    
    # detailed prompt/instructions with all sub-skills and indicators
    subskill_descriptions = []
    for skill, steps in EFT_SUBSKILLS.items():
        for step, details in steps.items():
            indicators_text = ", ".join(details['indicators'])
            subskill_descriptions.append(f"{skill} - {step}: {details['name']}")
            subskill_descriptions.append(f"  Description: {details['description']}")
            subskill_descriptions.append(f"  Key indicators: {indicators_text}")
            subskill_descriptions.append("")
    
    prompt = f"""
You are an expert EFT supervisor. Analyze the trainee's intervention to identify the specific EFT sub-skill step being used.

Context (recent conversation):
{context}

Current trainee intervention: "{last_trainee}"

EFT Sub-skills with indicators:
{chr(10).join(subskill_descriptions)}

Instructions:
1. Look for key indicators in the trainee's language and therapeutic intent
2. Consider the context of the conversation and what the trainee is trying to accomplish
3. Match the intervention to the most specific sub-skill step
4. Even if the exact wording doesn't match, consider the therapeutic technique being used

Examples of what to look for:
- Assessment: Building rapport, creating safety, exploring issues
- Identifying cycles: Pointing out patterns, pursue-withdraw dynamics
- Accessing emotions: Exploring feelings, "what's underneath"
- Reframing: New perspective, "the cycle is the problem"
- Expressing needs: Facilitating vulnerable sharing, direct communication
- Acceptance: Validating partner's experience, promoting understanding

Respond with the format: "SKILL - STEP" (e.g., "Cycle De-escalation - Step 2" or "Restructuring interactions - Step 7")
If no specific sub-skill is evident, respond with "None".
"""
    
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert EFT (Emotionally Focused Therapy) supervisor with extensive experience in identifying specific therapeutic techniques and sub-skills. You are precise and accurate in your assessments. Focus on the therapeutic intent and technique, not just exact word matching."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50,  
        temperature=0.1  
    )
    
    content = response.choices[0].message.content
    if not content:
        return {}
    content = content.strip()
    
    # Parse the AI's response
    if content == "None":
        return {}
    
    if " - " not in content:
        return {}
    
    try:
       
        parts = content.split(" - ", 1)
        if len(parts) != 2:
            return {}
        
        skill, step = parts
        skill = skill.strip()
        step = step.strip()
        
       
        if skill in EFT_SUBSKILLS and step in EFT_SUBSKILLS[skill]:
            details = EFT_SUBSKILLS[skill][step]
            result = {
                "skill": skill,
                "step": step,
                "name": details["name"],
                "description": details["description"]
            }
            return result
        else:
            return {}
            
    except Exception as e:
        return {}
    
    return {}

def get_all_eft_subskills():
    """
    Return the complete EFT sub-skills mapping for frontend display.
    """
    return EFT_SUBSKILLS 