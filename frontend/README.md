# ISA_D Frontend

This directory contains the web frontend for the ISA_D platform, built with Next.js and React.

## 📁 Structure Overview

```
frontend/
├── src/                    # Source code
│   ├── app/               # Next.js app router
│   ├── components/        # React components
│   ├── lib/               # Utility libraries
│   ├── styles/            # CSS and styling
│   └── types/             # TypeScript types
├── public/                # Static assets
├── .next/                 # Build output (generated)
├── package.json           # Dependencies and scripts
├── next.config.js         # Next.js configuration
├── tailwind.config.js     # Tailwind CSS config
├── tsconfig.json          # TypeScript configuration
└── eslint.config.js       # ESLint configuration
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running (see `../README.md`)

### Installation

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   # or
   yarn install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

3. **Open browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
# Build the application
npm run build

# Start production server
npm start

# Export static files (optional)
npm run export
```

## ⚙️ Configuration

### Environment Variables

Create a `.env.local` file:

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_WS_URL=ws://localhost:8001

# Authentication
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key

# Feature flags
NEXT_PUBLIC_ENABLE_CHAT=true
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```

### Next.js Configuration

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['localhost'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8001/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig
```

## 🏗️ Architecture

### App Router Structure

```
src/app/
├── layout.tsx            # Root layout
├── page.tsx              # Home page
├── globals.css           # Global styles
├── (auth)/               # Authentication routes
│   ├── login/
│   └── register/
├── dashboard/            # Main application
│   ├── layout.tsx
│   ├── page.tsx
│   └── [other pages]
├── api/                  # API routes (if needed)
└── loading.tsx           # Loading UI
```

### Component Structure

```
src/components/
├── ui/                   # Reusable UI components
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Modal.tsx
│   └── ...
├── layout/               # Layout components
│   ├── Header.tsx
│   ├── Sidebar.tsx
│   └── Footer.tsx
├── forms/                # Form components
├── charts/               # Data visualization
└── [feature]/            # Feature-specific components
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `ChatInterface` | Real-time chat with agents |
| `DocumentViewer` | PDF and document display |
| `ComplianceDashboard` | Compliance status overview |
| `ResearchPanel` | Research task management |
| `AnalyticsCharts` | Performance metrics |

## 🎨 Styling

### Tailwind CSS

The frontend uses Tailwind CSS for styling:

```jsx
// Example component
export default function Button({ children, variant = 'primary' }) {
  const baseClasses = 'px-4 py-2 rounded-md font-medium transition-colors'
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
  }

  return (
    <button className={`${baseClasses} ${variantClasses[variant]}`}>
      {children}
    </button>
  )
}
```

### Theme Configuration

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        isa: {
          primary: '#2563eb',
          secondary: '#64748b',
          accent: '#f59e0b',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
```

## 🔧 Development

### Available Scripts

```json
// package.json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "test:watch": "jest --watch",
    "type-check": "tsc --noEmit"
  }
}
```

### Development Workflow

1. **Start development server**: `npm run dev`
2. **Make changes** to components
3. **Check TypeScript**: `npm run type-check`
4. **Run tests**: `npm test`
5. **Lint code**: `npm run lint`

### Hot Reload

The development server supports hot reload for:
- React components
- CSS changes
- TypeScript files
- Configuration files

## 🔗 API Integration

### Backend Communication

```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL

export async function fetchAgents() {
  const response = await fetch(`${API_BASE}/agents`)
  return response.json()
}

export async function submitResearchTask(task: ResearchTask) {
  const response = await fetch(`${API_BASE}/research`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(task),
  })
  return response.json()
}
```

### WebSocket Connection

```typescript
// lib/websocket.ts
import { io } from 'socket.io-client'

export function createSocketConnection() {
  return io(process.env.NEXT_PUBLIC_WS_URL!, {
    transports: ['websocket'],
  })
}

// Usage in component
useEffect(() => {
  const socket = createSocketConnection()

  socket.on('agent_response', (data) => {
    // Handle real-time updates
  })

  return () => socket.disconnect()
}, [])
```

## 🔐 Authentication

### NextAuth.js Setup

