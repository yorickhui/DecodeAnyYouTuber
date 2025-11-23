# DecodeAnyYouTuber

A powerful tool to analyze YouTube channels using AI. It extracts insights on content strategy, script structure, visual style, and audience feedback to help creators learn and improve.

## Features
- **Channel-Level Analysis**: Analyzes the most recent videos to find patterns.
- **No API Key Required**: Uses `yt-dlp` for data extraction (no YouTube Data API quota limits).
- **Multimodal AI**: Uses Gemini (or GPT-4o) to analyze text (transcripts, comments) and visuals (thumbnails).
- **Premium UI**: Modern, dark-themed interface built with Next.js and Tailwind CSS.

## Prerequisites
- Python 3.8+
- Node.js 18+
- **API Keys**: You need a Google Gemini API Key (`GEMINI_API_KEY`) or OpenAI API Key (`OPENAI_API_KEY`).

## Setup

1. **Configure Environment Variables**:
   Create a `.env` file in `backend/` (copy from `.env.example`):
   ```bash
   cp backend/.env.example backend/.env
   ```
   Edit `backend/.env` and add your API keys.

2. **Run the Application**:
   ```bash
   ./run.sh
   ```

3. **Access**:
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000/docs](http://localhost:8000/docs)

## Tech Stack
- **Frontend**: Next.js 15, Tailwind CSS, Lucide React
- **Backend**: FastAPI, yt-dlp, Google Gemini / OpenAI SDK
