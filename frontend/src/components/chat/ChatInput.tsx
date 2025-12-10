import { useState, useRef, KeyboardEvent } from 'react';
import { Button } from '@/components/ui/button';
import { ImageUploader } from './ImageUploader';
import { VoiceButton } from './VoiceButton';
import { Send, Plus, Image as ImageIcon, FileText } from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

interface ChatInputProps {
  onSend: (message: string, imageUrl?: string, imageFile?: File | null) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleSubmit = () => {
    if (!message.trim() && !selectedImage) return;

    onSend(message.trim(), selectedImage || undefined, selectedFile);
    setMessage('');
    setSelectedImage(null);
    setSelectedFile(null);

    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleVoiceTranscript = (transcript: string) => {
    setMessage((prev) => prev + (prev ? ' ' : '') + transcript);
    textareaRef.current?.focus();
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);

    // Auto-resize
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
  };

  // Wrapper for image selection to close menu
  const handleImageSelect = (fileUrl: string | null, file?: File | null) => {
    setSelectedImage(fileUrl);
    setSelectedFile(file || null);
    setIsMenuOpen(false);
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className={cn(
        "relative flex flex-col gap-2 rounded-[24px] border transition-all duration-300 bg-[#1E1F20] backdrop-blur-xl shadow-lg",
        isFocused ? "border-white/20 shadow-lg ring-1 ring-white/5" : "border-border/10 hover:border-border/30"
      )}>

        {/* Selected Image Preview inside the box */}
        {selectedImage && (
          <div className="px-4 pt-4">
            <ImageUploader
              onImageSelect={handleImageSelect}
              selectedImage={selectedImage}
              compact
            />
          </div>
        )}

        <div className="flex items-center gap-3 p-3">
          <div className="flex-none">
            <Popover open={isMenuOpen} onOpenChange={setIsMenuOpen}>
              <PopoverTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="rounded-full w-9 h-9 bg-surface-200/50 hover:bg-surface-300 text-muted-foreground hover:text-foreground transition-colors"
                  aria-label="Add content"
                >
                  <Plus className="w-5 h-5" />
                </Button>
              </PopoverTrigger>
              <PopoverContent align="start" className="w-48 p-1 glass border-border/50">
                <div className="grid gap-1">
                  {/* We reuse ImageUploader's logic or a custom trigger here. 
                            For this implementation, we will keep it simple and assume ImageUploader 
                            can be triggered or we just show options. 
                            Since ImageUploader is a complex component, we'll render a simplified trigger here 
                            that would theoretically open the file dialog.
                        */}
                  <Button variant="ghost" className="justify-start gap-2 h-9 px-2 relative font-normal text-sm">
                    <ImageIcon className="w-4 h-4 text-blue-400" />
                    Upload Image
                    {/* This is a hacky way to use the existing logic without refactoring the whole ImageUploader component today. 
                                Ideally, ImageUploader should expose a `openFileDialog` method or be headless.
                                For now, we will just render the ImageUploader inside the popover invisible or refactor later.
                                Let's just place the ImageUploader here visible but styled as a button? No.
                                We will place a "Add Image" text. 
                            */}
                    <div className="absolute inset-0 opacity-0 cursor-pointer overflow-hidden">
                      <ImageUploader
                        onImageSelect={handleImageSelect}
                        selectedImage={null}
                        triggerOnly
                      />
                    </div>
                  </Button>
                  <Button variant="ghost" className="justify-start gap-2 h-9 px-2 font-normal text-sm" disabled>
                    <FileText className="w-4 h-4 text-red-400" />
                    Upload File (Soon)
                  </Button>
                </div>
              </PopoverContent>
            </Popover>
          </div>

          <div className="flex-1 min-w-0 flex items-center">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={handleTextareaChange}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder="Ask anything..."
              className="w-full bg-transparent text-foreground placeholder:text-muted-foreground/70 resize-none focus:outline-none text-base py-1 max-h-[200px] overflow-y-auto"
              rows={1}
              disabled={disabled}
              aria-label="Chat message input"
              style={{ minHeight: '24px' }}
            />
          </div>

          <div className="flex-none flex items-center gap-2">
            <VoiceButton onTranscript={handleVoiceTranscript} />

            {/* Only show send button when there is content, similar to Gemini ?? No, user didn't ask that specifically, kept it standard but cleaner */}
            <Button
              onClick={handleSubmit}
              disabled={disabled || (!message.trim() && !selectedImage)}
              size="icon"
              className={cn(
                "rounded-full w-9 h-9 transition-all duration-300 flex items-center justify-center",
                (message.trim() || selectedImage) ? "bg-primary text-primary-foreground hover:bg-primary/90" : "bg-transparent text-muted-foreground hover:bg-surface-200"
              )}
              aria-label="Send message"
            >
              <Send className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </div>

      <p className="mt-3 text-[10px] text-muted-foreground text-center opacity-60">
        AI can make mistakes. Double-check responses.
      </p>
    </div>
  );
}
