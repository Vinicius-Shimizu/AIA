import express from "express";
import cors from "cors";
import {spawn} from "child_process";

const app = express();
app.use(express.json());
app.use(cors());

const PORT = 3000;

function startSTTService() {
  const stt = spawn("python", ["-u", "stt_engine.py"]);

  let buffer = "";

  stt.stdout.on("data", (chunk) => {
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

  const { messages } = req.body;
  console.log(messages)
  try {
    const response = await fetch("http://127.0.0.1:11434/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "gemma3",
        messages,
        stream: false,
      }),
    });

    const data = await response.json();
    const assistantContent = data.message.content;
    res.json({ message: assistantContent });
  } catch (err) {
    console.error("Error contacting Ollama:", err);
    res.status(500).json({ error: "Failed to reach Ollama." });
  }
});

startSTTService();
app.listen(PORT, () => console.log(`Backend running on http://localhost:${PORT}`));