```typescript
// pages/api/auth/[...nextauth].ts
import NextAuth from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'

export default NextAuth({
  providers: [
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        // Validate credentials with backend
        const response = await fetch(`${process.env.API_URL}/auth/login`, {
          method: 'POST',
          body: JSON.stringify(credentials),
        })

        if (response.ok) {
          return await response.json()
        }
        return null
      }
    })
  ],
  pages: {
    signIn: '/auth/login',
    signUp: '/auth/register',
  },
})
```

### Protected Routes

```typescript
// components/ProtectedRoute.tsx
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession()
  const router = useRouter()

  if (status === 'loading') {
    return <div>Loading...</div>
  }

  if (!session) {
    router.push('/auth/login')
    return null
  }

  return <>{children}</>
}
```

## 📊 State Management

### React Context

```typescript
// contexts/AppContext.tsx
import { createContext, useContext, useReducer } from 'react'

interface AppState {
  user: User | null
  agents: Agent[]
  currentTask: Task | null
}

type AppAction = 
  | { type: 'SET_USER'; payload: User }
  | { type: 'SET_AGENTS'; payload: Agent[] }
  | { type: 'SET_CURRENT_TASK'; payload: Task }

const AppContext = createContext<{
  state: AppState
  dispatch: React.Dispatch<AppAction>
} | null>(null)

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState)

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within AppProvider')
  }
  return context
}
```

## 🧪 Testing

### Component Testing

```typescript
// __tests__/Button.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Button from '../components/Button'

describe('Button', () => {
  it('renders children correctly', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('handles click events', async () => {
    const handleClick = jest.fn()
    const user = userEvent.setup()

    render(<Button onClick={handleClick}>Click me</Button>)
    await user.click(screen.getByText('Click me'))

    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

### E2E Testing

```typescript
// e2e/chat.spec.ts
import { test, expect } from '@playwright/test'

test('user can send message to agent', async ({ page }) => {
  await page.goto('http://localhost:3000')

  // Login
  await page.fill('[data-testid="email"]', 'user@example.com')
  await page.fill('[data-testid="password"]', 'password')
  await page.click('[data-testid="login-button"]')

  // Send message
  await page.fill('[data-testid="message-input"]', 'Hello agent')
  await page.click('[data-testid="send-button"]')

  // Check response
  await expect(page.locator('[data-testid="agent-response"]')).toBeVisible()
})
```

## 🚀 Deployment

### Docker Build

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

### Kubernetes Deployment

```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: isa-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: isa-frontend
  template:
    metadata:
      labels:
        app: isa-frontend
    spec:
      containers:
        - name: frontend
          image: isa/frontend:latest
          ports:
            - containerPort: 3000
          env:
            - name: NEXT_PUBLIC_API_URL
              value: "http://isa-api:8001"
```

## 📈 Performance

### Optimization Techniques

- **Code Splitting**: Dynamic imports for large components
- **Image Optimization**: Next.js Image component
- **Caching**: Service worker for static assets
- **Bundle Analysis**: Webpack bundle analyzer

### Monitoring

```typescript
// lib/analytics.ts
import { init, track } from '@vercel/analytics'

export function initAnalytics() {
  if (process.env.NODE_ENV === 'production') {
    init()
  }
}

export function trackEvent(name: string, properties?: Record<string, any>) {
  if (process.env.NODE_ENV === 'production') {
    track(name, properties)
  }
}
```

## 📚 Related Documentation

- [Backend API](../src/README.md)
- [Project Structure](../docs/project-structure.md)
- [Deployment Guide](../docs/deployment/)
- [UI/UX Guidelines](../docs/ui-guidelines.md)

## 🤝 Contributing

### Frontend Development

1. Follow React and Next.js best practices
2. Use TypeScript for type safety
3. Write tests for new components
4. Follow component composition patterns
5. Optimize for performance

### Code Standards

- **TypeScript**: Strict type checking enabled
- **ESLint**: Airbnb config with React rules
- **Prettier**: Consistent code formatting
- **Testing**: Jest with React Testing Library
- **Accessibility**: WCAG 2.1 AA compliance

This frontend provides a modern, responsive interface for interacting with the ISA_D intelligent agent system.