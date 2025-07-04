export default function CharacterMemory({ memoryInfo }) {
  return (
    <div className="flex flex-col h-full px-5 w-full gap-5 overflow-y-auto transparent-scrollbar">
      <div className="flex-none flex flex-col gap-5 border p-4 rounded-xl shadow bg-coral w-full text-white">
        <h1 className="uppercase font-bold tracking-wide mb-5 text-xl">Memory Information</h1>
        <div className="flex-none flex flex-col border p-4 rounded-xl shadow bg-white w-full text-coral">
          <h2 className="uppercase font-bold tracking-wide mb-5 text-lg">Session Summary</h2>
          <p>{memoryInfo.summary ?? "(none)"}</p>
        </div>
        <div className="flex-none flex flex-col border p-4 rounded-xl shadow bg-white w-full text-coral">
          <h2 className="uppercase font-bold tracking-wide mb-5 text-lg">Long Term Memory</h2>
          <h3><strong>Current Repository:</strong> {memoryInfo.currentRepo ?? "(none)"} </h3>
          <h3 className="font-bold">Full Repository</h3>
          <p>{memoryInfo.fullRepo ?? "(none)"}</p>
        </div>
      </div>
      <div className="flex-none flex flex-col h-96 border p-4 rounded-xl shadow bg-teal w-full text-white">
        <h1 className="uppercase font-bold tracking-wide mb-5 text-xl">SEM Information</h1>
      </div>
    </div>
  )
}
