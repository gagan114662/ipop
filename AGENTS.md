# AGENTS.md

## Project Overview

This is a Motia backend application - a unified framework for building **ANY type of production-ready backend**. Whether you're creating e-commerce platforms, social networks, fintech applications, IoT systems, healthcare platforms, gaming backends, or any other custom application - Motia provides the flexible foundation you need.

**Unlimited Application Possibilities:**
- 🛍️ E-commerce: product catalogs, payments, inventory, order processing
- 📱 Social platforms: user feeds, real-time chat, notifications, content moderation
- 💰 Fintech: transaction processing, account management, compliance workflows  
- 🏥 Healthcare: patient records, appointment scheduling, medical data processing
- 🎮 Gaming: player management, leaderboards, real-time multiplayer features
- 🏢 Enterprise: CRM systems, workflow automation, reporting dashboards
- **...and literally any other type of backend your business needs**

**Unified Multi-Language Architecture:**
Motia seamlessly combines JavaScript, TypeScript, Python, and Ruby in a single event-driven system with APIs, background jobs, real-time streaming, AI agents, and complex workflows - all following proven architectural patterns.

**Key Concepts:**
- **Steps**: Core building blocks (API, Event, Cron, Stream, NOOP)
- **Flows**: Logical groupings of related steps
- **Topics**: Event channels for step communication
- **State**: Persistent data management scoped by traceId
- **Streams**: Real-time data channels for live features

## Setup Commands

- Install dependencies: `pnpm install`
- Setup Python environment: `pnpm python-setup`
- Start development server: `pnpm dev`
- Start with workbench UI: `pnpm dev:workbench`  
- Run tests: `pnpm test`
- Build project: `pnpm build`

## Agents Folder Structure

The `agents/` folder contains the proper Motia documentation structure and development rules:

### Documentation Structure
- **`agents/index.mdc`** - Main index with references to database migrations, real-time events, state management, and authentication
- **`agents/architecture/`** - Core architecture and technical patterns
  - `database/database.mdc` - Knex database connections, repository patterns, camelCase/snake_case conversion
  - `database/database-migration.mdc` - Knex migration setup and commands
  - `architecture.mdc` - Project structure, DDD principles, services organization, logging practices
  - `error-handling.mdc` - Custom error classes (BaseError), core middleware for error handling
- **`agents/rules/motia/`** - Complete Motia step implementation guides
  - `api-steps.mdc` - HTTP endpoint creation with Zod validation, request/response handling
  - `event-steps.mdc` - Background event processing for async tasks (LLM calls, file processing, emails)
  - `cron-steps.mdc` - Scheduled tasks with cron expressions and emit patterns
  - `ui-steps.mdc` - Custom Workbench visualization components (EventNode, ApiNode, CronNode)
  - `virtual-steps.mdc` - NOOP steps and virtual connections for Workbench flow visualization
  - `middlewares.mdc` - Middleware patterns for authentication, validation, error handling
  - `realtime-streaming.mdc` - Motia Streams for real-time data (chat, collaboration, live updates)
  - `state-management.mdc` - Cross-step state storage and caching patterns

### Using the Agents Folder

When developing with Motia, always reference the appropriate `.mdc` files in the agents folder:

1. **For API Development**: Use `agents/rules/motia/api-steps.mdc` for HTTP endpoints with Zod schemas and request/response patterns
2. **For Event Processing**: Use `agents/rules/motia/event-steps.mdc` for async background tasks (LLM calls, file processing, emails, webhooks)
3. **For Scheduled Jobs**: Use `agents/rules/motia/cron-steps.mdc` for cron expressions and scheduled task patterns
4. **For Real-time Features**: Use `agents/rules/motia/realtime-streaming.mdc` for Motia Streams (chat, collaboration, live data)
5. **For Database Work**: Use `agents/architecture/database/` for Knex patterns, migrations, and repository structure
6. **For Error Handling**: Use `agents/architecture/error-handling.mdc` for custom error classes and core middleware
7. **For Project Structure**: Use `agents/architecture/architecture.mdc` for DDD patterns, services organization, and logging
8. **For Middleware**: Use `agents/rules/motia/middlewares.mdc` for authentication, validation, and error handling middleware
9. **For Workbench UI**: Use `agents/rules/motia/ui-steps.mdc` for custom step visualization components
10. **For Workflow Visualization**: Use `agents/rules/motia/virtual-steps.mdc` for NOOP steps and virtual connections

