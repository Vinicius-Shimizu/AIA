export async function getOllamaResponse(query) {
  const response = await fetch("http://127.0.0.1:11434/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "aia",
      messages: query,
      stream: false,
    }),
  });

  const data = await response.json();
  return data.message.content;
}