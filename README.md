# Multimodal multiagent couples virtual patients 
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
