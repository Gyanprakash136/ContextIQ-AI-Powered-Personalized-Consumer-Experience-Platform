import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useSessionStore } from '@/stores/sessionStore';
import { MessageSquare, LogOut } from 'lucide-react';

export function Header() {
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useSessionStore();

  const handleTryNow = () => {
    if (isAuthenticated) {
      navigate('/chat');
    } else {
      navigate('/auth');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass">
      <div className="container flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
            <MessageSquare className="w-4 h-4 text-primary" />
          </div>
          <span className="font-semibold text-foreground">Nexus</span>
        </Link>

        <nav className="hidden md:flex items-center gap-8">
          <Link 
            to="/" 
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Home
          </Link>
          <Link 
            to="/chat" 
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Chat
          </Link>
          {!isAuthenticated && (
            <Link 
              to="/auth" 
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Sign In
            </Link>
          )}
        </nav>

        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <>
              <span className="text-sm text-muted-foreground hidden sm:block">
                {user?.name}
              </span>
              <Button variant="ghost" size="icon-sm" onClick={handleLogout}>
                <LogOut className="w-4 h-4" />
              </Button>
            </>
          ) : (
            <Button onClick={handleTryNow} size="sm">
              Try Now
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}
