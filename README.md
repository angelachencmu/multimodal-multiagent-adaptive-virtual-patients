# Multimodal multiagent couples virtual patients - EFT Couple Therapy Training Simulator

### Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **OpenAI API Key** (for GPT and TTS)

### Installation

**you may download or copy to a new branch to test if you want (optional)**

The folder "app" is for backend.

**Set up the backend:**
   ```bash
 
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   pip install -r requirements.txt
   
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

**Set up the frontend:**
   ```bash
   cd frontend
   npm install
   ```

**Start the application:**
   ```bash
   # Terminal 1 - Backend
   cd ..  # Return to the project root directory. Use 'python3' instead of 'python' if 'python' not working.
   python -m uvicorn app.main:app --reload 
   
   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

**Open your browser** to [http://localhost:3000](http://localhost:3000)
<!-- your may need to change to your port name-->

## Notes
the gernated audio files will be automatically saved in the "audio" folder just in case you need to check.

## Description

### Agent 

- **Alpha (Pursuer/Demander)**
- **Beta (Withdrawer)**

### Communication selections

- **Both**: Speak to both agents simultaneously (default)
- **Alpha**: Direct talk to Alpha.
- **Beta**: Direct talk to Beta.

### communication stages

1. **Greeting**: Initial session opening and rapport building
2. **Problem Raising**: Issues and concerns are introduced
3. **Escalation**: Conflict intensifies
4. **De-escalation**: Therapeutic intervention calms the situation
5. **Enactment**: Partners share vulnerable feelings directly
6. **Wrap-up**: Session conclusion

### EFT Skills Detected


#### Cycle De-escalation
- **Step 1**: Assessments
- **Step 2**: Identifying problem interactional cycles
- **Step 3**: Accessing underlying emotions
- **Step 4**: Reframing problems in terms of cycles and attachment needs

#### Restructuring Interactions
- **Step 5**: Promoting identification with disowned needs
- **Step 6**: Promoting partner acceptance
- **Step 7**: Facilitating emotional expression

#### Consolidation
- **Step 8**: Facilitating new solutions
- **Step 9**: Consolidating new positions

### Difficulty Levels

- **Easy**: Couple shows openness to therapeutic guidance
- **Normal**: Moderate resistance with realistic therapeutic responsiveness
- **Hard**: High defensiveness, resistance to change, quick escalation

# Multimodal adaptive virtual patient 
A virtual patient prototype based on a conversation summary and long-term memory. Built with a **Python** backend and a **React** frontend with **Tailwind CSS**.

The emotions map isn't very accurate for the first iteration since it's built on the conversation summary but the more the conversation progresses the more accurate it becomes. 

This branch experiments with replacing the STM in the model with a summary and directly inputing highly influencial developments into long term memory.

---

## Features
- Virtual Patient Chatbot
- Toggle between four character personas (Alex, Steph, Theo, and Sam)
- Display of the current short term memory and actively recalled long term repository 
- Display of basic character card information
    - Everything that is displayed is what is actively being inputed into the system

---

## Notes

- Parameters might need to be more fine tuned to have a balance between forgetfullness and tokens (length of the memory stream (currently 5), number of forgotten components ect.)

- React dev server runs on: http://localhost:3000
- Python backend defaults to: http://localhost:5000

---

## Installation & Setup

### 1. Backend (Python)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
python server.py
```
#### Set Up API Key
- Insert an .env file at the top of the multimodal_adaptive_virtual_patient folder OPENAI_API_KEY = *your key here*
- Insert an .env file at the top of the multimodal_adaptive_virtual_patient/frontend folder REACT_APP_API_URL= *your url here*
    - use "http://127.0.0.1:5000" for local host


### 2. Frontend (React)
```
cd frontend
npm install
npm start
```
