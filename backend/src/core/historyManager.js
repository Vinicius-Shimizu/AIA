let conversationHistory = [];
const MAX_HISTORY = 20;

export function getHistory() {
  return [...conversationHistory];
}

export function addToHistory(role, content) {
  conversationHistory.push({ role, content });
  
  if (conversationHistory.length > MAX_HISTORY) {
    conversationHistory = conversationHistory.slice(conversationHistory.length - MAX_HISTORY);
  }
}

export function clearHistory() {
  conversationHistory = [];
}