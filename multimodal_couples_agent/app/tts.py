import openai
import os
from uuid import uuid4
import re

openai.api_key = os.getenv("OPENAI_API_KEY")

AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def clean_text_for_tts(text: str) -> str:
    """
    Remove agent names and convert non-verbal cues to TTS-friendly sound effects.
    """
    # Remove agent name prefixes
    text = re.sub(r'^(Alpha|Beta):\s*', '', text, flags=re.IGNORECASE)
    
    # Map non-verbal cues to TTS-friendly sound effects, optional, can be removed if not needed
    sound_map = {
        'sighs': '*sigh*',
        'sigh': '*sigh*',
        "silence": "*sigh*",
        'groans': '*groan*',
        'groan': '*groan*',
        'shrugs': '*hmm*',
        'shrug': '*hmm*',
        'rolls eyes': '*tsk*',
        'eye roll': '*tsk*',
        'looks away': '*pause*',
        'looks down': '*pause*',
        'looks': '*pause*',
        'pauses': '*pause*',
        'pause': '*pause*',
        'crosses arms': '*hmph*',
        'leans back': '*hmm*',
        'fidgets': '*um*',
        'nods': '*mm*',
        'shakes head': '*no*',
        'laughs': '*laugh*',
        'chuckles': '*chuckle*',
        'scoffs': '*sigh*',
        'scoff': '*sigh*',
        'snorts': '*snort*'
    }
    
    def cue_replacer(match):
        cue = match.group(1).strip().lower()
        
        # Check if we have a specific sound mapping
        for phrase, sound in sound_map.items():
            if phrase in cue:
                return sound
        
        # For unmapped cues, use the first word or convert to pause
        main_cue = cue.split()[0] if cue else ''
        if main_cue in ['sits', 'stands', 'walks', 'moves', 'turns', 'glances']:
            return '*pause*'
        elif main_cue:
            return f"*{main_cue}*"
        else:
            return ''
    
    # Convert [cue ...] patterns
    text = re.sub(r'\[(.*?)\]', cue_replacer, text)
    
    # Convert (cue ...) patterns  
    text = re.sub(r'\((.*?)\)', cue_replacer, text)
    
    # Clean up existing *...* patterns to use sound mappings
    def asterisk_replacer(match):
        cue = match.group(1).strip().lower()
        for phrase, sound in sound_map.items():
            if phrase in cue:
                return sound
        return match.group(0)  # Keep original if no mapping found
    
    text = re.sub(r'\*(.*?)\*', asterisk_replacer, text)
    
    return text.strip()

def get_voice_instructions(agent_name: str, emotion: str | None) -> str:
    base_instruction = "IMPORTANT: When you see text in asterisks like *sighs*, *groans*, *shrugs*, *looks*, *pauses*, etc., DO NOT SAY THE WORDS. Instead, make the actual sound effect or pause. For example: *sighs* = make a sighing sound, *groans* = make a groaning sound, *pauses* = pause silently for 1-2 seconds, *shrugs* = make a small 'hmm' or 'eh' sound, *looks* = pause briefly. NEVER say the words inside asterisks."
    
    if agent_name == "Alpha":
        if emotion == "neutral":
            return f"Speak in a serious, subdued tone, as if you're trying to start a difficult conversation while feeling sad and holding back frustration. Let a gentle sadness color your voice, with a slight heaviness or sigh at the start of sentences. {base_instruction}"
        elif emotion == "sad":
            return f"Breathe out softly at sentence starts, you can use longer pauses (1-2 seconds) to convey heaviness or sadness, and let out a soft sigh when the feeling is heavy or difficult to express, you can also cry a bit. {base_instruction}"
        elif emotion == "angry":
            return f"Breathe out softly at sentence starts, forceful, with clear anger and edge. Let a subtle growl slip into stressed words. {base_instruction}"
        elif emotion == "frustrated_angry":
            return f"Breathe out softly at sentence starts, intense, urgent tone with underlying desperation. Voice may crack or waver between anger and pleading. Speak faster when frustrated, slower when the hurt shows through. {base_instruction}"
        elif emotion == "vulnerable":
            return f"Softer, more tentative tone. Show emotional openness and fear of being hurt. Speak with gentle hesitation, as if sharing something deeply personal. {base_instruction}"
        elif emotion == "hopeful":
            return f"Softer, more open tone. Less forceful, showing vulnerability under the anger. {base_instruction}"
        elif emotion == "relieved":
            return f"Calmer, more relaxed tone. Show some hope and relief. {base_instruction}"
        else:
            return f"Louder, more forceful, with a bit of edge. Louder and firmer. Let a subtle growl slip into stressed words. {base_instruction}"
    
    elif agent_name == "Beta":
        if emotion == "anxious":
            return f"Slow, hesitant, nervous tone. Slight tremor in voice. {base_instruction}"
        elif emotion == "defensive":
            return f"Slow, hesitant, slightly contemptuous, with defensive edge. {base_instruction}"
        elif emotion == "sad":
            return f"Quiet, strained voice showing emotional overload. May sound flat or monotone when shutting down, or shaky when hurt breaks through. Include pauses as if struggling to speak. {base_instruction}"
        elif emotion == "neutral":
            return f"Neutral tone, natrual speed. Show emotional pain and vulnerability, use sigh or groan when appropriate. {base_instruction}"
        elif emotion == "cautious":
            return f"Slow, careful, guarded tone. Show wariness and caution. {base_instruction}"
        elif emotion == "open":
            return f"More engaged and open tone. Show willingness to participate. {base_instruction}"
        elif emotion == "calm":
            return f"Relaxed, more open tone. Show gratitude and cautious optimism. {base_instruction}"
        else:
            return f"Slow, hesitant, slightly contemptuous, having sigh. {base_instruction}"
    
    return base_instruction

def text_to_speech(text: str, agent_name: str, emotion: str | None = None) -> str:
   
    voice = "sage" if agent_name == "Alpha" else "echo"
    cleaned_text = clean_text_for_tts(text)
    
    # Handle complete silence, if the response is just silence indicators, create a pause
    silence_patterns = ["...", "*stays silent*", "*silence*", "*quiet*", "*no response*"]
    if cleaned_text.strip() in silence_patterns or cleaned_text.strip() == "":
        # Create a short pause audio instead of trying to speak empty text
        cleaned_text = "*pause*"
    
    instructions = get_voice_instructions(agent_name, emotion)
    
    filename = f"{agent_name}_{uuid4().hex}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=cleaned_text,
        instructions=instructions
    ) as response:
        response.stream_to_file(filepath)
  
    return f"/audio/{filename}"

