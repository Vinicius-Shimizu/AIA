import express from "express";
import { processAIAQuery } from "../core/processAIAQuery.js";
import { getHistory, addToHistory } from "../core/historyManager.js";

const router = express.Router();

router.post("/", async (req, res) => {
  try {
    const query = req.body.messages[0];
    console.log("[/chat] Query sent: ", query);

    addToHistory(query.role, query.content);
    const current_history = getHistory();
    console.log(current_history);
    const { response, followup } = await processAIAQuery(current_history);
    
    if (followup) {
      console.log("[AIA Response]:", followup);
      res.json({ message: followup });
      
      addToHistory("assistant", followup);
    }
    else res.json({ message: response });
  } catch (err) {
    console.error("Error contacting Ollama:", err);
    res.status(500).json({ error: "Failed to reach Ollama." });
  }
});

export default router;