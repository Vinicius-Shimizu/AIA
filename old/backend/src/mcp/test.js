// import fs from "fs";
// import path from "path";
import { fileURLToPath } from "url";
// import { exec } from "child_process";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
// const whitelistPath = path.join(__dirname, "apps_whitelist.json");

// async function searchApp( app_name ) {
//     console.log(`Searching for ${app_name}...`);
    
//     // Command to search Program Files directories using PowerShell
//     // We filter for .exe files and stop after the first match to save time.
//     const command = `powershell -command "Get-ChildItem -Path 'C:\\Program Files', 'C:\\Program Files (x86)' -Filter '${app_name}*.exe' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName"`;

//     return new Promise((resolve) => {
//       exec(command, (error, stdout, stderr) => {
//         if (error || !stdout.trim()) {
//           resolve({
//             content: [{ type: "text", text: `Could not find executable for '${app_name}'.` }],
//             isError: true,
//           });
//           return;
//         }

//         const path = stdout.trim();
//         resolve({
//           content: [{ type: "text", text: path }], // Returns the full path (e.g., C:\Program Files\...\app.exe)
//           result: path
//         });
//       });
//     });
// }

// const app = await searchApp("discord");
// console.log(app);

import fs from 'fs';
import path from 'path';
import os from 'os';

// 1. Define where Windows keeps shortcuts
const commonStartMenu = path.join(process.env.ProgramData, 'Microsoft', 'Windows', 'Menu Iniciar', 'Programas');
const userStartMenu = path.join(process.env.APPDATA, 'Microsoft', 'Windows', 'Menu Iniciar', 'Programas');
const whitelistPath = path.join(__dirname, "test_apps_whitelist.json");
// 2. Helper function to scan folders recursively
function getAppsFromDir(dir, fileList = []) {
  if (!fs.existsSync(dir)) return fileList;
  
  const files = fs.readdirSync(dir);

  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      // Go deeper into subfolders (like "Accessories" or "Steam")
      getAppsFromDir(filePath, fileList);
    } else if (file.toLowerCase().endsWith('.lnk')) {
      // 3. We found a shortcut! 
      // The "name" is the filename without extension (e.g., "Calculadora.lnk" -> "Calculadora")
      fileList.push({
        name: path.parse(file).name, // This automatically gets the localized name
        path: filePath // Windows can execute .lnk files directly
      });
    }
  });

  return fileList;
}

// 4. Build the whitelist once on startup
const dynamicWhitelist = [
  ...getAppsFromDir(commonStartMenu),
  ...getAppsFromDir(userStartMenu)
];

console.log(`Loaded ${dynamicWhitelist.length} apps automatically.`);

fs.writeFileSync(whitelistPath, JSON.stringify(dynamicWhitelist));