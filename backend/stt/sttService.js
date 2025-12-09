import { spawn } from "child_process";
import { processAIAQuery } from "../core/processAIAQuery.js";

export async function runSTTService() {
  const stt = spawn("python", ["-u", "./stt/stt_engine.py"]);

  let buffer = "";

  await new Promise((resolve) => {
    stt.stdout.on("data", async (chunk) => {
      buffer += chunk;

      const lines = buffer.split("\n");
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.trim()) continue;

        let json;
        try {
          json = JSON.parse(line);
        } catch {
          continue;
        }

        if (json.type === "ready") {
          console.log(json.text);
          resolve();
        }

        else if (json.type === "AIA") {
          console.log("[AIA Response]:", json.text);
        }

        else if (json.type === "transcription") {
          console.log("[Command]:", json.text);

          const { response, followup } = await processAIAQuery([
            { role: "user", content: json.text }
          ]);

          console.log("[AIA Response]:", response);
          if (followup) console.log("[Tool Followup]:", followup);
        }
      }
    });
  });
}
