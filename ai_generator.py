import os
import json
# pyrefly: ignore [missing-import]
import google.generativeai as genai
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use the latest Gemini 2.5 Flash model for best text generation
model = genai.GenerativeModel('gemini-2.5-flash')

import re

def generate_metadata(raw_title, raw_description):
    """
    Calls the Gemini API to generate an SEO-optimized title, description, and tags
    based on the initial raw metadata.
    """
    tone_match = re.search(r'\[Tone:\s*(.*?)\]', raw_description, re.IGNORECASE)
    focus_match = re.search(r'\[Focus:\s*(.*?)\]', raw_description, re.IGNORECASE)
    
    tone_instruction = f"Use a {tone_match.group(1)} tone." if tone_match else ""
    focus_instruction = f"Focus the content specifically on: {focus_match.group(1)}." if focus_match else ""

    prompt = f"""
    You are an expert YouTube SEO specialist. I am providing you with the raw title and 
    raw description of a newly uploaded YouTube video. 
    
    {tone_instruction}
    {focus_instruction}
    
    Your task is to generate:
    1. A highly engaging, click-worthy title (under 100 characters).
    2. A comprehensive, SEO-optimized description that will maximize reach. Include a brief summary, 
       key points, and any relevant hashtags at the bottom.
    3. A list of 15-20 highly relevant "reachability" tags that people might search for to find this video. 
       IMPORTANT: Always include the exact tag "#OptimisedbyBOSS" in the list of tags.
    4. Generate 3 unique and engaging ideas for YouTube Shorts based on the video content.
    
    Raw Title: {raw_title}
    Raw Description: {raw_description}
    
    Return the response strictly in the following JSON format without any markdown blocks or extra text:
    {{
        "title": "Your Generated Title Here",
        "description": "Your Generated Description Here",
        "tags": ["tag1", "tag2", "tag3"],
        "shorts_ideas": ["Idea 1", "Idea 2", "Idea 3"]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean up the response in case it contains markdown formatting like ```json
        text_response = response.text.strip()
        if text_response.startswith('```json'):
            text_response = text_response[7:]
        if text_response.endswith('```'):
            text_response = text_response[:-3]
            
        data = json.loads(text_response.strip())
        return data
    except Exception as e:
        print(f"Error generating metadata with AI: {e}")
        return None
