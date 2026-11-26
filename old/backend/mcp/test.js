import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const whitelistPath = path.join(__dirname, "apps_whitelist.json");

async function allow_app(app_name) {
    const lower = app_name.toLowerCase();
    const whitelist = JSON.parse(fs.readFileSync(whitelistPath, "utf-8"));

    console.log(lower);
    console.log(whitelist);
    const allowed = whitelist.apps.some(app =>
        lower.includes(app.toLowerCase()) ||
        app.toLowerCase().includes(lower)
    );

    const findApp = function(){
        for (let app in whitelist.apps){
            if(lower.includes(app.toLowerCase()) || app.toLowerCase().includes(lower)){
                console.log("Found")
                return app;
            }
        }
    }
    console.log(findApp());
}

allow_app("calculadora");