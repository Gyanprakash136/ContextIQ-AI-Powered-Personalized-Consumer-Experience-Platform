import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Upload, X } from 'lucide-react';
import { toast } from 'sonner';

interface ImageUploaderProps {
  onImageSelect: (imageUrl: string | null) => void;
  selectedImage: string | null;
  compact?: boolean;
  triggerOnly?: boolean;
}

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

export function ImageUploader({ onImageSelect, selectedImage, compact, triggerOnly }: ImageUploaderProps) {

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];

    if (!file) return;

    if (file.size > MAX_FILE_SIZE) {
      toast.error('Image must be less than 5MB');
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => {
      onImageSelect(reader.result as string);
    };
    reader.readAsDataURL(file);
  }, [onImageSelect]);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp']
    },
    maxFiles: 1,
  });

  const handleClear = () => {
    onImageSelect(null);
  };

  if (selectedImage) {
    return (
      <div className="relative inline-block mt-2">
        <img
          src={selectedImage}
          alt="Selected"
          className="h-16 w-16 rounded-xl object-cover border border-border/50"
        />
        <button
          onClick={handleClear}
          className="absolute -top-2 -right-2 w-5 h-5 bg-background border border-border text-foreground rounded-full flex items-center justify-center hover:bg-muted"
          aria-label="Remove image"
        >
          <X className="w-3 h-3" />
        </button>
      </div>
    );
  }

  if (triggerOnly) {
    return (
      <div {...getRootProps()} className="w-full h-full cursor-pointer">
        <input {...getInputProps()} />
      </div>
    );
  }

  // Fallback for default usage if any (though we primarily use triggerOnly or selectedImage view now)
  return (
    <div {...getRootProps()}>
      <input {...getInputProps()} />
      <Button variant="outline" size="icon">
        <Upload className="w-4 h-4" />
      </Button>
    </div>
  );
}
