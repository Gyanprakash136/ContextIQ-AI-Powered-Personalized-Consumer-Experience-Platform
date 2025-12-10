import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '@/components/Header';
import { AuthForm } from '@/components/AuthForm';
import { useSessionStore } from '@/stores/sessionStore';

const Auth = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useSessionStore();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/chat');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1 flex items-center justify-center py-20">
        <AuthForm />
      </main>
    </div>
  );
};

export default Auth;
