import { auth } from "@/lib/firebase";

const API_BASE_URL = "http://localhost:8000";

/**
 * Validates if the backend is online.
 */
export async function checkBackendHealth(): Promise<boolean> {
    try {
        const res = await fetch(`${API_BASE_URL}/health`);
        return res.ok;
    } catch (e) {
        return false;
    }
}

/**
 * Main chat function to send message and/or image to the backend agent.
 */
export interface Product {
    name: string;
    price: string;
    marketplace: string;
    link: string;
    image: string;
    reason?: string;
}

export interface ChatResponse {
    agent_response: string;
    session_id: string;
    products: Product[];
}

/**
 * Main chat function to send message and/or image to the backend agent.
 */
export async function sendChatToBackend(
    message: string,
    imageFile?: File | null
): Promise<ChatResponse> {
    // 1. Get Firebase Token
    const currentUser = auth.currentUser;
    if (!currentUser) {
        throw new Error("User not authenticated. Please log in.");
    }

    const token = await currentUser.getIdToken();

    // 2. Prepare Form Data
    const formData = new FormData();
    // Backend expects 'message' field even if empty string
    formData.append("message", message || "");

    // If an image is provided
    if (imageFile) {
        formData.append("image", imageFile);
    }

    // 3. Send Request
    try {
        const response = await fetch(`${API_BASE_URL}/agent/chat`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                // Note: Do NOT set Content-Type header manually for FormData, 
                // the browser automatically sets it with the boundary.
            },
            body: formData,
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Backend Error (${response.status}): ${errorText}`);
        }

        const data = await response.json();
        // Expected format: { "agent_response": "...", "session_id": "...", "products": [...] }
        return data as ChatResponse;

    } catch (error) {
        console.error("Chat API Error:", error);
        throw error;
    }
}

// Deprecated Mock function replacement - redirects to real backend
export async function mockChatResponse(message: string, imageUrl?: string): Promise<string> {
    // We need to convert the imageUrl string back to a File object if possible, 
    // but the backend expects a file.
    // For now, if we only have a string URL (like from a previous session or partial implementation),
    // we might skip the image or need to fetch it.
    // HOWEVER, the UI components usually pass the plain string for preview.
    // Ideally, we should update ChatLayout to pass the File object.

    // For this immediate integration, we'll try to fetch the blob if it's a blob url, 
    // or just send text if no file object is handy.

    // NOTE: This shim is to make existing components valid without changing every single import immediately.
    // But we should update ChatLayout.tsx to use sendChatToBackend directly.
    const res = await sendChatToBackend(message, null);
    return res.agent_response;
}
