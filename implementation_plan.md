# Advanced Features Implementation Plan

This plan details the implementation of all the suggested advanced features: AI Comment Auto-Replies, Custom Prompting, Shorts Ideas generation, WhatsApp Notifications, and Weekly Performance Reports.

## User Review Required

> [!WARNING]
> **WhatsApp Notifications:** To send WhatsApp messages without setting up a complex Meta Business account, the easiest and free method is using the **CallMeBot API**. You will need to get an API key from them by simply sending a WhatsApp message to their bot.
> 
> **Comment Auto-Replies:** Replying to comments via the YouTube API requires an additional OAuth scope (`https://www.googleapis.com/auth/youtube.force-ssl` is what you currently have, which actually already covers comments! So no token refresh is needed).

## Open Questions

1. **WhatsApp API**: Are you okay with using the free [CallMeBot API](https://www.callmebot.com/) for WhatsApp notifications? It only requires you to send a message from your phone to get an API key.
2. **Auto-Reply Rules**: Should the bot reply to *every* new top-level comment on the optimized videos, or only the very first one? Also, is there a specific persona you want the bot to have when replying (e.g., helpful, funny, professional)?
3. **Weekly Report Day**: What day of the week and time do you want the weekly performance report to run? (e.g., Sundays at 9:00 AM).

## Proposed Changes

### 1. Generate Shorts Ideas
#### [MODIFY] [`ai_generator.py`](file:///c:/Users/BSNL/OneDrive/Documents/Templates/Description%20Bot/ai_generator.py)
- Update the prompt to ask the AI for 3 YouTube Shorts ideas based on the video content.
- Update the expected JSON schema to return a list of `shorts_ideas`.

### 2. Custom Prompting via Description Tags
#### [MODIFY] [`ai_generator.py`](file:///c:/Users/BSNL/OneDrive/Documents/Templates/Description%20Bot/ai_generator.py)
- Use regular expressions to extract special directives from your raw video description (e.g., `[Tone: Funny]`, `[Focus: Beginners]`) and dynamically inject them into the Gemini prompt.

### 3. WhatsApp Notifications
#### [MODIFY] [`.env`](file:///c:/Users/BSNL/OneDrive/Documents/Templates/Description%20Bot/.env) & `upload_secrets.py`
- Add `WHATSAPP_PHONE_NUMBER` and `WHATSAPP_API_KEY`.
#### [NEW] `whatsapp_notifier.py`
- Create a script that uses the `requests` library to send messages to the CallMeBot API.
#### [MODIFY] [`main.py`](file:///c:/Users/BSNL/OneDrive/Documents/Templates/Description%20Bot/main.py)
- Call the WhatsApp notifier (alongside the email notifier) when a video is processed. The message will include the title and the newly generated Shorts ideas.

### 4. AI Auto-Reply to Comments
#### [MODIFY] [`youtube_client.py`](file:///c:/Users/BSNL/OneDrive/Documents/Templates/Description%20Bot/youtube_client.py)
- Add functions to `get_unreplied_comments(video_id)` and `reply_to_comment(comment_id, reply_text)`.
#### [NEW] `comment_manager.py`
- A script to fetch comments, ask Gemini for a contextual reply, and post it.

### 5. Weekly Performance Reports
#### [NEW] `weekly_report.py`
- A script that fetches all videos from the last 7 days, gets their view/like/comment counts using the YouTube API, formats it into a summary, and sends it via Email and WhatsApp.
#### [NEW] `.github/workflows/weekly_report.yml`
- A new GitHub Actions workflow scheduled to run once a week.

## Verification Plan

- We will modify `upload_secrets.py` to securely push your new WhatsApp keys to GitHub.
- We will perform a manual test run of the comment replier.
- We will push the updated workflows and verify the GitHub Actions pass.
