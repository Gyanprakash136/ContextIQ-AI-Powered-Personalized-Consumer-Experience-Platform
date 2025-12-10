import { getAuth } from "firebase/auth";

export interface Product {
    name: string;
    price: string;
    marketplace: string;
    link: string;
    image: string;
    reason: string;
}

export interface ChatResponse {
    agent_response: string;
    products: Product[];
    predictive_insight?: string;
    session_id: string;
}

const BACKEND_URL = "http://127.0.0.1:8000";

export async function sendMessageToBackend(
    message: string,
    imageFile?: File, 
    contextLink?: string,
    userId?: string,
    sessionId?: string
): Promise<ChatResponse> {
    let token = "mock_token";
    let finalUserId = userId || "guest_user";

    // Try to get real Firebase user
    try {
        const auth = getAuth();
        const user = auth.currentUser;
        if (user) {
            token = await user.getIdToken();
            finalUserId = user.uid;
        }
    } catch (e) {
        console.warn("Firebase Auth not initialized or no user, using mock_token");
    }

    const formData = new FormData();

    formData.append("message", message);
    if (finalUserId) formData.append("user_id", finalUserId);
    if (sessionId) formData.append("session_id", sessionId);
    if (contextLink) formData.append("context_link", contextLink);
    if (imageFile) formData.append("image", imageFile);

    try {
        const response = await fetch(`${BACKEND_URL}/agent/chat`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`, 
            },
            body: formData,
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API Error: ${response.status} - ${errorText}`);
        }

        const data: ChatResponse = await response.json();
        return data;
    } catch (error) {
        console.error("Error sending message to backend:", error);
        throw error;
    }
}
