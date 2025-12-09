import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const whitelistPath = path.join(__dirname, "apps_whitelist.json");

async function allow_app(app_name) {
    const lower = app_name.toLowerCase();
    const whitelist = JSON.parse(fs.readFileSync(whitelistPath, "utf-8"));
    whitelist.apps.push(lower);
    console.log(whitelist);
    fs.writeFileSync(whitelistPath, JSON.stringify(whitelist), function(err) {
        if(err){
            retu
        }
    })
    
}

allow_app("test");