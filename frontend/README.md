# 🎨 Lead Management Frontend

> The modern, responsive user interface for the AI Lead Management System. Built with Next.js 16, Tailwind CSS v4, and Shadcn UI.

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- npm (or yarn/pnpm)

### installation

1.  Navigate to the directory:

    ```bash
    cd frontend
    ```

2.  Install dependencies:

    ```bash
    npm install
    # or
    yarn install
    ```

3.  **Environment Setup** (Important):
    Create a `.env.local` file in the root of `frontend/` to configure the backend connection:

    ```env
    NEXT_PUBLIC_API_URL=http://localhost:8000
    ```

4.  Run the development server:

    ```bash
    npm run dev
    ```

    Open [http://localhost:3000](http://localhost:3000) to view the application.

## 📂 Architecture & Structure

```
frontend/
├── app/                  # Next.js App Router pages
│   ├── dashboard/        # Dashboard view
│   ├── leads/            # Lead management & lists
│   ├── scoring/          # AI scoring configuration
│   └── layout.tsx        # Main application layout
├── components/           # Reusable UI components
│   ├── ui/               # Shadcn UI primitives (buttons, dialogs, etc.)
│   └── lead-details...   # Feature-specific components
├── lib/                  # Utilities and API clients
│   └── api.ts            # Axios configuration & API calls
└── styles/               # Global styles (Tailwind)
```

## ✨ Key Features

### 1. 📊 Interactive Dashboard

- Real-time KPIs (Total Leads, Conversion Rate).
- Visual charts powered by `Recharts`.
- Recent leads feed.

### 2. 🤖 AI-Enriched Lead View

- **Lead Details Dialog**: A complex component that displays:
  - **Company Logo**: Auto-fetched via Google Favicons.
  - **AI Summary**: Narrative explanation of the lead's score.
  - **BANT Analysis**: Breakdown of Budget, Authority, Need, and Timeline.
  - **Strategic Hints**: AI-generated follow-up questions.

### 3. ⚙️ Configuration

- **Theme Toggle**: Dark/Light mode support.
- **Scoring Settings**: Adjust the weights for BANT parameters vs. Intent signals.

## 🛠️ Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Styling**: Tailwind CSS v4
- **Components**: Radix UI + Shadcn
- **State**: Redux Toolkit (for global state management)
- **Icons**: Lucide React

## 🧪 Best Practices

- **Component Composition**: UI is built using small, composable atoms.
- **Server/Client Components**: Strategic use of `"use client"` for interactive parts while keeping pages server-rendered where possible.
- **Type Safety**: Full TypeScript integration.
