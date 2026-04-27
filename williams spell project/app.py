from flask import Flask, render_template, request, jsonify
from collections import Counter
import re, os, json

app = Flask(__name__)

# -------- ADVANCED SPELL CHECK MODEL --------

def words(text):
    return re.findall(r'\w+', text.lower())

def load_dictionary():
    """Load and combine all dictionary files"""
    combined_words = Counter()
    for filename in ('words.txt', 'word.txt'):
        if os.path.exists(filename):
            with open(filename, encoding='utf-8', errors='ignore') as f:
                combined_words.update(words(f.read()))
    return combined_words

WORDS = load_dictionary()

def P(word):
    """Probability of word in dictionary"""
    N = sum(WORDS.values())
    return WORDS[word] / N if N else 0

def edits1(word):
    """Generate all edits that are one edit away from word"""
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word)+1)]
    deletes = [L + R[1:] for L, R in splits if R]
    inserts = [L + c + R for L, R in splits for c in letters]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    return set(deletes + inserts + replaces + transposes)

def edits2(word):
    """Generate all edits that are two edits away from word"""
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1))

def known(words_list):
    """Return subset of words that appear in dictionary"""
    return set(w for w in words_list if w in WORDS)

def candidates(word):
    """Generate possible spelling corrections for word"""
    return (known([word]) or
            known(edits1(word)) or
            known(edits2(word)) or
            [word])

def correct(word):
    """Most probable spelling correction for word"""
    return max(candidates(word), key=P)

def get_suggestions(word, max_suggestions=5):
    """Get multiple spelling suggestions ranked by probability"""
    candidate_words = candidates(word)
    # Sort by probability, then alphabetically for ties
    suggestions = sorted(candidate_words, key=lambda w: (-P(w), w))
    return suggestions[:max_suggestions]

def spell_check_text(text):
    """Check text and return corrections with suggestions"""
    words_in_text = re.findall(r'\w+', text)
    corrections = {}

    for word in words_in_text:
        lower_word = word.lower()
        if lower_word not in WORDS:
            suggestions = get_suggestions(lower_word)
            if suggestions:
                corrections[word] = {
                    'original': word,
                    'suggestions': suggestions,
                    'best_correction': suggestions[0]
                }

    return corrections

# -------- ROUTES --------

@app.route("/", methods=["GET", "POST"])
def index():
    corrected_text = ""
    spell_check_results = {}

    if request.method == "POST":
        text = request.form.get("text", "").strip()
        if text:
            # Get spell check results
            spell_check_results = spell_check_text(text)

            # Apply automatic corrections for corrected_text
            corrected_text = text
            for original, data in spell_check_results.items():
                # Replace with best suggestion, preserving case
                if original.isupper():
                    replacement = data['best_correction'].upper()
                elif original.istitle():
                    replacement = data['best_correction'].title()
                else:
                    replacement = data['best_correction']
                corrected_text = re.sub(r'\b' + re.escape(original) + r'\b', replacement, corrected_text)
        else:
            corrected_text = "Please enter some text to correct."

    return render_template("index.html",
                         corrected=corrected_text,
                         spell_check=json.dumps(spell_check_results))

@app.route("/api/spellcheck", methods=["POST"])
def api_spellcheck():
    """API endpoint for real-time spell checking"""
    data = request.get_json()
    text = data.get('text', '')
    results = spell_check_text(text)
    return jsonify(results)

if __name__ == "__main__":
    import webbrowser
    host = "0.0.0.0"
    port = 5000
    url = f"http://127.0.0.1:{port}"
    print(f"Starting server at {url} (host={host}, port={port})")
    # Open browser automatically
    webbrowser.open(url)
    app.run(host=host, port=port, debug=True)