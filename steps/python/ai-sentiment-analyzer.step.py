# Python Step - AI Sentiment Analysis
import motia
from datetime import datetime

@motia.step(
    type='event',
    name='AISentimentAnalyzer',
    description='Analyzes pet descriptions using AI to determine sentiment and generate insights',
    flows=['basic-tutorial'],
    subscribes=['py.pet.analyze'],
    emits=['py.sentiment.analyzed']
)
async def analyze_pet_sentiment(event, context):
    """
    Demonstrates Python's strength in AI/ML processing within Motia workflows.
    In a real implementation, you could use libraries like:
    - transformers (Hugging Face)
    - openai
    - langchain
    - tensorflow/pytorch
    """
    logger = context['logger']
    emit = context['emit']
    
    pet_data = event.data
    pet_name = pet_data.get('name', 'Unknown Pet')
    
    logger.info(f'🐍 Python AI Step: Analyzing sentiment for pet: {pet_name}')
    
    # Simulated AI sentiment analysis
    # In production, replace with actual AI models:
    # from transformers import pipeline
    # classifier = pipeline("sentiment-analysis")
    # result = classifier(pet_name)
    
    # Mock sentiment analysis based on pet name
    positive_words = ['buddy', 'angel', 'sweet', 'happy', 'joy', 'love', 'precious']
    negative_words = ['grumpy', 'cranky', 'mean', 'sad', 'angry']
    
    sentiment_score = 0.7  # Default neutral-positive
    if any(word in pet_name.lower() for word in positive_words):
        sentiment_score = 0.9
        sentiment_label = 'POSITIVE'
    elif any(word in pet_name.lower() for word in negative_words):
        sentiment_score = 0.2
        sentiment_label = 'NEGATIVE'
    else:
        sentiment_label = 'NEUTRAL'
    
    # AI-generated insights
    insights = {
        'sentiment': {
            'label': sentiment_label,
            'score': sentiment_score,
            'confidence': 0.85
        },
        'ai_insights': [
            f'Pet name "{pet_name}" suggests {sentiment_label.lower()} characteristics',
            'Recommended for family-friendly environments' if sentiment_score > 0.6 else 'May require special care',
            f'AI confidence: {int(sentiment_score * 100)}%'
        ],
        'processing_timestamp': datetime.now().isoformat(),
        'model_version': 'motia-sentiment-v1.0',
        'language': 'python'
    }
    
    logger.info(f'🤖 AI Analysis Complete: {sentiment_label} ({sentiment_score:.2f})')
    
    # Emit results for other steps to consume
    await emit('py.sentiment.analyzed', {
        'pet_id': pet_data.get('id'),
        'pet_name': pet_name,
        'analysis': insights,
        'processed_by': 'python-ai-step'
    })
    
    return {
        'status': 'analyzed',
        'sentiment': sentiment_label,
        'confidence': sentiment_score,
        'insights_generated': len(insights['ai_insights'])
    }