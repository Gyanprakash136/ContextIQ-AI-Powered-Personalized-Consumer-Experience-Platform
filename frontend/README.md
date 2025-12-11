
# ContextIQ Frontend 🧠✨

The modern, AI-powered interface for **ContextIQ**, the specialized consumer experience platform. Built for speed, aesthetics, and seamless interaction with the ContextIQ Agent.

## 🚀 Key Features

*   **Cybernetic UI**: Premium dark mode aesthetic with glassmorphism, smooth animations, and responsive layouts.
*   **Real-time Chat**: Streaming AI responses with Markdown support and product visualization.
*   **Rich Product Cards**: Automated extraction and display of product details (Images, Prices, Links) directly in chat.
*   **Robust Session Management**:
    *   Guest mode support.
    *   Seamless history persistence (Guest -> User transition).
    *   Chat titles auto-generated from context.
*   **Secure Authentication**: Integrated with **Firebase Auth** (Google Sign-In).

## 🛠️ Tech Stack

*   **Framework**: [React](https://react.dev/) + [Vite](https://vitejs.dev/) (Fast HMR)
*   **Language**: [TypeScript](https://www.typescriptlang.org/) for type safety.
*   **Styling**: [Tailwind CSS](https://tailwindcss.com/) + [Shadcn/UI](https://ui.shadcn.com/) components.
*   **State Management**: [Zustand](https://github.com/pmndrs/zustand) (with persistence).
*   **Routing**: [React Router DOM](https://reactrouter.com/).
*   **Icons**: Material Symbols Outlined.

---

## ⚙️ Setup & Installation

### 1. Prerequisites
*   Node.js (v18+ recommended)
*   npm or yarn

### 2. Clone & Install
```bash
cd frontend
npm install
```

### 3. Environment Configuration
Create a `.env` file in the `frontend` root. **Use the following template:**

```env
# API Connection
VITE_API_URL=http://127.0.0.1:8000  # Or your deployed backend URL

# Firebase Authentication (Get these from Firebase Console)
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_bucket.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
VITE_FIREBASE_MEASUREMENT_ID=your_measurement_id
```

### 4. Run Locally
Start the development server:

```bash
npm run dev
```
Access the app at `http://localhost:8080`.

---

## 📦 Deployment (Vercel)

This frontend is optimized for **Vercel** deployment.

1.  **Push to GitHub**.
2.  **Import** project in Vercel.
3.  **Root Directory**: Select `frontend`.
4.  **Environment Variables**: Add all variables from your `.env` (excluding comments) into Vercel's settings.
5.  **Deploy**!

> **Note**: For SPA routing to work correctly on Vercel, a `vercel.json` file is included in the project root.

---

## 📂 Project Structure

```
frontend/
├── src/
│   ├── api/            # API client (realApi.ts)
│   ├── assets/         # Static assets (images, videos)
│   ├── components/     # Reusable UI components (Chat, Layout, UI kit)
│   ├── hooks/          # Custom hooks (use-toast, etc.)
│   ├── lib/            # Utilities (firebase.ts, utils.ts)
│   ├── pages/          # Page views (Index, Chat, Auth)
│   └── stores/         # Global state (sessionStore.ts)
├── public/             # Public static files
├── index.html          # Entry point
└── tailwind.config.ts  # Theme configuration
```

## 🤝 Contributing

1.  Fork the repo.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit changes.
4.  Push to branch.
5.  Open a Pull Request.
