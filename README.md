# 🔥 Motia Framework Template

A complete Replit template for the **Motia Backend Framework** - the unified runtime that eliminates backend fragmentation by bringing APIs, background jobs, workflows, and AI agents into one system.

## 🚀 Quick Start

This template comes pre-configured with everything you need to start building with Motia. Just click **Run** and start coding!

### What's Included

- ✅ **Complete Motia framework setup** with TypeScript support
- ✅ **Example workflow** demonstrating APIs, events, and cron jobs
- ✅ **Pre-configured development environment** ready to use
- ✅ **Sample project structure** with best practices
- ✅ **Visual workbench** for debugging and monitoring

## 🎯 Project Structure

```
motia-template/
├── steps/                    # Motia step definitions
│   ├── api.step.ts          # API endpoint example
│   ├── notification.step.ts  # Event handler example
│   ├── process-food-order.step.ts # Event processing
│   └── state-audit-cron.step.ts  # Scheduled job example
├── services/                 # Business logic and services
│   ├── pet-store.ts         # Sample service
│   └── types.ts             # Type definitions
├── config/                   # Configuration files
├── package.json             # Dependencies and scripts
└── tsconfig.json           # TypeScript configuration
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

## 🔄 Example Workflow

This template includes a complete pet store workflow:

1. **API Call** → Creates a pet and optional food order
2. **Event Processing** → Processes the food order and saves to state
3. **Notification** → Sends confirmation notification
4. **Audit Job** → Periodically checks for overdue orders

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

- **🔄 Event-Driven Architecture**: Connect steps through events
- **📊 Built-in Observability**: Track everything that happens
- **🌍 Multi-Language Support**: TypeScript, Python, JavaScript, and more
- **🤖 AI-Ready**: Perfect for building AI agents and workflows
- **⚡ Zero Configuration**: Start coding immediately
- **🔧 Developer Experience**: Rich tooling and debugging

## 💡 Tips

- Use the workbench to visualize your workflow before coding
- Start with the example steps and modify them for your use case
- Check the console logs in the workbench for debugging
- Experiment with different step types to build complex workflows

---

**Happy Building with Motia! 🚀**

*Built with ❤️ using the Motia Backend Framework*