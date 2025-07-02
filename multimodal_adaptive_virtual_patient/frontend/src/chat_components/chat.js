import { PaperAirplaneIcon } from '@heroicons/react/24/solid';
import { UserCircleIcon } from '@heroicons/react/24/solid';
import { FaRobot } from 'react-icons/fa';

export default function Chat() {
  return (
    <div className="border p-4 rounded-xl shadow bg-lightGray w-full h-full">
        <div className="bg-white p-5 h-[90%] overflow-y-auto rounded-t-lg">
            <div class="flex justify-end mb-4 w-auto">
                <div
                class="mr-2 py-3 px-4 bg-coral rounded-bl-3xl rounded-tl-3xl rounded-tr-xl text-white"
                >
                Welcome to group everyone !
                </div>
                <UserCircleIcon className="flex-shrink-0 h-10 w-10 text-coral" />
            </div>
            <div class="flex justify-start mb-4">
                <FaRobot className="flex-shrink-0 h-10 w-10 text-blue" />
                <div
                    class="ml-2 py-3 px-4 bg-blue rounded-br-3xl rounded-tr-3xl rounded-tl-xl text-white"
                >
                    Lorem ipsum dolor sit amet consectetur adipisicing elit. Quaerat
                    at praesentium, aut ullam delectus odio error sit rem. Architecto
                    nulla doloribus laborum illo rem enim dolor odio saepe,
                    consequatur quas?
                </div>
            </div>  
        </div>
        <div className="flex bg-teal p-2 items-center justify-center rounded-b-lg h-[10%]">
            <input
            type="text"
            placeholder="Type your message..."
            className="border mt-2 p-2 w-full rounded-xl"
            />
            <button
                className={`px-4 py-2 rounded }`}>
                <PaperAirplaneIcon className="h-8 w-8 text-white" />
            </button>  
        </div>
    </div>
  );
}
