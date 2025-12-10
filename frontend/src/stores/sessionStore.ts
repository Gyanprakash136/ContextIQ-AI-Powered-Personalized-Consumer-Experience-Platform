import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface User {
  id: string;
  email: string;
  name: string;
  isGuest: boolean;
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
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  loginAsGuest: () => void;
  logout: () => void;
  
  // Chat actions
  createSession: () => string;
  setCurrentSession: (sessionId: string) => void;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  getCurrentSession: () => ChatSession | null;
}

const generateId = () => Math.random().toString(36).substring(2, 15);

export const useSessionStore = create<SessionState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      currentSessionId: null,
      sessions: [],

      login: async (email: string, _password: string) => {
        // Mock API call
        await new Promise(resolve => setTimeout(resolve, 800));
        
        const user: User = {
          id: generateId(),
          email,
          name: email.split('@')[0],
          isGuest: false,
        };
        
        set({ user, isAuthenticated: true });
      },

      signup: async (name: string, email: string, _password: string) => {
        // Mock API call
        await new Promise(resolve => setTimeout(resolve, 800));
        
        const user: User = {
          id: generateId(),
          email,
          name,
          isGuest: false,
        };
        
        set({ user, isAuthenticated: true });
      },

      loginAsGuest: () => {
        const user: User = {
          id: generateId(),
          email: 'guest@demo.local',
          name: 'Guest',
          isGuest: true,
        };
        
        set({ user, isAuthenticated: true });
      },

      logout: () => {
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
    }),
    {
      name: 'chat-session-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        sessions: state.sessions,
        currentSessionId: state.currentSessionId,
      }),
    }
  )
);
