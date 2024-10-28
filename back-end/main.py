from flask import Flask, request, jsonify
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.search.documents import SearchClient
from flask_cors import CORS 
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env
app = Flask(__name__)
CORS(app)
load_dotenv()


# Azure API credentials (ensure to secure this in your environment variables or secrets)
API_KEY = os.getenv('API_KEY')
ENDPOINT = os.getenv('ENDPOINT')

INDEX_NAME =os.getenv('INDEX_NAME')
AI_SEARCH_ENDPOINT=os.getenv('AI_SEARCH_ENDPOINT')
AI_SEARCH_KEY=os.getenv('AI_SEARCH_KEY')

TEXT_ANALYTICS_ENDPOINT = os.getenv('TEXT_ANALYTICS_ENDPOINT')
TEXT_ANALYTICS_KEY = os.getenv('TEXT_ANALYTICS_KEY')

# Initialize Azure clients
text_analytics_client = TextAnalyticsClient(endpoint=TEXT_ANALYTICS_ENDPOINT, credential=AzureKeyCredential(TEXT_ANALYTICS_KEY))
search_client = SearchClient(endpoint=AI_SEARCH_ENDPOINT, index_name=INDEX_NAME, credential=AzureKeyCredential(AI_SEARCH_KEY))
openai_client = AzureOpenAI(api_key=API_KEY, api_version="2024-08-01-preview", azure_endpoint=ENDPOINT)

# Function to analyze user sentiment
def get_sentiment(query_text):
    docs = [query_text]
    result = text_analytics_client.analyze_sentiment(docs, show_opinion_mining=True)
    sentiment_result = [doc for doc in result if not doc.is_error]
    
    if not sentiment_result:
        return "neutral", "neutral and informative"

    sentiment = sentiment_result[0].sentiment
    if sentiment == "negative":
        tone = "empathetic and supportive"
    elif sentiment == "positive":
        tone = "encouraging and positive"
    else:
        tone = "neutral and informative"

    return sentiment, tone

# Function to perform Azure Search
def get_search_results(query_text):
    search_results = search_client.search(
        search_text=query_text,
        top=5  # Number of documents to retrieve
    )
    # Extract top 5 results as a list of texts
    return [result['content'] for result in search_results]

# Function to generate a response using Azure OpenAI
def generate_response(query_text, search_results, sentiment, tone):
    messages = [
        {
            "role": "system",
            "content": "Anda adalah asisten AI yang membantu orang menemukan informasi tentang layanan MariBelajar. Berikan sentiment yang sesuai terlebih dahulu seperti sambutan atau respon terhadap sentiment dulu, setelah itu baru jawab pertanyaan berdasarkan informasi yang tersedia.Selalu mulai dengan kata : Anda sepertinya sedang...... isis titik titik dengan suasana dan sentiment pengguna"
        },
        {
            "role": "user",
            "content": f"User Input: {query_text}. FAQ Information: {search_results}. User Sentiment: {sentiment}. Create a response using the FAQ information with a {tone} tone."
        }
    ]

    response = openai_client.chat.completions.create(
        model="gpt-35-turbo",
        messages=messages,
        temperature=0.7,
        top_p=0.95,
        max_tokens=800,
        stream=False,
        frequency_penalty=0,
        presence_penalty=0
    )

    content = response.choices[0].message.content

    return content

# Flask API route
@app.route('/get_rag_chain', methods=['POST'])
def get_rag_chain():
    try:
        # Get query text from request body
        data = request.get_json()
        query_text = data['query']

        # Analyze sentiment
        sentiment, tone = get_sentiment(query_text)

        # Perform Azure search
        search_results = get_search_results(query_text)

        # Generate response
        response_text = generate_response(query_text, search_results, sentiment, tone)

        # Return response with sentiment and tone
        return jsonify({
            "response": response_text,
            "sentiment": sentiment,
            "tone": tone
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
