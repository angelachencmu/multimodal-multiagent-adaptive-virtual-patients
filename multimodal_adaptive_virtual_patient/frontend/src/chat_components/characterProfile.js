import SEMSettingsForm from './characterForm';

export default function CharacterProfile({ changeCharacter, characterCard }) {
  return (
    <div className="flex flex-col h-full p-4 w-full gap-5 overflow-y-auto transparent-scrollbar">
        <div className="flex-none flex flex-col border p-5 rounded-xl shadow bg-white w-full text-center">
            <h1 className="text-purple uppercase font-bold tracking-wide mb-5 text-xl">Character Selection</h1>
            <div className="flex gap-2">
                <button
                    onClick={() => changeCharacter("Alex")}
                    className="mt-2 px-4 py-2 rounded-full bg-purple tracking-wide border-4 border-solid duration-300 border-purple text-white w-1/2 hover:tracking-wider hover:bg-white hover:text-purple"
                >
                <h2 className="uppercase font-bold">Alex</h2>
                </button>
                <button
                    onClick={() => changeCharacter("Steph")}
                    className="mt-2 px-4 py-2 rounded-full bg-coral tracking-wide border-4 border-solid duration-300 border-coral text-white w-1/2 hover:tracking-wider hover:bg-white hover:text-coral"
                >
                    <h2 className="uppercase font-bold">Steph</h2>
                </button>
            </div>
            <div className="flex gap-2">
                <button
                    onClick={() => changeCharacter("Theo")}
                    className="mt-2 px-4 py-2 rounded-full bg-teal tracking-wide border-4 border-solid duration-300 border-teal text-purple w-1/2 hover:tracking-wider hover:bg-white hover:text-teal"
                >
                    <h2 className="uppercase font-bold">Theo</h2>
                </button>
                <button
                    onClick={() => changeCharacter("Sam")}
                    className="mt-2 px-4 py-2 rounded-full bg-blue tracking-wide border-4 border-solid duration-300 border-blue text-purple w-1/2 hover:tracking-wider hover:bg-white hover:text-blue"
                >
                    <h2 className="uppercase font-bold">Sam</h2>
                </button>
            </div>
        </div>
        <div className="flex-none flex flex-col border p-4 rounded-xl shadow bg-white w-full text-purple">
            <h1 className="uppercase font-bold tracking-wide mb-5 text-xl"> Character Information </h1>
            <h2><strong>Name: </strong>{characterCard.name}</h2>
            <h2><strong>Identity:</strong></h2>
            <ul className="list-disc ml-5">
            {characterCard.identity?.map((item, index) => (
                <li key={index}>{item}</li>
            ))}
            </ul>
            <h2><strong>Key Background:</strong></h2>
            <ul className="list-disc ml-5">
            {characterCard.keyBackground?.map((item, index) => (
                <li key={index}>{item}</li>
            ))}
            </ul>
            <h2><strong>Personality: </strong>{characterCard.personality}</h2>
            <h2><strong>Context: </strong></h2>
            <ul className="list-none">
                {(characterCard.context ?? "(none)")
                    .split('\n')
                    .map((line, index) => (
                    <li key={index}>{line}</li>
                ))}
            </ul>
        </div>
        <div className="flex-none flex flex-col border p-4 rounded-xl shadow bg-white w-full">
            <SEMSettingsForm/>
        </div>
    </div>
  );
}
