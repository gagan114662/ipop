// JavaScript Step - Pet Recommendation Engine
import motia from 'motia'

export default motia.step({
  type: 'event',
  name: 'PetRecommendationEngine',
  description: 'Generates personalized pet recommendations based on sentiment analysis',
  flows: ['basic-tutorial'],
  subscribes: ['sentiment.analyzed'],
  emits: ['recommendations.generated']
})

export const handler = async (event, { logger, emit, state }) => {
  logger.info('🟡 JavaScript Step: Generating pet recommendations')
  
  const { pet_id, pet_name, analysis } = event.data
  const sentiment = analysis.sentiment
  
  // JavaScript excels at rapid prototyping and complex data manipulation
  const recommendations = generateRecommendations(sentiment, pet_name)
  const userPreferences = await getUserPreferences(pet_id)
  const personalizedRecs = personalizeRecommendations(recommendations, userPreferences)
  
  logger.info(`📊 Generated ${personalizedRecs.length} recommendations for ${pet_name}`)
  
  // Store recommendations in shared state
  await state.set('recommendations', pet_id, {
    pet_id,
    pet_name,
    recommendations: personalizedRecs,
    sentiment_used: sentiment.label,
    generated_at: new Date().toISOString(),
    language: 'javascript'
  })
  
  // Emit for notification step
  await emit('recommendations.generated', {
    pet_id,
    pet_name,
    recommendations: personalizedRecs,
    sentiment: sentiment.label
  })
  
  return {
    recommendations_count: personalizedRecs.length,
    sentiment_processed: sentiment.label,
    personalized: true
  }
}

function generateRecommendations(sentiment, petName) {
  const baseRecommendations = {
    'POSITIVE': [
      '🎾 Interactive toys for energetic play',
      '🦴 Premium treats for good behavior',
      '🏠 Comfortable bedding for happy pets',
      '🎪 Training classes for social pets'
    ],
    'NEGATIVE': [
      '🧸 Calming toys to reduce anxiety',
      '🌿 Natural stress-relief supplements',
      '🛏️ Quiet, safe spaces for comfort',
      '👨‍⚕️ Behavioral consultation services'
    ],
    'NEUTRAL': [
      '🍽️ Balanced nutrition plans',
      '🚿 Regular grooming services',
      '🏃‍♂️ Daily exercise routines',
      '🩺 Regular health checkups'
    ]
  }
  
  return baseRecommendations[sentiment.label] || baseRecommendations['NEUTRAL']
}

async function getUserPreferences(petId) {
  // Simulate user preference retrieval
  // In production, this could query a database or external service
  return {
    budget: 'medium',
    activity_level: 'moderate',
    experience: 'beginner',
    living_situation: 'apartment'
  }
}

function personalizeRecommendations(recommendations, preferences) {
  // JavaScript's strength: flexible data transformation
  return recommendations.map((rec, index) => ({
    id: index + 1,
    recommendation: rec,
    priority: Math.random() > 0.5 ? 'high' : 'medium',
    estimated_cost: preferences.budget === 'high' ? '$50-100' : '$20-50',
    suitable_for: preferences.living_situation,
    difficulty: preferences.experience === 'beginner' ? 'easy' : 'moderate'
  }))
}