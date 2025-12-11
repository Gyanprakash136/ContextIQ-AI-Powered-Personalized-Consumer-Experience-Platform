import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { auth, googleProvider } from '@/lib/firebase';
import { signInWithPopup, signOut, User as FirebaseUser, getAuth } from 'firebase/auth';
import { Product } from '@/api/api';
import { fetchChatHistory, generateChatTitle, fetchSessionDetails } from '@/api/realApi';

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}

export interface Message {
  id: string;
  sender: 'user' | 'assistant';
  type: 'text' | 'image';
  content: string;
  imageUrl?: string;
  products?: Product[];
  timestamp: Date;
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
  syncWithBackend: () => Promise<void>;
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

            // Claim local sessions first
            const { sessions: localSessions } = get();
            if (localSessions.length > 0) {
              const token = await fbUser.getIdToken();
              const { claimSession } = await import('@/api/realApi');

              await Promise.all(localSessions.map(session =>
                claimSession(session.id, token)
              ));
            }

            set({ user, isAuthenticated: true });

            // Sync history after login
            await get().syncWithBackend();
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
          const { sessions } = get();

          // If the most recent session is empty, reuse it to prevent piling up empty chats
          if (sessions && sessions.length > 0) {
            const recentSession = sessions[0];
            if (recentSession && recentSession.messages.length === 0) {
              set({ currentSessionId: recentSession.id });
              return recentSession.id;
            }
          }

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

          // Title generation logic is handled in ChatLayout/UI now
        },

        syncWithBackend: async () => {
          const auth = getAuth();
          const user = auth.currentUser;
          if (!user) return;

          try {
            const token = await user.getIdToken();
            const history = await fetchChatHistory(token);

            const backendSessions: ChatSession[] = history.map((h: any) => ({
              id: h.session_id,
              title: h.title || "New Chat",
              messages: [],
              createdAt: new Date(h.created_at || Date.now()),
              updatedAt: new Date(h.updated_at || Date.now()),
            }));

            // Smart Merge: Union by ID
            const { sessions: localSessions } = get();

            // Map of ID -> Session
            const sessionMap = new Map<string, ChatSession>();

            // Add local sessions first
            localSessions.forEach(s => sessionMap.set(s.id, s));

            // Add/Update with Backend sessions
            backendSessions.forEach(bs => {
              const existing = sessionMap.get(bs.id);
              if (existing) {
                // Update metadata but keep messages if we have them locally and backend doesn't (since we fetch summary only)
                // Also preserve title if backend is "New Chat" (fix for title reversion)
                const title = (bs.title === "New Chat" && existing.title !== "New Chat") ? existing.title : bs.title;

                sessionMap.set(bs.id, {
                  ...existing,
                  title,
                  updatedAt: bs.updatedAt, // Trust backend timestamp
                  // Keep existing messages as backend list doesn't have them
                });
              } else {
                sessionMap.set(bs.id, bs);
              }
            });

            const mergedSessions = Array.from(sessionMap.values())
              .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());

            set({ sessions: mergedSessions });

            // If current session is active, maybe fetch full details? 
            // Only if it has no messages?
            const { currentSessionId } = get();
            if (currentSessionId) {
              const current = sessionMap.get(currentSessionId);
              // If it came from backend and has empty messages, load them
              // CRITIAL FIX: Only fetch if we know it came from backend (exists in newSessions)
              const isBackendSession = backendSessions.some(s => s.id === currentSessionId);

              if (current && current.messages.length === 0 && isBackendSession) {
                const fullDetails = await fetchSessionDetails(currentSessionId, token);
                if (fullDetails && fullDetails.messages) {
                  const mappedMessages: Message[] = fullDetails.messages.map((m: any, idx: number) => ({
                    id: `msg-${idx}`,
                    sender: m.role,
                    type: 'text',
                    content: m.content,
                    timestamp: new Date(),
                  }));

                  set(state => ({
                    sessions: state.sessions.map(s =>
                      s.id === currentSessionId ? { ...s, messages: mappedMessages } : s
                    )
                  }));
                }
              }
            }

          } catch (e) {
            console.error("Failed to sync with backend", e);
          }
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
        // Persist user and auth state to survive refreshes
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        sessions: state.sessions,
        currentSessionId: state.currentSessionId,
      }),
    }
  )
);
