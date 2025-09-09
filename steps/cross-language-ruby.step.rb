# Cross-Language Ruby Step
require 'motia'
require 'json'
require 'time'

Motia.step(
  type: 'event',
  name: 'CrossLanguageRubyNotifier',
  description: 'Cross-language Ruby step that receives from JavaScript and completes the workflow',
  flows: ['cross-language-demo'],
  subscribes: ['cross.recommendations.ready'],
  emits: ['cross.workflow.complete']
) do |event, context|
  
  logger = context[:logger]
  emit = context[:emit]
  
  logger.info '💎 Cross-Language Ruby: Crafting final notifications from JS recommendations'
  
  pet_name = event.data['pet_name']
  recommendations = event.data['recommendations']
  sentiment = event.data['sentiment']
  ai_confidence = event.data['ai_confidence']
  
  # Ruby's elegant string processing for cross-language email
  cross_language_email = craft_cross_language_email(pet_name, recommendations, sentiment, ai_confidence)
  
  # Simulate advanced email delivery with Ruby gems
  email_result = send_cross_language_email(
    to: 'cross-language-demo@example.com',
    subject: "🌍 Multi-Language AI Analysis Complete for #{pet_name}",
    content: cross_language_email
  )
  
  logger.info "📧 Cross-Language Ruby: Workflow complete for #{pet_name}"
  
  # Final emit to complete the cross-language chain
  emit.call('cross.workflow.complete', {
    pet_name: pet_name,
    processing_chain: 'TypeScript API → Python AI → JavaScript Engine → Ruby Email',
    workflow_completed_at: Time.now.iso8601,
    recommendations_sent: recommendations.length,
    final_sentiment: sentiment,
    ai_confidence: ai_confidence,
    languages_used: ['typescript', 'python', 'javascript', 'ruby']
  })
  
  {
    status: 'cross_language_workflow_complete',
    pet_name: pet_name,
    languages_processed: 4,
    final_processor: 'ruby'
  }
end

def craft_cross_language_email(pet_name, recommendations, sentiment, ai_confidence)
  confidence_emoji = ai_confidence > 0.8 ? '🎯' : '📊'
  
  template = <<~EMAIL
    🌍 Multi-Language AI Analysis Complete! #{confidence_emoji}
    
    Dear Pet Parent,
    
    Our advanced multi-language AI system has completed a comprehensive analysis of #{pet_name}!
    
    🔄 Processing Chain:
    1. 🟦 TypeScript API - Initial request handling
    2. 🐍 Python AI - Advanced sentiment analysis (#{(ai_confidence * 100).round}% confidence)  
    3. 🟡 JavaScript - Personalized recommendation engine
    4. 💎 Ruby - Beautiful notification crafting
    
    📊 AI Analysis Results:
    • Sentiment: #{sentiment} 
    • Confidence: #{(ai_confidence * 100).round}%
    • Processing Languages: 4 different languages working together!
    
    🎯 Cross-Language Enhanced Recommendations:
    #{format_cross_language_recommendations(recommendations)}
    
    ✨ This demonstrates Motia's powerful multi-language capabilities - each step 
    was processed in the language best suited for the task!
    
    🚀 Powered by Motia's Polyglot Architecture
    
    ---
    Generated: #{Time.now.strftime('%B %d, %Y at %I:%M %p')}
    Languages: TypeScript + Python + JavaScript + Ruby
  EMAIL
  
  template
end

def format_cross_language_recommendations(recommendations)
  recommendations.map.with_index(1) do |rec, index|
    "   #{index}. #{rec['recommendation']} (#{rec['priority']} priority, AI confidence: #{(rec['ai_confidence'] * 100).round}%)"
  end.join("\n")
end

def send_cross_language_email(to:, subject:, content:)
  {
    message_id: "cross-lang-#{Time.now.to_i}-#{rand(1000)}",
    status: 'delivered',
    sent_at: Time.now.iso8601,
    to: to,
    subject: subject,
    languages_used: 4,
    provider: 'motia-cross-language-service'
  }
end