"use client";

import React, { useState, useEffect } from 'react';
import ChatInterface from '../components/ChatInterface';
import { Lock } from 'lucide-react';

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState("");
  const [error, setError] = useState(false);

  // Simple client-side auth
  const CORRECT_PASSWORD = process.env.NEXT_PUBLIC_APP_PASSWORD || "marketing123";

  useEffect(() => {
    const storedAuth = localStorage.getItem("auth");
    if (storedAuth === "true") {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (password === CORRECT_PASSWORD) {
      setIsAuthenticated(true);
      localStorage.setItem("auth", "true");
      setError(false);
    } else {
      setError(true);
      setPassword("");
    }
  };

  if (isAuthenticated) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-between p-8 bg-gradient-to-br from-gray-900 to-black">
        <ChatInterface />
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gradient-to-br from-gray-900 to-black">
      <div className="w-full max-w-md p-8 rounded-3xl bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl">
        <div className="flex flex-col items-center gap-4 mb-8">
          <div className="p-3 rounded-full bg-indigo-500/20">
            <Lock className="w-8 h-8 text-indigo-400" />
          </div>
          <h1 className="text-2xl font-bold text-white text-center">Antigravity Access</h1>
          <p className="text-gray-400 text-center text-sm">Please verify your identity to continue</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter access code"
              className="w-full bg-black/20 text-white placeholder-gray-500 rounded-xl px-4 py-3 border border-white/10 focus:outline-none focus:border-indigo-500/50 transition-all font-light text-center"
              autoFocus
            />
          </div>

          {error && (
            <p className="text-red-400 text-xs text-center animate-pulse">Invalid access code</p>
          )}

          <button
            type="submit"
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-medium transition-all shadow-lg shadow-indigo-500/20"
          >
            Unlock System
          </button>
        </form>
      </div>
    </main>
  );
}
