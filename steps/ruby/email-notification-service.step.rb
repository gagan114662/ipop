# Ruby Step - Email Notification Service
require 'motia'
require 'json'
require 'time'

Motia.step(
  type: 'event',
  name: 'EmailNotificationService',
  description: 'Sends beautifully formatted email notifications using Ruby',
  flows: ['basic-tutorial'],
  subscribes: ['rb.send.email'],
  emits: ['rb.email.sent']
) do |event, context|
  
  logger = context[:logger]
  emit = context[:emit]
  
  logger.info '💎 Ruby Step: Crafting beautiful email notifications'
  
  pet_name = event.data['pet_name']
  recommendations = event.data['recommendations']
  sentiment = event.data['sentiment']
  
  # Ruby excels at string manipulation and templating
  email_content = craft_email_template(pet_name, recommendations, sentiment)
  
  # Simulate email sending
  # In production, use gems like:
  # - mail
  # - sendgrid-ruby  
  # - mailgun-ruby
  # - aws-ses
  
  email_result = send_email(
    to: 'pet-owner@example.com',
    subject: "🐾 Personalized Recommendations for #{pet_name}",
    content: email_content
  )
  
  logger.info "📧 Email sent successfully for #{pet_name}"
  
  # Emit confirmation
  emit.call('rb.email.sent', {
    pet_name: pet_name,
    email_sent_at: Time.now.iso8601,
    recommendation_count: recommendations.length,
    sentiment_context: sentiment,
    language: 'ruby'
  })
  
  {
    status: 'sent',
    pet_name: pet_name,
    recommendations_included: recommendations.length,
    email_type: 'personalized_recommendations'
  }
end

def craft_email_template(pet_name, recommendations, sentiment)
  # Ruby's elegant string interpolation and formatting
  sentiment_emoji = case sentiment
                   when 'POSITIVE' then '😊'
                   when 'NEGATIVE' then '😔'
                   else '😐'
                   end
  
  template = <<~EMAIL
    🐾 Hello Pet Parent!
    
    We've analyzed #{pet_name} and discovered some exciting insights! #{sentiment_emoji}
    
    Based on our AI analysis, #{pet_name} shows #{sentiment.downcase} characteristics.
    Here are our personalized recommendations:
    
    #{format_recommendations(recommendations)}
    
    💝 These recommendations are tailored specifically for #{pet_name}'s personality!
    
    Happy Pet Parenting! 🏠
    
    ---
    Crafted with ❤️ using Ruby in Motia
    Generated: #{Time.now.strftime('%B %d, %Y at %I:%M %p')}
  EMAIL
  
  template
end

def format_recommendations(recommendations)
  recommendations.map.with_index(1) do |rec, index|
    "#{index}. #{rec['recommendation']} (#{rec['priority']} priority, #{rec['estimated_cost']})"
  end.join("\n    ")
end

def send_email(to:, subject:, content:)
  # Simulate email sending with Ruby elegance
  {
    message_id: "ruby-#{Time.now.to_i}-#{rand(1000)}",
    status: 'delivered',
    sent_at: Time.now.iso8601,
    to: to,
    subject: subject,
    provider: 'motia-mail-service'
  }
end