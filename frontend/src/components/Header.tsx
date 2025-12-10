import { Link, useNavigate } from "react-router-dom";
import { useSessionStore } from "@/stores/sessionStore";
import SoftwareAgentLogo from "@/assets/software-agent.png";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { LogOut, User as UserIcon } from "lucide-react";

export const Header = () => {
  const { user, isAuthenticated, logout } = useSessionStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <header className="fixed top-0 w-full z-50 bg-ink-black/80 backdrop-blur-md border-b border-white/5 text-white px-6 py-4 md:px-12 flex justify-between items-center transition-all duration-300">
      <Link to="/" className="flex items-center gap-2 group transition-opacity hover:opacity-80">
        <img src={SoftwareAgentLogo} alt="ContextIQ Logo" className="h-10 w-10 object-contain" />
        <h2 className="text-lg font-bold tracking-tight font-display">
          ContextIQ<span className="text-primary">.</span>
        </h2>
      </Link>
      <div className="flex items-center gap-8 text-sm font-medium font-sans">
        {!isAuthenticated ? (
          <Link
            to="/auth"
            className="hidden md:block opacity-70 hover:opacity-100 transition-opacity hover-underline-animation"
          >
            Sign in
          </Link>
        ) : (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <div className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity">
                <Avatar className="h-8 w-8 ring-2 ring-primary/20">
                  <AvatarImage src={user?.avatar} />
                  <AvatarFallback className="bg-primary/10 text-primary">
                    {user?.name?.charAt(0) || "U"}
                  </AvatarFallback>
                </Avatar>
              </div>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 bg-surface-800 border-white/10 text-white">
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-white/10" />
              <DropdownMenuItem className="cursor-pointer focus:bg-white/5 focus:text-white group">
                <UserIcon className="mr-2 h-4 w-4 text-white/50 group-hover:text-primary transition-colors" />
                <span>Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleLogout} className="cursor-pointer focus:bg-destructive/10 focus:text-destructive text-destructive group">
                <LogOut className="mr-2 h-4 w-4 group-hover:text-destructive transition-colors" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
        <Link
          to="/chat"
          className="group flex items-center gap-2 hover:text-primary transition-colors"
        >
          <span className="hover-underline-animation">Open agent</span>
          <span className="material-symbols-outlined text-[16px] group-hover:translate-x-1 transition-transform">
            arrow_forward
          </span>
        </Link>
      </div>
    </header>
  );
};
