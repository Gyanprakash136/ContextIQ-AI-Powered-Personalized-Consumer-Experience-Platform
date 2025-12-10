
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyBZP78hEWKE7lglLiZ1nLcZ6jiXaQTzl4o",
    authDomain: "contextiq-31a9c.firebaseapp.com",
    projectId: "contextiq-31a9c",
    storageBucket: "contextiq-31a9c.firebasestorage.app",
    messagingSenderId: "800365989088",
    appId: "1:800365989088:web:5206f40cb6bb65809c1485",
    measurementId: "G-YSJV1809M0"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
