// Integration reference: blueprint:javascript_openai
// the newest OpenAI model is "gpt-5" which was released August 7, 2025. do not change this unless explicitly requested by the user
import OpenAI from "openai";

const OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1";
const OLLAMA_BASE_URL = "http://192.168.2.67:11434/v1";

const envKey =
  process.env.OPENAI_API_KEY ||
  process.env.OPENROUTER_API_KEY ||
  process.env.openrouter_api_key ||
  "ollama"; // Dummy key for Ollama (required but not used)

const usingOllama = process.env.USE_OLLAMA === "true";
const usingOpenRouter =
  !usingOllama &&
  !process.env.OPENAI_API_KEY &&
  (process.env.OPENROUTER_API_KEY || process.env.openrouter_api_key);

export const openai = new OpenAI({
  apiKey: envKey,
  ...(usingOllama
    ? {
        baseURL: OLLAMA_BASE_URL,
      }
    : usingOpenRouter
    ? {
        baseURL: OPENROUTER_BASE_URL,
        defaultHeaders: {
          "HTTP-Referer":
            process.env.OPENROUTER_SITE || "https://motiacreative-development.local",
          "X-Title": process.env.OPENROUTER_APP_NAME || "Motia Creative Development",
        },
      }
    : {}),
});

export const RESEARCH_MODEL = usingOllama ? "llama3.3:latest" : "gpt-5";
