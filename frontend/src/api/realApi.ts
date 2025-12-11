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

export async function fetchChatHistory(token: string): Promise<any[]> {
    try {
        const response = await fetch(`${BACKEND_URL}/agent/history`, {
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });
        if (!response.ok) throw new Error("Failed to fetch history");
        return await response.json();
    } catch (error) {
        console.error("Error fetching history:", error);
        return [];
    }
}

export async function fetchSessionDetails(sessionId: string, token: string): Promise<any> {
    try {
        const response = await fetch(`${BACKEND_URL}/agent/session/${sessionId}`, {
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });
        if (!response.ok) throw new Error("Failed to fetch session details");
        return await response.json();
    } catch (error) {
        console.error("Error fetching session details:", error);
        return null;
    }
}

export async function generateChatTitle(sessionId: string, token: string): Promise<string> {
    try {
        const response = await fetch(`${BACKEND_URL}/agent/title`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ session_id: sessionId }),
        });
        if (!response.ok) return "New Chat";
        const data = await response.json();
        return data.title || "New Chat";
    } catch (error) {
        console.error("Error generating title:", error);
        return "New Chat";
    }
}


export async function claimSession(sessionId: string, token: string): Promise<boolean> {
    try {
        const response = await fetch(`${BACKEND_URL}/agent/session/${sessionId}/claim`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });
        return response.ok;
    } catch (error) {
        console.error("Error claiming session:", error);
        return false;
    }
}
