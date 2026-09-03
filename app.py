import os
import re
from datetime import date, timedelta
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL = 'gemini-3.5-flash'

CHAT_SYSTEM_PROMPT = """
You are a helpful AI assistant integrated into the portfolio website of Christian Renz Ledesma, a BS Information Technology student at NEUST Papaya Off-Campus.

Answer questions about his background, skills, projects, coursework, and experience. Keep responses concise, accurate, and professional.

FORMATTING RULES (strict):
- Use Markdown formatting in all responses.
- Use **bold** for key names, technologies, and important terms.
- Use bullet lists (- item) for enumerations, skills, or grouped items.
- Use numbered lists (1. item) for step-by-step instructions.
- Use headings (## or ###) sparingly, only when needed to organize longer answers.
- Wrap code samples in triple backticks with the language name.
- Wrap inline code in single backticks.
- Use [link text](url) for any URLs.
- Keep paragraphs short (1-3 sentences each).
- Do NOT use emojis.
- Never fabricate information. If unsure, say so honestly.
"""


@app.route('/')
def home():
    return render_template('index.html', name='Christian Renz Ledesma')


@app.route('/termsofuse')
def show_terms():
    return render_template('termsofuse.html')


@app.route('/sitemap')
def sitemap():
    return render_template('sitemap.html')


GITHUB_USERNAME = 'ChristianRenzLedesma'


@app.route('/contributions')
def contributions():
    data = []
    total = 0
    error = None

    try:
        resp = requests.get(
            f'https://github.com/users/{GITHUB_USERNAME}/contributions',
            timeout=20,
            headers={'User-Agent': 'Mozilla/5.0 (portfolio)'}
        )
        resp.raise_for_status()
        html = resp.text

        pattern = re.compile(
            r'<td[^>]*data-date="([^"]+)"[^>]*id="([^"]+)"[^>]*data-level="(\d)"[^>]*></td>\s*'
            r'<tool-tip[^>]*for="\2"[^>]*>([^<]*)<'
        )
        for match in pattern.finditer(html):
            day, _, level, tooltip = match.groups()
            count = 0
            m = re.search(r'(\d+)\s+contribution', tooltip or '')
            if m:
                count = int(m.group(1))
            total += count
            d = date.fromisoformat(day)
            data.append({
                'date': day,
                'level': int(level),
                'count': count,
                'month': d.strftime('%b'),
                'index': len(data),
            })
    except Exception as e:
        error = str(e)

    return render_template('contributions.html', data=data, total=total, error=error)


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = (data or {}).get('message', '').strip()
    history = (data or {}).get('history', [])

    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    if not GEMINI_API_KEY:
        return jsonify({'error': 'Gemini API key not configured. Set GEMINI_API_KEY environment variable.'}), 500

    url = f'https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent'

    contents = [{'role': 'user', 'parts': [{'text': CHAT_SYSTEM_PROMPT}]}]
    for msg in history:
        role = 'model' if msg.get('role') == 'assistant' else 'user'
        contents.append({'role': role, 'parts': [{'text': msg.get('content', '')}]})
    contents.append({'role': 'user', 'parts': [{'text': user_message}]})

    payload = {'contents': contents}

    try:
        response = requests.post(
            url,
            params={'key': GEMINI_API_KEY},
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        reply = data['candidates'][0]['content']['parts'][0]['text']
        return jsonify({'reply': reply})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to reach Gemini API: {str(e)}'}), 502
    except (KeyError, IndexError) as e:
        return jsonify({'error': f'Unexpected API response: {str(e)}'}), 502


if __name__ == '__main__':
    app.run(debug=True)
