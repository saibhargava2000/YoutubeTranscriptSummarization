from flask import Flask, render_template, request, url_for
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

app = Flask(__name__)

# Load BART model and tokenizer
model_name = 'facebook/bart-large-cnn'
tokenizer = AutoTokenizer.from_pretrained(model_name)
path = r'C:\Users\Bhargava Cheppela\Documents\Youtube Transcript Summarization\model'
model = AutoModelForSeq2SeqLM.from_pretrained(path)

def get_youtube_transcript(video_url):
    try:
        video_id = video_url.split("v=")[1]
        transcripts = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join(entry['text'] for entry in transcripts)
        return transcript_text
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def summarize_text(text):
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True, padding=True)
    summary_ids = model.generate(inputs, max_length=512, min_length=50, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form['video_url']
        transcripts = get_youtube_transcript(video_url)
        if transcripts:
            summary = summarize_text(transcripts)
            return render_template('index.html', video_url=video_url, transcripts=transcripts, summary=summary)
    return render_template('index.html', video_url='', transcripts='', summary='')

if __name__ == '__main__':
    app.run(debug=True)
