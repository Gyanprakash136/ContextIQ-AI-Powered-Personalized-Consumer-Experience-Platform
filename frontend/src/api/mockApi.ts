// Mock API responses for chat
// TODO: Replace with actual backend API integration (e.g., OpenAI, custom backend)

const MOCK_RESPONSES = [
  "I'd be happy to help you with that! Based on what you've shared, here are some thoughts...",
  "That's a great question. Let me break this down for you...",
  "I understand what you're looking for. Here's what I can tell you...",
  "Thanks for sharing that context. Here's my analysis...",
  "Interesting! Let me provide some insights on this topic...",
];

const IMAGE_RESPONSES = [
  "I can see the image you've uploaded. It appears to show an interesting scene. What would you like to know about it?",
  "Thanks for sharing this image! I can help analyze or discuss what you see here. What specific aspects are you curious about?",
  "I've received your image. Based on what I can see, this is quite interesting. Would you like me to describe it or help you with something specific?",
];

export async function mockChatResponse(
  message: string,
  imageUrl?: string
): Promise<string> {
  // Simulate network delay (700-1200ms)
  const delay = 700 + Math.random() * 500;
  await new Promise((resolve) => setTimeout(resolve, delay));

  if (imageUrl) {
    return IMAGE_RESPONSES[Math.floor(Math.random() * IMAGE_RESPONSES.length)];
  }

  // Simple keyword-based responses for demo
  const lowerMessage = message.toLowerCase();

  if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
    return "Hello! I'm your AI assistant. How can I help you today?";
  }

  if (lowerMessage.includes('help')) {
    return "I'm here to assist you! You can:\n\n• Ask me any questions\n• Upload images for analysis\n• Use voice input for hands-free interaction\n\nWhat would you like to explore?";
  }

  if (lowerMessage.includes('thank')) {
    return "You're welcome! Feel free to ask if you have more questions.";
  }

  return MOCK_RESPONSES[Math.floor(Math.random() * MOCK_RESPONSES.length)];
}

// Mock auth endpoints
export async function mockLogin(
  email: string,
  _password: string
): Promise<{ token: string; user: { id: string; email: string; name: string } }> {
  await new Promise((resolve) => setTimeout(resolve, 800));

  return {
    token: 'mock_jwt_token_' + Math.random().toString(36).substring(7),
    user: {
      id: Math.random().toString(36).substring(7),
      email,
      name: email.split('@')[0],
    },
  };
}

export async function mockSignup(
  name: string,
  email: string,
  _password: string
): Promise<{ token: string; user: { id: string; email: string; name: string } }> {
  await new Promise((resolve) => setTimeout(resolve, 800));

  return {
    token: 'mock_jwt_token_' + Math.random().toString(36).substring(7),
    user: {
      id: Math.random().toString(36).substring(7),
      email,
      name,
    },
  };
}