The agents folder provides comprehensive, production-ready Motia patterns with detailed code examples and should be the primary reference for all development work.



### Step Naming Conventions
- Use kebab-case for filenames: `resource-processing.step.ts`, `data_processor_step.py`
- Include `.step` before language extension (TypeScript/JavaScript) or `_step` for Python
- Match handler names to config names
- Use descriptive, action-oriented names

### Code Style Guidelines
- **JavaScript**: Use modern ES6+ features, async/await, proper error handling
- **TypeScript**: Use strict mode, prefer functional patterns, leverage type safety
- **Python**: Follow PEP 8, use async/await for handlers, type hints recommended
- **Ruby**: Follow Ruby style guide, use snake_case, leverage Ruby idioms
- **Imports**: Group external, internal, relative imports consistently
- **Error Handling**: Always use try/catch with proper logging and context
- **Logging**: Use structured logging with traceId context for traceability


## Multi-language Integration

### Language Selection Guide
- **JavaScript**: Rapid prototyping, simple APIs, real-time features, event-driven processing
- **TypeScript**: Complex APIs, type-safe business logic, frontend integration, production systems
- **Python**: ML/AI processing, data science, scientific computing, complex algorithms
- **Ruby**: Background jobs, data manipulation, system integration, batch processing

### Cross-language Data Flow
1. **JavaScript/TypeScript** receives HTTP requests and validates data
2. **Python** processes ML/AI workloads and complex computations
3. **Ruby** handles data exports and background processing
4. All languages communicate seamlessly via Motia events and shared state

## Available Cursor Rule Patterns

The cursor rules provide comprehensive, production-ready patterns that work for **absolutely any application type**. These patterns are completely generic and adaptable - never limiting you to specific domains or use cases:

### Core Application Patterns
- **Complete Application Architecture** - Full-stack project structure and organization
- **Authentication & Authorization** - JWT, OAuth, multi-factor auth, session management  
- **Real-time Streaming** - Live updates, notifications, collaborative features
- **Multi-language Workflows** - TypeScript, Python, Ruby unified workflows

### API & Integration Patterns
- **RESTful API Design** - CRUD operations, filtering, pagination, versioning
- **Batch Operations** - Bulk processing, transaction handling
- **Rate Limiting & Security** - Protection, validation, middleware
- **External Service Integration** - Third-party APIs, webhooks

### Background Processing Patterns
- **Job Queue Systems** - Async task processing, retry logic
- **Scheduled Tasks** - Cron jobs, maintenance, monitoring
- **Long-running Processes** - Data processing, exports, analysis
- **Process Coordination** - Multi-step job workflows

### AI Agent Patterns
- **Intelligent Agents** - Planning, execution, decision making
- **Content Generation** - Text, code, document creation
- **Multi-agent Coordination** - Agent collaboration, workflow orchestration
- **AI-powered Workflows** - Automated decision trees, smart processing

### Workflow Patterns
- **Linear Workflows** - Sequential step-by-step processes
- **Parallel Processing** - Fan-out/fan-in, concurrent execution
- **State Machines** - Complex approval flows, status management
- **Conditional Routing** - Dynamic process routing, business rules

### Production Patterns
- **Deployment & DevOps** - Docker, CI/CD, monitoring, health checks
- **Error Handling** - Comprehensive error management, retry strategies
- **Performance Optimization** - Caching, compression, response optimization
- **Testing Strategies** - Unit tests, integration tests, workflow testing

## Authentication Patterns

Always implement:
- JWT token management with refresh tokens
- Password hashing with bcrypt (12+ rounds)
- Email verification flows
- Rate limiting on auth endpoints
- Proper middleware for protected routes
- Structured error responses

## Real-time Features

