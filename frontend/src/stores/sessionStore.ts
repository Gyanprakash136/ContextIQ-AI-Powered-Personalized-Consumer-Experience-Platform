import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { auth, googleProvider } from '@/lib/firebase';
import { signInWithPopup, signOut, onAuthStateChanged, User as FirebaseUser } from 'firebase/auth';
import { Product } from '@/api/api';

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}

import { Product } from '../api/realApi';

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Message {
  id: string;
  sender: 'user' | 'assistant';
  type: 'text' | 'image';
  content: string;
  imageUrl?: string;
  products?: Product[];
  timestamp: Date;
  products?: Product[];
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

interface SessionState {
  user: User | null;
  isAuthenticated: boolean;
  currentSessionId: string | null;
  sessions: ChatSession[];

  // Auth actions
  login: () => Promise<void>;
  loginAsGuest: () => void;
  logout: () => Promise<void>;

  // Chat actions
  createSession: () => string;
  setCurrentSession: (sessionId: string) => void;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  getCurrentSession: () => ChatSession | null;
}

const generateId = () => Math.random().toString(36).substring(2, 15);

export const useSessionStore = create<SessionState>()(
  persist(
    (set, get) => {
      // Initialize Auth Listener
      // Note: Zustand persist might conflict with async listeners if not careful.
      // We'll set up the listener separately or rely on checking auth state on mount in App.tsx

      return {
        user: null,
        isAuthenticated: false,
        currentSessionId: null,
        sessions: [],

        login: async () => {
          try {
            const result = await signInWithPopup(auth, googleProvider);
            const fbUser = result.user;

            const user: User = {
              id: fbUser.uid,
              email: fbUser.email || '',
              name: fbUser.displayName || 'User',
              avatar: fbUser.photoURL || undefined,
            };

            set({ user, isAuthenticated: true });
          } catch (error) {
            console.error("Login failed:", error);
            throw error;
          }
        },

        loginAsGuest: () => {
          const guestUser: User = {
            id: 'guest-' + Math.random().toString(36).substring(2, 9),
            email: 'guest@example.com',
            name: 'Guest User',
          };
          set({ user: guestUser, isAuthenticated: true });
        },

        logout: async () => {
          await signOut(auth);
          set({
            user: null,
            isAuthenticated: false,
            currentSessionId: null,
            sessions: [],
          });
        },

        createSession: () => {
          const newSession: ChatSession = {
            id: generateId(),
            title: 'New Chat',
            messages: [],
            createdAt: new Date(),
            updatedAt: new Date(),
          };

          set(state => ({
            sessions: [newSession, ...state.sessions],
            currentSessionId: newSession.id,
          }));

          return newSession.id;
        },

        setCurrentSession: (sessionId: string) => {
          set({ currentSessionId: sessionId });
        },

        addMessage: (message) => {
          const { currentSessionId, sessions } = get();

          if (!currentSessionId) return;

          const newMessage: Message = {
            ...message,
            id: generateId(),
            timestamp: new Date(),
          };

          set({
            sessions: sessions.map(session =>
              session.id === currentSessionId
                ? {
                  ...session,
                  messages: [...session.messages, newMessage],
                  updatedAt: new Date(),
                  title: session.messages.length === 0 && message.type === 'text'
                    ? message.content.slice(0, 30) + (message.content.length > 30 ? '...' : '')
                    : session.title,
                }
                : session
            ),
          });
        },

        getCurrentSession: () => {
          const { currentSessionId, sessions } = get();
          return sessions.find(s => s.id === currentSessionId) || null;
        },
      };
    },
    {
      name: 'chat-session-storage',
      partialize: (state) => ({
        // We generally don't persist 'user' in local storage if we want to rely on Firebase Auth state
        // But for offline/optimistic UI, we can. Firebase SDK handles token persistence.
        sessions: state.sessions,
        currentSessionId: state.currentSessionId,
      }),
    }
  )
);
