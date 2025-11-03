async function testOllamaChat() {
  const response = await fetch("http://localhost:3000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      messages: [{ role: "user", content: "Hello Ollama!" }],
    }),
  });

  const data = await response.json();
  console.log("Response from backend:", data);
}

testOllamaChat();