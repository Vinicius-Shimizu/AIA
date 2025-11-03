import { useState, useRef } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import MessageBox from './components/MessageBox'
import InputBox from './components/InputBox'
import SendButton from './components/SendButton'

function App() {
  const [messages, setMessages] = useState([]);
  const inputRef = useRef(null);
  const [isLoading, setIsLoading] = useState(false);

  const getOllamaResponse = async () => {
    const query = inputRef.current?.getValue?.();
    if(!query || query.trim() === "") return;

    setMessages((prev) => [...prev, {sender: "user", content: query.trim() }]);
    inputRef.current.clear?.();
    setIsLoading(true);

    try{
      const res = await fetch("http://localhost:3000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [{ role: "user", content: query }],
        }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, {sender: "ollama", content: data.message || "No response"}])
    }catch(err){
      console.error("Error calling API: ", err)
    }finally{
      setIsLoading(false)
    }
  }

  return (
      <div className="flex min-h-screen justify-center bg-stone-800">
        <div className="flex flex-col justify-between border border-stone-300 w-[1200px] h-[900px] m-4 rounded-lg">
          <div className="h-[750px] overflow-auto">
            {messages.map((msg, idx) => (
              <MessageBox key={idx} sender={msg.sender} content={msg.content}/>
            ))}
            {isLoading && <MessageBox sender="ollama" content="Thinking..." />}
          </div>
          <div className="flex items-center justify-center">
            <InputBox ref={inputRef}/>
            <SendButton onClick={getOllamaResponse}/>  
          </div>
        </div>
      </div>
    );
}

export default App
