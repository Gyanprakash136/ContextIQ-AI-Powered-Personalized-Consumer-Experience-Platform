import { useEffect } from 'react';
import { X } from 'lucide-react';

interface LightboxProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
}

export function Lightbox({ isOpen, onClose, imageUrl }: LightboxProps) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-background/90 backdrop-blur-sm animate-fade-in"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Image preview"
    >
      <button
        onClick={onClose}
        className="absolute top-4 right-4 p-2 rounded-lg bg-surface-800 hover:bg-surface-700 transition-colors"
        aria-label="Close lightbox"
      >
        <X className="w-5 h-5" />
      </button>
      
      <img
        src={imageUrl}
        alt="Full size preview"
        className="max-w-[90vw] max-h-[90vh] object-contain rounded-lg animate-scale-in"
        onClick={(e) => e.stopPropagation()}
      />
    </div>
  );
}
