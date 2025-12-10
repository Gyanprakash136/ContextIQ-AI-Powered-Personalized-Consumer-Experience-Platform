import { useSessionStore, ChatSession } from '@/stores/sessionStore';
import { Button } from '@/components/ui/button';
import { Plus, MessageSquare, Menu, X, Search, PanelLeftClose, PanelLeftOpen, Home } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import { useEffect, useState } from 'react';

interface ChatSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onToggle: () => void;
}

import { useNavigate } from 'react-router-dom';

export function ChatSidebar({ isOpen, onClose, onToggle }: ChatSidebarProps) {
  const { sessions, currentSessionId, createSession, setCurrentSession } = useSessionStore();
  const [isSearchActive, setIsSearchActive] = useState(false);
  const navigate = useNavigate();

  const handleNewChat = () => {
    createSession();
    if (window.innerWidth < 768) {
      onClose();
    }
  };

  const handleSelectSession = (id: string) => {
    setCurrentSession(id);
    if (window.innerWidth < 768) {
      onClose();
    }
  };

  const handleBackToHome = () => {
    navigate('/');
  };

  // Close sidebar on route change or when screen resizes to desktop if needed
  useEffect(() => {
    const handleResize = () => {
      // Logic for auto-adjusting if needed
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-40 backdrop-blur-sm"
          onClick={onClose}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={cn(
          "fixed md:relative inset-y-0 left-0 z-50 w-72 bg-[#1E1F20] backdrop-blur-xl border-r border-border/5 transform transition-all duration-300 ease-in-out md:transform-none flex flex-col h-full",
          isOpen ? "translate-x-0 w-72 opacity-100" : "-translate-x-full md:translate-x-0 md:w-0 md:opacity-0 md:overflow-hidden"
        )}
      >
        {/* Sidebar Header with Toggle and Search */}
        <div className="p-4 flex items-center justify-between gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggle}
            className="text-gray-400 hover:text-white hover:bg-white/5 transition-all duration-200"
            title="Collapse sidebar"
          >
            <PanelLeftClose className="w-5 h-5" />
          </Button>

          <div className="flex-1 flex justify-end items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="text-gray-400 hover:text-white hover:bg-white/5 transition-all duration-200"
              onClick={() => setIsSearchActive(!isSearchActive)}
              title="Search chats"
            >
              <Search className="w-5 h-5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleNewChat}
              className="text-gray-400 hover:text-white hover:bg-white/5 transition-all duration-200"
              title="New Chat"
            >
              <Plus className="w-5 h-5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleBackToHome}
              className="text-gray-400 hover:text-white hover:bg-white/5 transition-all duration-200"
              title="Back to Home"
            >
              <Home className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* Separator */}
        <div className="px-4">
          <div className="h-px bg-white/5 w-full" />
        </div>

        {/* Search Input Area */}
        {isSearchActive && (
          <div className="px-4 py-3 animate-fade-in">
            <input
              type="text"
              placeholder="Search..."
              className="w-full bg-[#131314] border border-border/20 rounded-full px-4 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-white/20 transition-all duration-300"
              autoFocus
            />
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-3 custom-scrollbar">
          <div className="mb-2 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider mt-2">
            Recent
          </div>

          {sessions.filter(s => s.messages.length > 0).length === 0 ? (
            <p className="text-xs text-gray-500 text-center py-8 opacity-70">
              No chat history
            </p>
          ) : (
            <div className="space-y-1 px-2">
              {sessions
                .filter(session => session.messages.length > 0)
                .map((session: ChatSession) => (
                  <div
                    key={session.id}
                    className="group relative"
                  >
                    <button
                      onClick={() => handleSelectSession(session.id)}
                      className={cn(
                        "w-full text-left py-2 px-4 rounded-full transition-all duration-200 flex items-center gap-3 text-sm",
                        session.id === currentSessionId
                          ? "bg-[#1E3760] text-blue-100 font-medium shadow-md"
                          : "text-gray-300 hover:text-white hover:bg-white/5"
                      )}
                    >
                      <MessageSquare className={cn(
                        "w-4 h-4 flex-shrink-0",
                        session.id === currentSessionId ? "text-blue-200" : "text-gray-400 group-hover:text-white"
                      )} />
                      <div className="flex-1 min-w-0">
                        <p className="truncate">{session.title || "Untitled Chat"}</p>
                      </div>
                    </button>
                  </div>
                ))}
            </div>
          )}
        </div>

        {/* Footer area if needed */}
        <div className="p-4 border-t border-border/50 bg-gradient-to-t from-surface-50/80 to-transparent">
          <div className="text-[10px] text-muted-foreground text-center">
            ContextIQ Platform © 2025
          </div>
        </div>
      </aside>
    </>
  );
}
