import { useState } from 'react';
import { Message } from '@/stores/sessionStore';

import { Lightbox } from './Lightbox';
import ReactMarkdown from 'react-markdown';
import { format } from 'date-fns';
import { Eye, Lightbulb } from 'lucide-react';
import { ProductCard } from './ProductCard';

interface MessageBubbleProps {
  message: Message;
}

// Parse content to extract predictive insight
function parseInsight(content: string): { mainContent: string; insight: string | null } {
  // Look for patterns like "💡 Pro Tip:", "💡 Insight:", "Future Insight:", etc.
  const insightPatterns = [
    /💡\s*(Pro Tip|Tip|Insight|Future Insight)[:\s]+(.+)$/is,
    /(Pro Tip|Future Insight|Insight)[:\s]+(.+)$/is,
  ];

  for (const pattern of insightPatterns) {
    const match = content.match(pattern);
    if (match) {
      const insightText = match[0];
      const mainContent = content.replace(insightText, '').trim();
      return { mainContent, insight: match[2]?.trim() || insightText };
    }
  }

  return { mainContent: content, insight: null };
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const isUser = message.sender === 'user';

  // Parse insight for assistant messages
  const { mainContent, insight } = !isUser && message.type === 'text'
    ? parseInsight(message.content)
    : { mainContent: message.content, insight: null };

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-slide-up`}
    >
      <div
        className={`max-w-[85%] md:max-w-[70%] ${isUser ? 'bubble-user' : 'bubble-assistant'
          } px-4 py-3`}
      >
        {/* Vision Badge for image messages */}
        {isUser && message.type === 'image' && message.imageUrl && (
          <div className="flex items-center gap-1.5 mb-2">
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-primary/20 text-primary text-xs font-medium">
              <Eye className="w-3 h-3" />
              Vision
            </span>
          </div>
        )}

        {message.type === 'image' && message.imageUrl && (
          <>
            <img
              src={message.imageUrl}
              alt="Uploaded content"
              className="rounded-lg max-h-64 object-cover cursor-pointer mb-2 hover:opacity-90 transition-opacity"
              onClick={() => setLightboxOpen(true)}
            />
            <Lightbox
              isOpen={lightboxOpen}
              onClose={() => setLightboxOpen(false)}
              imageUrl={message.imageUrl}
            />
          </>
        )}

        {mainContent && (
          <div className="text-sm text-foreground leading-relaxed">
            <ReactMarkdown
              components={{
                a: ({ node, ...props }) => (
                  <a {...props} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline" />
                ),
                strong: ({ node, ...props }) => (
                  <span {...props} className="font-bold" />
                ),
                ul: ({ node, ...props }) => (
                  <ul {...props} className="list-disc pl-4 my-2 space-y-1" />
                ),
                ol: ({ node, ...props }) => (
                  <ol {...props} className="list-decimal pl-4 my-2 space-y-1" />
                ),
                p: ({ node, ...props }) => (
                  <p {...props} className="mb-2 last:mb-0" />
                )
              }}
            >
              {mainContent}
            </ReactMarkdown>
          </div>
        )}

        {/* Predictive Insight Highlight */}
        {insight && (
          <div className="mt-3 p-3 rounded-lg bg-primary/10 border border-primary/20">
            <div className="flex items-start gap-2">
              <Lightbulb className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
              <p className="text-sm text-primary leading-relaxed">
                {insight}
              </p>
            </div>
          </div>
        )}

        {/* Product Cards Carousel */}
        {message.products && message.products.length > 0 && (
          <div className="mt-4 -mx-2 px-2 overflow-x-auto pb-4 custom-scrollbar flex gap-4 snap-x">
            {message.products.map((product, index) => (
              <div key={index} className="snap-center">
                <ProductCard product={product} />
              </div>
            ))}
          </div>
        )}

        <div className={`flex items-center gap-2 mt-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
          <span className="text-xs text-muted-foreground">
            {format(new Date(message.timestamp), 'h:mm a')}
          </span>
        </div>
      </div>
    </div>
  );
}