For live applications:
- Use Motia Streams for real-time data
- Implement proper cleanup with TTL
- Broadcast events to specific users/rooms
- Handle connection state properly
- Implement reconnection logic

## State Management

- Use traceId for flow-scoped state
- Implement hierarchical keys (`user:${id}:profile`)
- Clean up state when flows complete
- Use appropriate TTL for data retention
- Type state data properly in TypeScript

## Testing Strategy

- Unit tests for all step handlers
- Integration tests for complete flows
- Mock external services in tests
- Test error scenarios and edge cases
- Use `@motiadev/test` utilities
- Test multi-language workflows end-to-end

## Production Deployment

### Environment Variables
Set required environment variables:
- `JWT_SECRET` (32+ characters)
- `DATABASE_URL` for persistence
- `REDIS_URL` for state management
- External service APIs (OpenAI, SendGrid, etc.)

### Docker Deployment
- Use multi-stage builds
- Install all language runtimes
- Set proper health checks
- Use non-root users
- Configure resource limits

### Monitoring
- Implement `/health` endpoint
- Use structured logging (JSON format)
- Set up error tracking (Sentry)
- Monitor system metrics
- Implement alerting for critical issues

## Security Best Practices

- Validate all inputs with Zod schemas
- Use parameterized queries for databases
- Implement proper CORS configuration
- Add security headers (helmet)
- Rate limit all public endpoints
- Never log sensitive data
- Use HTTPS in production
- Implement proper session management

## Performance Guidelines

- Use compression for large responses
- Implement caching strategies
- Optimize database queries
- Use connection pooling
- Monitor response times
- Implement request timeouts
- Use CDN for static assets

## Error Handling Standards

- Always use structured error responses
- Log errors with full context (traceId, userId, etc.)
- Don't expose internal errors to users
- Implement proper HTTP status codes
- Use circuit breakers for external services
- Implement retry logic with exponential backoff

## Development Workflow

1. **Plan**: Define the flow and required steps
2. **Reference**: Check the appropriate `.mdc` files in the `agents/` folder for patterns and best practices
3. **Create**: Start with step configurations following the agents folder guidelines
4. **Implement**: Write handlers with proper error handling using the documented patterns
5. **Test**: Add unit and integration tests
6. **Integrate**: Connect steps via topics/events
7. **Monitor**: Add logging and observability
8. **Deploy**: Use proper CI/CD pipelines

### Quick Reference for Development Steps

Before creating any Motia components, always check:
- `agents/index.mdc` for general guidance
- Specific `.mdc` files in `agents/rules/motia/` for step-type patterns  
- `agents/architecture/` files for system-level decisions

## Common Patterns

### Production Application Style
- Multi-language workflows (TypeScript + Python + Ruby)
- Real-time data streaming and live updates
- Authentication with user sessions and JWT management
- AI/ML integration for intelligent processing
- Comprehensive monitoring and health checks
- Event-driven architecture with proper error handling

### Data Processing Pipeline
1. API Step (JS/TS) - Receive and validate incoming data
2. Event Step (Python) - Process with ML/AI or complex computations
3. Event Step (JS/TS) - Format results and trigger notifications
4. Stream updates for real-time UI synchronization

### Background Job Processing
1. API Step (JS/TS) - Queue job with parameters and metadata
2. Event Step (Ruby) - Process job asynchronously with retry logic
3. Cron Step - Clean up completed jobs and maintenance
4. Notification Step - Send completion alerts and status updates

## Debugging Tips

- Use `motia dev:debug` for verbose logging
- Check step handler names match config names
- Verify topic names in subscribes/emits arrays
- Use Workbench UI to visualize flows
- Check state data in development tools
- Monitor logs for validation errors
- Test with curl/Postman for API debugging

## External Integrations

When integrating external services:
- Always use environment variables for API keys
- Implement proper error handling and retries
- Add circuit breakers for reliability
- Mock services in tests
- Log integration attempts and failures
- Handle rate limits gracefully
- Validate responses from external APIs

Remember: Motia excels at building production-ready backends quickly by unifying different languages and paradigms in a single, event-driven system.
