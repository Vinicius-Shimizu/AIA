// server.js
const express = require("express");
const cors = require("cors");
const multer = require("multer");
const { exec } = require("child_process");

const app = express();
app.use(express.json());
app.use(cors());


const upload = multer({ dest: "uploads/" });

app.post("/transcribe", upload.single("audio"), (req, res) => {
  const filePath = req.file.path;
  console.log("Route found!")
  console.log(req)
  exec(`python3 whisper_test.py whisper_test.m4a`, (error, stdout, stderr) => {
    if (error || stderr) return res.status(500).send(stderr || error.message);
    res.json({ text: stdout });
  });
});




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

const PORT = 3000;
app.listen(PORT, () => console.log(`✅ Backend running on http://localhost:${PORT}`));
