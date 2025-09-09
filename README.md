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
├── steps/                                    # Motia step definitions
│   ├── # TypeScript Workflow (ts.* events)
│   ├── api.step.ts                          # 🟦 Main API endpoint  
│   ├── process-food-order.step.ts           # 🟦 Order processing
│   ├── notification.step.ts                 # 🟦 Notifications
│   ├── state-audit-cron.step.ts             # 🟦 Scheduled audits
│   │
│   ├── # Separate Language Workflows  
│   ├── python-api.step.ts                   # 🟦→🐍 Python workflow trigger
│   ├── javascript-api.step.ts               # 🟦→🟡 JavaScript workflow trigger  
│   ├── ruby-api.step.ts                     # 🟦→💎 Ruby workflow trigger
│   │
│   ├── # Language-Specific Steps
│   ├── python/
│   │   └── ai-sentiment-analyzer.step.py   # 🐍 AI/ML processing (py.* events)
│   ├── javascript/
│   │   └── pet-recommendation-engine.step.js # 🟡 Data manipulation (js.* events)
│   ├── ruby/
│   │   └── email-notification-service.step.rb # 💎 Background processing (rb.* events)
│   │
│   ├── # Cross-Language Workflow Example
│   ├── cross-language-api.step.ts           # 🌍 Multi-language trigger
│   ├── cross-language-python.step.py        # 🐍 Cross-language AI step
│   ├── cross-language-javascript.step.js    # 🟡 Cross-language recommendations
│   └── cross-language-ruby.step.rb          # 💎 Cross-language notifications
├── services/                                 # Business logic and services
│   ├── pet-store.ts                         # TypeScript service layer
│   └── types.ts                             # Shared type definitions
├── config/                                   # Configuration files
├── package.json                              # Dependencies and scripts  
└── tsconfig.json                            # TypeScript configuration
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

## 🔄 **Workflow Patterns: Separate vs Cross-Language**

This template demonstrates **two important workflow patterns** that solve the common problem of event collision between languages:

### 🎯 **Pattern 1: Separate Language Workflows (Recommended)**

Each language has its **own independent workflow** using language-prefixed events:

```
🟦 TypeScript Workflow:
POST /basic-tutorial → ts.pet.created → ts.order.processed → ts.notification

🐍 Python Workflow:  
POST /python/analyze-pet → py.pet.analyze → py.sentiment.analyzed

🟡 JavaScript Workflow:
POST /javascript/recommend → js.pet.recommend → js.recommendations.generated

💎 Ruby Workflow:
POST /ruby/send-notification → rb.send.email → rb.email.sent
```

**✅ Benefits:**
- **No event collision** - each language workflow runs independently
- **Cleaner logs** - only relevant steps are triggered
- **Easy debugging** - clear separation of concerns
- **Scalable** - each workflow can scale independently

### 🌍 **Pattern 2: Intentional Cross-Language Communication**

When you **want** languages to work together, use the `cross.` prefix:

```
🌍 Cross-Language Pipeline:
POST /cross-language/full-pipeline 
  ↓ cross.python.analyze
🐍 Python AI Analysis
  ↓ cross.analysis.complete  
🟡 JavaScript Recommendations
  ↓ cross.recommendations.ready
💎 Ruby Email Service
  ↓ cross.workflow.complete
```

**✅ Benefits:**
- **Intentional communication** - explicitly designed for cross-language workflows
- **Language-specific strengths** - each step uses the best language for its task  
- **Shared state** - data flows seamlessly between languages
- **Full observability** - trace the complete multi-language journey

### 🎛️ **Event Naming Convention**

| Pattern | Event Format | Example | Use Case |
|---------|-------------|---------|----------|
| **Separate** | `{lang}.{domain}.{action}` | `py.pet.analyze` | Independent workflows |
| **Cross-Language** | `cross.{step}.{action}` | `cross.analysis.complete` | Multi-language pipelines |
| **TypeScript** | `ts.{domain}.{action}` | `ts.order.processed` | TypeScript-specific workflow |

### 🚀 **Quick Test**

Try these endpoints to see the different patterns:

```bash
# Separate Workflows (won't interfere with each other)
curl -X POST /python/analyze-pet -d '{"pet":{"id":1,"name":"Buddy"}}'
curl -X POST /javascript/recommend -d '{"pet":{"id":2,"name":"Luna"}}'  
curl -X POST /ruby/send-notification -d '{"pet":{"name":"Max","owner_email":"owner@example.com"}}'

# Cross-Language Pipeline (all languages work together)
curl -X POST /cross-language/full-pipeline -d '{"pet":{"id":3,"name":"Charlie","description":"Happy dog","owner_email":"owner@example.com"}}'
```

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

## 💡 **Best Practices**

### 🎯 **Choosing Workflow Patterns**

**Use Separate Workflows When:**
- Building independent features (user management, payments, analytics)
- Each language workflow serves different business domains  
- You want to avoid event collision and keep logs clean
- Different teams work on different language components

**Use Cross-Language Workflows When:**
- You need the specific strengths of each language in one pipeline
- Building AI/ML workflows (Python AI → JavaScript API → Ruby notifications)
- Data processing pipelines that benefit from polyglot processing
- You want to demonstrate Motia's cross-language capabilities

### 🛠️ **Development Tips**

- **📊 Visual Debugging**: Use the workbench to see workflow separation clearly
- **🏷️ Event Naming**: Always use language prefixes (`ts.`, `py.`, `js.`, `rb.`, `cross.`)
- **📝 Clear Logs**: Language prefixes make debugging much easier
- **🧪 Test Separation**: Try triggering different language workflows simultaneously
- **🔍 Monitor Warnings**: Motia warns about events with no subscribers - use this to verify separation

### 🚀 **Getting Started**

1. **Start Simple**: Begin with separate language workflows  
2. **Add Cross-Language**: Once comfortable, experiment with `cross.*` events
3. **Use the Workbench**: Visualize your workflows before coding
4. **Check Event Flow**: Ensure events go to intended subscribers only
5. **Scale Gradually**: Add more languages and complexity as needed

---

**Happy Building with Motia! 🚀**

*Built with ❤️ using the Motia Backend Framework*