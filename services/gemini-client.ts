// Integration reference: blueprint:javascript_gemini
// Note that the newest Gemini model series is "gemini-2.5-flash" or gemini-2.5-pro"
// For image generation, use gemini-2.5-flash-image-preview (Nano Banana)
import { GoogleGenAI } from "@google/genai";

export const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || "" });

export const FLASH_MODEL = "gemini-2.5-flash";
export const PRO_MODEL = "gemini-2.5-pro";
export const IMAGE_GEN_MODEL = "gemini-2.5-flash-image-preview";
