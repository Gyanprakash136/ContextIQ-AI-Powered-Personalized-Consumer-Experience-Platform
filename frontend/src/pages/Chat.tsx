import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ChatLayout } from '@/components/chat/ChatLayout';
import { useSessionStore } from '@/stores/sessionStore';

const Chat = () => {
  const navigate = useNavigate();
  const { sessionId } = useParams();
  const { isAuthenticated, createSession, currentSessionId } = useSessionStore.getState();
  // Should use hook for reactivity if we depend on store state, but actions are fine.
  const createSessionAction = useSessionStore(s => s.createSession);
  const setCurrentSession = useSessionStore(s => s.setCurrentSession);

  // Actually useSessionStore hook is better for reactivity
  const store = useSessionStore();

  useEffect(() => {
    if (!store.isAuthenticated) {
      navigate('/auth');
      return;
    }

    // Handle Deep Linking / Refresh
    if (sessionId) {
      // If URL has ID, set it in store
      setCurrentSession(sessionId);
    } else {
      // No ID in URL == New Chat
      // But only creating if we really don't have one or user explicitly navigated to /chat
      // If we just landed on /chat, we want a fresh empty session.
      // If we already have a session in store but no URL, what to do?
      // Standard behavior: /chat -> New Chat.

      // However, the issue described is "Refresh redirecting to new chat".
      // If user was on /chat and refreshed, they lose state because URL didn't have ID.
      // So we must update URL when session changes.

      // For now, on mount of /chat, create new session.
      if (!store.currentSessionId) {
        createSessionAction();
      }
    }
  }, [store.isAuthenticated, sessionId, navigate]);

  // Sync URL when session changes (e.g. created new one)
  useEffect(() => {
    if (store.currentSessionId && store.currentSessionId !== sessionId) {
      // Update URL without reloading
      navigate(`/chat/${store.currentSessionId}`, { replace: true });
    }
  }, [store.currentSessionId, navigate, sessionId]);

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden relative">
      <div className="flex-1 relative h-full overflow-hidden">
        <ChatLayout />
      </div>
    </div>
  );
};

export default Chat;
