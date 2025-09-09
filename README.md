# 🔥 Motia Framework Template

A complete Replit template for the **Motia Backend Framework** - the unified runtime that eliminates backend fragmentation by bringing APIs, background jobs, workflows, and AI agents into one system.

## 🌍 **Polyglot Workflow Showcase**

This template demonstrates Motia's **multi-language capabilities** - write each step in the language that best fits the task:
- **🟦 TypeScript** - APIs and business logic
- **🐍 Python** - AI/ML processing and data analysis  
- **🟡 JavaScript** - Rapid prototyping and data manipulation
- **💎 Ruby** - Background processing and notifications

## 🚀 Quick Start

This template comes pre-configured with everything you need to start building with Motia. Just click **Run** and start coding!

### What's Included

- ✅ **Multi-language workflow** with TypeScript, Python, JavaScript & Ruby examples
- ✅ **Complete Motia framework setup** with polyglot support
- ✅ **AI/ML capabilities** showcased through Python steps
- ✅ **Event-driven architecture** connecting steps across languages
- ✅ **Visual workbench** for debugging and monitoring workflows

## 🎯 Project Structure

```
motia-template/
├── steps/                           # Motia step definitions
│   ├── api.step.ts                 # 🟦 TypeScript API endpoint
│   ├── notification.step.ts        # 🟦 TypeScript notifications  
│   ├── process-food-order.step.ts  # 🟦 TypeScript event processing
│   ├── state-audit-cron.step.ts    # 🟦 TypeScript scheduled jobs
│   ├── python/
│   │   └── ai-sentiment-analyzer.step.py    # 🐍 Python AI/ML processing
│   ├── javascript/
│   │   └── pet-recommendation-engine.step.js # 🟡 JavaScript data manipulation
│   └── ruby/
│       └── email-notification-service.step.rb # 💎 Ruby background processing
├── services/                        # Business logic and services
│   ├── pet-store.ts                # TypeScript service layer
│   └── types.ts                    # Shared type definitions
├── config/                          # Configuration files
├── package.json                     # Dependencies and scripts
└── tsconfig.json                   # TypeScript configuration
```

## 🔨 Available Commands

```bash
npm run dev    # Start development server with live reload
npm run start  # Start production server
npm run build  # Build the project
npm run test   # Run tests
```

## 📖 Understanding Steps

Motia unifies your entire backend through **Steps**. Everything is a step:

### 🌐 API Step
```typescript
export const config: ApiRouteConfig = {
  type: 'api',
  method: 'POST',
  path: '/basic-tutorial',
  bodySchema: z.object({ /* validation */ }),
  emits: ['process-food-order'], // Trigger other steps
}
```

### ⚡ Event Step
```typescript
export const config: EventConfig = {
  type: 'event',
  subscribes: ['process-food-order'], // Listen to events
  emits: ['notification'], // Emit new events
}
```

### ⏰ Cron Step
```typescript
export const config: CronConfig = {
  type: 'cron',
  cron: '*/5 * * * *', // Every 5 minutes
  emits: ['notification'],
}
```

## 🔄 Polyglot Workflow Example

This template showcases a **multi-language pet store workflow** that demonstrates how different languages excel at different tasks:

### 🌟 **Complete Workflow Chain**
1. **🟦 TypeScript API** → Creates pet records and triggers events
2. **🐍 Python AI Step** → Analyzes pet sentiment using AI/ML capabilities  
3. **🟡 JavaScript Engine** → Generates personalized recommendations
4. **💎 Ruby Service** → Sends beautifully formatted email notifications
5. **🟦 TypeScript Cron** → Audits and monitors system health

### 🔗 **Event-Driven Connections**
```
API (TypeScript) 
    ↓ emits: pet.created
Python AI Analyzer
    ↓ emits: sentiment.analyzed  
JavaScript Recommender
    ↓ emits: recommendations.generated
Ruby Email Service
    ↓ emits: email.sent
```

**Why Each Language?**
- **Python**: Perfect for AI/ML libraries (transformers, scikit-learn, tensorflow)
- **JavaScript**: Excellent for rapid data manipulation and business logic
- **Ruby**: Elegant syntax for background processing and integrations
- **TypeScript**: Strong typing for APIs and system reliability

## 🛠️ Development Workflow

1. **Edit Steps**: Modify files in the `steps/` directory
2. **Add Services**: Create business logic in `services/`
3. **Live Reload**: Changes are automatically reflected
4. **Visual Debug**: Use the workbench at `http://localhost:5000`

## 📊 Workbench Features

The Motia workbench provides:
- **Step Visualization**: See all your steps and their connections
- **Live Logs**: Monitor step execution in real-time
- **State Management**: View and manage application state
- **Event Tracing**: Track events through your workflow
- **API Testing**: Test endpoints directly from the UI

## 🎨 Customization

### Adding New Steps

1. Create a new `.step.ts` file in the `steps/` directory
2. Define your step configuration and handler
3. The framework automatically detects and loads it

### Extending Services

1. Add new service files in the `services/` directory
2. Import and use them in your step handlers
3. Update type definitions in `services/types.ts`

## 📚 Next Steps

- **[Motia Documentation](https://motia.dev/docs)** - Complete framework documentation
- **[Step Definitions](https://motia.dev/docs/concepts/steps)** - Learn about different step types
- **[Examples Repository](https://github.com/MotiaDev/motia-examples)** - 20+ example projects
- **[GitHub Repository](https://github.com/MotiaDev/motia)** - Source code and community

## 🌟 Features Highlights

- **🌍 True Polyglot Support**: Mix Python, JavaScript, TypeScript, Ruby in one workflow
- **🔄 Event-Driven Architecture**: Connect steps seamlessly across languages
- **🤖 AI/ML Ready**: Python steps with access to full PyPI ecosystem
- **📊 Built-in Observability**: Visual workflow tracking across all languages
- **⚡ Zero Configuration**: All languages pre-configured and ready
- **🔧 Language-Specific Strengths**: Use each language where it excels most

## 🚀 **Why Multi-Language Matters**

**Traditional Problem**: Forced to choose one language for entire backend
**Motia Solution**: Use the right language for each specific task

- **🐍 Python** → AI/ML, data science, complex algorithms
- **🟡 JavaScript** → Fast prototyping, JSON manipulation, modern ecosystem  
- **🟦 TypeScript** → Type-safe APIs, business logic, system reliability
- **💎 Ruby** → Beautiful code, rapid development, elegant integrations

## 💡 Tips

- Use the workbench to visualize your workflow before coding
- Start with the example steps and modify them for your use case
- Check the console logs in the workbench for debugging
- Experiment with different step types to build complex workflows

---

**Happy Building with Motia! 🚀**

*Built with ❤️ using the Motia Backend Framework*