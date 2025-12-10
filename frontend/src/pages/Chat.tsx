import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChatLayout } from '@/components/chat/ChatLayout';
import { useSessionStore } from '@/stores/sessionStore';

const Chat = () => {
  const navigate = useNavigate();
  const { isAuthenticated, createSession } = useSessionStore();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/auth');
    } else {
      // Force new session on entry
      createSession();
    }
  }, [isAuthenticated, navigate, createSession]);

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
