import express from "express";
import cors from "cors";
import {spawn} from "child_process";

const app = express();
app.use(express.json());
app.use(cors());

const PORT = 3000;

async function getOllamaResponse(query){
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
  const assistantContent = data.message.content;
  return assistantContent;
} 

async function startSTTService() {
  const stt = spawn("python", ["-u", "stt_engine.py"]);

  let buffer = "";

  stt.stdout.on("data", async (chunk) => {
    buffer += chunk;

    let lines = buffer.split("\n");
    buffer = lines.pop(); // save incomplete line

    for (const line of lines) {
      if (!line.trim()) continue;

      try {
        const json = JSON.parse(line);

        switch (json.type) {
          case "AIA":
            console.log("[STT AIA]:", json.text);
            break;
          case "transcription":
            console.log("[STT Command]:", json.text);
            const query = [{"role": "user", "content": json.text}]
            const response = await getOllamaResponse(query);
            console.log("[AIA]: ", response);  
            break;
          case "status":
            console.log("[STT Status]:", json.text);
            break;
          default:
            console.log("[STT LOG]", json);
        }

      } catch (err) {
        console.log("[JSON PARSE ERROR]", err);
        console.log("[LINE RECEIVED]", line);
      }
    }
  });
}

// Express API
app.post("/chat", async (req, res) => {
  try{
    const query = req.body.messages;
    console.log("Query sent: ", query);
    const response = await getOllamaResponse(query);
    res.json({message: response});
  }catch (err) {
    console.error("Error contacting Ollama:", err);
    res.status(500).json({ error: "Failed to reach Ollama." });
  }
  
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`)
  startSTTService();
});