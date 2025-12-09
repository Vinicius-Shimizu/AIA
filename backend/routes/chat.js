import express from "express";
import { getOllamaResponse } from "../ollama/ollamaClient.js";

const router = express.Router();

router.post("/", async (req, res) => {
  try {
    const query = req.body.messages;
    console.log("[/chat] Query sent: ", query);

    const response = await getOllamaResponse(query);

    res.json({ message: response });
  } catch (err) {
    console.error("Error contacting Ollama:", err);
    res.status(500).json({ error: "Failed to reach Ollama." });
  }
});

export default router;