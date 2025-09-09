// Cross-Language JavaScript Step
import motia from 'motia'

export default motia.step({
  type: 'event',
  name: 'CrossLanguageJavaScriptRecommender',
  description: 'Cross-language JavaScript step that receives from Python and sends to Ruby',
  flows: ['cross-language-demo'],
  subscribes: ['cross.analysis.complete'],
  emits: ['cross.recommendations.ready']
})

export const handler = async (event, { logger, emit, state }) => {
  logger.info('🟡 Cross-Language JavaScript: Processing recommendations from Python AI')
  
  const { pet_id, pet_name, analysis } = event.data
  const sentiment = analysis.sentiment
  
  // Enhanced recommendations based on Python AI analysis
  const aiEnhancedRecommendations = generateCrossLanguageRecommendations(sentiment, pet_name, analysis)
  
  logger.info(`📊 Cross-Language JS: Generated ${aiEnhancedRecommendations.length} AI-enhanced recommendations`)
  
  // Store in cross-language state namespace
  await state.set('cross-recommendations', pet_id, {
    pet_id,
    pet_name,
    recommendations: aiEnhancedRecommendations,
    source_analysis: analysis,
    processing_language: 'javascript',
    cross_language_flow: true,
    generated_at: new Date().toISOString()
  })
  
  // Emit to trigger Ruby email step
  await emit('cross.recommendations.ready', {
    pet_id,
    pet_name,
    recommendations: aiEnhancedRecommendations,
    sentiment: sentiment.label,
    ai_confidence: sentiment.confidence,
    source: 'cross-language-javascript',
    next_step: 'ruby-email'
  })
  
  return {
    status: 'cross_language_recommendations_complete',
    recommendations_count: aiEnhancedRecommendations.length,
    sentiment_used: sentiment.label,
    next_language: 'ruby'
  }
}

function generateCrossLanguageRecommendations(sentiment, petName, aiAnalysis) {
  const baseRecs = {
    'POSITIVE': [
      '🎾 AI-recommended interactive toys for happy pets',
      '🌟 Premium treats based on sentiment analysis',
      '🏆 Advanced training programs for positive pets',
      '🎪 Social activities for confident animals'
    ],
    'NEUTRAL': [
      '🎯 Balanced activity recommendations',
      '📚 Educational toys for curious pets', 
      '🛡️ Comfort items for neutral temperament',
      '⚖️ Well-rounded care packages'
    ],
    'NEGATIVE': [
      '🧸 Calming toys for anxious pets',
      '🌿 Stress-relief natural supplements',
      '🛏️ Safe space comfort items',
      '👨‍⚕️ Behavioral support services'
    ]
  }
  
  const recs = baseRecs[sentiment.label] || baseRecs['NEUTRAL']
  
  return recs.map((rec, index) => ({
    id: index + 1,
    recommendation: rec,
    priority: sentiment.score > 0.7 ? 'high' : 'medium',
    ai_confidence: sentiment.confidence,
    cross_language_enhanced: true,
    estimated_cost: '$30-75',
    processing_chain: 'Python AI → JavaScript Engine'
  }))
}