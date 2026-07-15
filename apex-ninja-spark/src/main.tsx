import { createRoot } from "react-dom/client";
import { GoogleOAuthProvider } from "@react-oauth/google"; // <--- Import this
import App from "./App.tsx";
import "./index.css";


const GOOGLE_CLIENT_ID = "291305177140-n8hou6k7ciholo51g01qnin3t6pud84m.apps.googleusercontent.com";

createRoot(document.getElementById("root")!).render(
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}> {/* <--- Wrap App */}
        <App />
    </GoogleOAuthProvider>
);