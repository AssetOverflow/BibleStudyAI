<!-- @format -->

# Gemini Frontend Development Plan

This document outlines the development plan for the Koinonia House frontend. The frontend is a React application built with Vite and TypeScript, responsible for providing a rich and interactive user experience.

## 1. Project Setup & Configuration

- **Environment Variables**: All API and WebSocket URLs will be managed through `.env` files (`.env.development`, `.env.production`). The `VITE_API_URL` and `VITE_WS_URL` variables will be used to connect to the backend.
- **Styling**: A consistent styling approach will be used. We will use a combination of global styles (`index.css`, `App.css`) and component-specific CSS files. A modern CSS framework or utility library (like Tailwind CSS or Material-UI) could be considered for rapid development.
- **Component Structure**: Components will be organized logically within the `src/components` directory.

## 2. Core Components

This section details the main components that make up the user interface.

### `Header.tsx`

- Displays the application title and logo.
- Contains the main navigation links.
- Shows the current user's profile picture and name, with a dropdown for profile settings and logout.

### `VerticalNav.tsx`

- A persistent vertical navigation bar on the left side of the screen.
- Provides quick access to the main features: Dashboard, Bible Explorer, Prophecy Lab, Note Stack, Study Groups, and Knowledge Graph.

### `Dashboard.tsx`

- The main landing page after login.
- Displays a welcome message.
- Provides a high-level overview of recent activity, such as recent notes, unread messages in study groups, and suggested topics for exploration.

### `ChatInterface.tsx`

- The central component for interacting with the AI.
- Contains a chat history view (`ChatHistory.tsx`) and a message input form.
- Handles sending user messages to the backend and displaying the AI's responses.
- Manages chat sessions.

### `BibleExplorer.tsx`

- Allows users to navigate and read the Bible.
- Dropdowns to select book, chapter, and verse.
- Displays the text of the selected passage.
- Includes a search functionality to find verses containing specific keywords.

### `NoteTaking.tsx` & `NoteStack.tsx`

- `NoteTaking.tsx`: A rich text editor for users to write and format notes. Notes can be linked to Bible verses, topics, or other resources.
- `NoteStack.tsx`: A view to browse, search, and manage all created notes.

### `KnowledgeGraph.tsx`

- Visualizes the knowledge graph data received from the backend.
- Uses a library like `react-force-graph` or `vis.js` to render nodes and edges.
- Allows users to interact with the graph (zoom, pan, click on nodes for more information).

### `ProphecyLab.tsx`

- A dedicated section for exploring biblical prophecy.
- Lists prophecy topics.
- Displays detailed analysis, related scriptures, and timelines for selected topics.

### `StudyGroups.tsx`

- A feature for collaborative learning.
- Users can create, join, and participate in study groups.
- Each group has its own chat, shared notes, and resources.

### `UserProfileModal.tsx`

- A modal window for users to view and edit their profile information.

## 3. State Management

- **React Query (TanStack Query)**: Will be used for managing server state. It simplifies data fetching, caching, synchronization, and updates from the backend API.
- **Zustand/Redux Toolkit**: For managing global client state that needs to be shared across multiple components (e.g., user authentication status, theme settings).

## 4. Routing

- **React Router**: Will be used to handle client-side routing. Routes will be defined for each main feature of the application.
  - `/`: Dashboard
  - `/bible`: Bible Explorer
  - `/notes`: Note Stack
  - `/graph`: Knowledge Graph
  - `/prophecy`: Prophecy Lab
  - `/groups`: Study Groups
  - `/groups/{id}`: Specific Study Group
  - `/login`: Login Page
  - `/profile`: User Profile

## 5. API Integration

- **Axios/Fetch**: A dedicated API client module will be created to handle all HTTP requests to the FastAPI backend. This module will manage authentication tokens and base URLs.
- **WebSocket**: A WebSocket client will be implemented to handle real-time communication for features like chat and study group discussions.

## 6. Development and Deployment

- **Local Development**: The Vite development server will be used for local development with hot module replacement.
- **Building**: The application will be built for production using `npm run build`, creating optimized static assets.
- **Docker**: The `Dockerfile` in the `frontend` directory will be used to create a production-ready container image to be served by the Docker environment.
