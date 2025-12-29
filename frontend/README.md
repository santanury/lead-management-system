# Lead Automation & AI Scoring System

This is a Next.js application that provides a front-end for a lead automation and AI scoring system. It allows users to manage, score, and analyze leads efficiently.

## Getting Started

First, ensure you have Node.js and yarn installed. Then, run the development server:

```bash
yarn install
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result. The app will automatically redirect you to the main dashboard.

## User Guide

The application is organized into four main sections:

### 1. Dashboard

The **Dashboard** is the landing page and provides a high-level overview of your lead management system.

-   **Key Performance Indicators (KPIs):** At the top of the page, you'll find quick statistics for:
    -   **Total Leads:** The total number of leads in the system.
    -   **Qualified Leads:** The number of leads that have met the qualification criteria.
    -   **Avg. Score:** The average BANT score across all leads.
    -   **New Leads Today:** The number of new leads added today.
-   **Lead Conversion Rate Chart:** A visual representation of leads generated over time.
-   **Recent Leads Table:** A list of the 5 most recently added leads for quick access.

### 2. Leads

The **Leads** page is where you can view and manage all your leads in a comprehensive table.

-   **Search:** Use the search bar to find specific leads by name, email, or company.
-   **Filtering:** You can filter the lead list by:
    -   **Status:** (All, Qualified, Pending, Rejected)
    -   **Score:** (All, Low, Medium, High)
-   **Pagination:** The table is paginated for easy navigation through a large number of leads.

### 3. Scoring

The **Scoring** page allows you to configure the BANT (Budget, Authority, Need, Timeline) model used by the AI to score leads.

-   **Scoring Parameters:** Adjust the weight of each BANT component to align the AI's scoring logic with your business priorities. The weights must sum to 1.
-   **Sample AI Output:** A JSON object displays a sample of the data returned by the AI after scoring a lead, helping you understand the model's output.

### 4. Settings

The **Settings** page contains general configuration options for the application.

-   **Automation Settings:**
    -   **Auto-Lead Routing:** Toggle to automatically assign new leads to team members.
    -   **External Enrichment:** Toggle to enable or disable third-party services for data enrichment.
-   **AI Model Selection:** Choose the Large Language Model (LLM) you want to use for lead scoring and analysis from the dropdown menu.

## Tech Stack

-   **Framework:** Next.js (App Router)
-   **Language:** TypeScript
-   **Styling:** TailwindCSS
-   **UI Components:** shadcn/ui
-   **Charts:** Recharts
-   **State Management:** React State/Context (Zustand planned for future)