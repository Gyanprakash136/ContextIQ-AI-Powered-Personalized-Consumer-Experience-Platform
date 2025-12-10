import { useEffect, useRef, useState, useMemo } from 'react';
import { useSessionStore } from '@/stores/sessionStore';
import { ChatSidebar } from './ChatSidebar';
import { ChatInput } from './ChatInput';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';
<<<<<<< HEAD
import { sendMessageToBackend } from '@/api/realApi';
=======
import { sendChatToBackend } from '@/api/api';
<<<<<<< HEAD
>>>>>>> b471a44 (connected backend with frontend)
import { MessageSquare, Sparkles, LogOut, Home, User } from 'lucide-react';
=======
import { MessageSquare, Sparkles, LogOut, Home, User, PanelLeftOpen } from 'lucide-react';
>>>>>>> 1a8c430 (changes in frontend)
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';
import softwareAgentLogo from '@/assets/software-agent.png';

// Detect if message contains a URL
function containsUrl(text: string): boolean {
  const urlPattern = /https?:\/\/[^\s]+/i;
  return urlPattern.test(text);
}

export function ChatLayout() {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isAnalyzingLink, setIsAnalyzingLink] = useState(false);
  // Default to true on desktop if we want persistent sidebar, but user asked for toggle.
  // We'll manage state here.
  // Default to false (closed) as per user request
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const navigate = useNavigate();

  const {
    currentSessionId,
    getCurrentSession,
    createSession,
    addMessage,
    user,
    logout
  } = useSessionStore();

  const currentSession = getCurrentSession();

  // Time-based greeting (Gemini-style)
  const { greetingTitle } = useMemo(() => {
    const hour = new Date().getHours();
    let title = 'Hello there';
    if (hour >= 5 && hour < 12) title = 'Good morning';
    else if (hour >= 12 && hour < 17) title = 'Good afternoon';
    else title = 'Good evening';

    return {
      greetingTitle: title,
    };
  }, []);

  // Updated suggestions based on user request
  const quickSuggestions = [
    "Help me find the best product for my needs",
    "Recommend products based on my preferences",
    "What should I buy for this occasion?",
    "Show me trending products right now",
    "Find alternatives similar to this product",
    "Suggest products under my budget",
  ];

  useEffect(() => {
    if (!currentSessionId) {
      createSession();
    }
  }, [currentSessionId, createSession]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentSession?.messages]);


  const handleSend = async (content: string, imageUrl?: string, imageFile?: File | null) => {
    if (!content && !imageUrl && !imageFile) return;

    // Add user message
    addMessage({
      sender: 'user',
      type: (imageUrl || imageFile) ? 'image' : 'text',
      content,
      imageUrl: imageUrl || (imageFile ? URL.createObjectURL(imageFile) : undefined),
    });

    // Check if message contains a link
    const hasLink = containsUrl(content);
    setIsLoading(true);
    setIsAnalyzingLink(hasLink);

    // Auto-open sidebar on first message if closed
    if (isEmpty && !isSidebarOpen) {
      setIsSidebarOpen(true);
    }

    try {
<<<<<<< HEAD
      // Real API Call
      // Convert base64 imageUrl to File if present (simplified for now, assumes base64)
      let imageFile: File | undefined;
      if (imageUrl) {
        const res = await fetch(imageUrl);
        const blob = await res.blob();
        imageFile = new File([blob], "upload.jpg", { type: blob.type });
      }

      const response = await sendMessageToBackend(content, imageFile, undefined, user?.id, currentSessionId || undefined);
=======
      // Real Backend API call
      // We pass the raw File object if we have it, otherwise null
      const { agent_response, products } = await sendChatToBackend(content, imageFile);

      addMessage({
        sender: 'assistant',
        type: 'text',
        content: agent_response,
        products: products
      });
    } catch (error) {
<<<<<<< HEAD
      console.error("Chat Error", error);
      addMessage({
        sender: 'assistant',
        type: 'text',
        content: 'Sorry, I encountered an error connecting to the server. Please ensure the backend is running.',
=======
      console.error(error);
      addMessage({
        sender: 'assistant',
        type: 'text',
        content: `Error: ${error instanceof Error ? error.message : 'Something went wrong connecting to ContextIQ.'}`,
>>>>>>> b471a44 (connected backend with frontend)
      });
    } finally {
      setIsLoading(false);
      setIsAnalyzingLink(false);
    }
  };

  const handleSuggestionClick = (text: string) => {
    void handleSend(text);
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const isEmpty = !currentSession || currentSession.messages.length === 0;

  return (
    <div className={cn(
      "flex h-full relative overflow-hidden text-foreground transition-colors duration-500",
      isEmpty ? "bg-black" : "bg-[#131314]"
    )}>
      {/* Soft gradient background like Gemini - Reduced opacity for dark theme */}
      <div className="pointer-events-none absolute inset-0 opacity-20">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-gradient-to-br from-primary/10 via-blue-500/5 to-transparent rounded-full blur-[100px]" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-gradient-to-tr from-purple-500/5 via-primary/5 to-transparent rounded-full blur-[100px]" />
      </div>

      <ChatSidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
      />

      <div className="flex-1 flex flex-col relative z-10 h-full overflow-hidden">

        {/* Custom Header */}
        <header className="h-16 flex items-center justify-between px-6 bg-transparent sticky top-0 z-20">
          <div className="flex items-center gap-4">
            {!isSidebarOpen && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsSidebarOpen(true)}
                className="text-muted-foreground hover:text-foreground"
              >
                <PanelLeftOpen className="w-5 h-5" />
              </Button>
            )}
            <div
              className="flex items-center gap-3 cursor-pointer group hover:opacity-80 transition-opacity"
              onClick={() => navigate('/')}
            >
              <img src={softwareAgentLogo} alt="ContextIQ" className="w-8 h-8 object-contain" />
              <span className="text-lg font-medium text-[#e3e3e3] tracking-tight hidden md:block">ContextIQ</span>
            </div>
          </div>

          {/* Center Title - visible only when chat is active */}
          <div className="hidden md:flex flex-1 justify-center relative">
            {!isEmpty && (
              <span className="text-sm font-medium text-white/80 bg-white/5 border border-white/5 rounded-full px-4 py-1.5 animate-fade-in truncate max-w-[300px]">
                {currentSession?.title || "New Chat"}
              </span>
            )}
          </div>

          <div className="flex items-center gap-4">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <div className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity">
                  <Button variant="ghost" size="icon" className="rounded-full w-9 h-9 border border-white/10 hover:bg-white/10 overflow-hidden">
                    {user?.avatar ? (
                      <img src={user.avatar} alt="User" className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center text-xs font-bold text-white">
                        {user?.name?.[0]?.toUpperCase() || "U"}
                      </div>
                    )}
                  </Button>
                </div>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56 glass border-border/50 bg-[#1e1f20] text-foreground p-2">
                <DropdownMenuLabel className="font-normal px-2 py-1.5">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none text-white">{user?.name || "User"}</p>
                    <p className="text-xs leading-none text-muted-foreground">{user?.email || "user@example.com"}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator className="bg-white/10 my-1" />
                <DropdownMenuItem onClick={() => navigate('/')} className="cursor-pointer focus:bg-white/10 focus:text-white rounded-md my-1 px-2 py-2 transition-colors duration-200">
                  <Home className="mr-2 h-4 w-4" />
                  <span>Home</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleLogout} className="cursor-pointer text-red-400 focus:bg-red-500/10 focus:text-red-400 rounded-md my-1 px-2 py-2 transition-colors duration-200">
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>


        {/* Messages area */}
        <div className="flex-1 overflow-y-auto custom-scrollbar">
          <div className="container max-w-4xl mx-auto py-6 px-4 min-h-full flex flex-col">
            {isEmpty ? (
              // GEMINI-STYLE EMPTY STATE WITH IMAGE
              <div className="flex-1 flex flex-col items-center justify-center text-center animate-fade-in my-auto">
                <div className="mb-6 relative">
                  <img src={softwareAgentLogo} alt="ContextIQ Agent" className="w-20 h-20 object-contain drop-shadow-2xl opacity-90" />
                </div>

                <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70 mb-3 tracking-tight">
                  {greetingTitle}
                  {user?.name ? `, ${user.name}` : ''}
                </h1>
                <p className="text-lg text-muted-foreground max-w-md mb-12">
                  How can I help you today?
                </p>

                {/* Quick suggestions (chips) */}
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 max-w-4xl w-full px-4">
                  {quickSuggestions.map((s, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(s)}
                      className="group p-4 text-left rounded-xl bg-surface-50/50 hover:bg-surface-100/80 border border-border/50 hover:border-primary/20 transition-all duration-200 shadow-sm hover:shadow-md backdrop-blur-sm"
                    >
                      <span className="text-sm font-medium text-muted-foreground group-hover:text-foreground transition-colors line-clamp-2">
                        {s}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-6 pb-4">
                {currentSession?.messages.map((message) => (
                  <MessageBubble key={message.id} message={message} />
                ))}
                {isLoading && <TypingIndicator isAnalyzingLink={isAnalyzingLink} />}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Input area */}
        <div className="p-4 bg-gradient-to-t from-background via-background to-transparent pt-10">
          <ChatInput onSend={handleSend} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}
