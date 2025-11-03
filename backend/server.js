// server.js
const express = require("express");
const cors = require("cors");

const app = express();
app.use(express.json());
app.use(cors());

// Handle chat requests
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
      }),
    });

    const text = await response.text();

    const lines = text.split("\n").filter((line) => line.trim() !== "");
    const parsedObjects = lines.map((line) => {
        try{ return JSON.parse(line) }
        catch {return null }
    }).filter(Boolean)

    const assitantContent = parsedObjects
        .filter(obj => obj.message && obj.message.role === "assistant" && obj.message.content)
        .map(obj => obj.message.content)
        .join("");
     
    res.json({ message: assitantContent });
  } catch (err) {
    console.error("Error contacting Ollama:", err);
    res.status(500).json({ error: "Failed to reach Ollama." });
  }
});

const PORT = 3000;
app.listen(PORT, () => console.log(`✅ Backend running on http://localhost:${PORT}`));
