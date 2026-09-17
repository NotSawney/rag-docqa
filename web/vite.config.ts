import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server on 5173 to match the compose `web` origin (keeps CORS to one entry).
export default defineConfig({
  plugins: [react()],
  server: { port: 5173 },
});
