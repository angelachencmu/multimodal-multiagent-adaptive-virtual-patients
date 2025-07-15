import { useState } from "react";
import Chat from "./chat_components/chat";
import CharacterProfile from "./chat_components/characterProfile";

export default function App() {
  // Shared state
  const [messages, setMessages] = useState([]);
  const [selected, setSelected] = useState(false);
  const [characterCard, setCharacterCard] = useState({
    name: "",
    identity: [],
    keyBackground: [],
    personality: "",
    session: 0,
    context: ""
  });
  const [isLoading, setIsLoading] = useState(false);

  const updateSession = (characterCard) => {
    setCharacterCard(characterCard);
    console.log(characterCard.context);
  };

  const resetCharacter = async() => {
    try {
        setIsLoading(true);
        setSelected(false);
        const response = await fetch(`${process.env.REACT_APP_API_URL}/reset-character`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: "true" }),
        });

        const data = await response.json();
        setCharacterCard(data.characterCard);
        console.log(data.characterCard);

        // Clear chat and name on character switch
        setMessages([]);
        setIsLoading(false);
        setSelected(true);
    } catch (error) {
        console.error("Failed to fetch:", error);
    }
  }


  // Change character and clear chat
  const handleChangeCharacter = async (characterName) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/change-character`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ character: characterName }),
      });

      const data = await response.json();
      setCharacterCard(data.characterCard);
      console.log(data.characterCard);

      // Clear chat and name on character switch
      setMessages([]);
      setSelected(true);
      console.log(selected);
    } catch (error) {
      console.error("Error changing character:", error);
    }
  };

  return (
    <div className="flex bg-blue p-5 h-screen">
      <div className="h-[95vh] w-1/4">
        <CharacterProfile
          changeCharacter={handleChangeCharacter}
          characterCard={characterCard}
        />
      </div>
      <div className="h-[95vh] w-3/4">
        <Chat
        selected={selected}
        messages={messages}
        setMessages={setMessages}
        name={characterCard.name}
        session={characterCard.session}
        updateSession={updateSession}
        resetCharacter={resetCharacter}
        isLoading={isLoading}
        setIsLoading={setIsLoading}
      />
      </div>
    </div>
  );
}
