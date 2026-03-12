"use client";

import { useEffect, useState } from "react";
import { useAuth, SignInButton } from "@clerk/nextjs";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

type SavedItem = {
  item_id: string;
  title: string;
  snippet: string;
  link: string;
  source: string;
};

export default function DeckPage() {
  const { isLoaded, isSignedIn, userId } = useAuth();
  const [items, setItems] = useState<SavedItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!isLoaded || !isSignedIn || !userId) {
      setIsLoading(false);
      return;
    }

    const fetchDeck = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/deck?user_id=${userId}`);
        if (!res.ok) throw new Error("Failed to fetch deck");
        const data = await res.json();
        setItems(data || []);
      } catch (error) {
        console.error("Error fetching deck:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDeck();
  }, [isLoaded, isSignedIn, userId]);

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center font-sans">
        <p className="text-white/50">Loading...</p>
      </div>
    );
  }

  if (!isSignedIn) {
    return (
      <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center font-sans">
        <div className="bg-white/[0.03] backdrop-blur-xl border border-white/10 p-8 rounded-2xl text-center max-w-md w-full">
          <h1 className="text-2xl font-semibold mb-4 text-white">Access Denied</h1>
          <p className="text-white/60 mb-8">
            Please log in to view your saved opportunities.
          </p>
          <SignInButton mode="modal">
            <button className="bg-white text-black px-6 py-2 rounded-full font-medium hover:bg-white/90 transition-colors">
              Log In
            </button>
          </SignInButton>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white font-sans p-6 md:p-12">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-12">
          <h1 className="text-3xl md:text-5xl font-bold tracking-tight text-white">My Saved Deck</h1>
          <Link href="/">
            <button className="bg-white/[0.05] hover:bg-white/[0.1] border border-white/10 px-4 py-2 rounded-full text-sm font-medium transition-colors">
              Back to Swipe
            </button>
          </Link>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-20">
            <p className="text-white/50">Loading your deck...</p>
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-32 rounded-2xl bg-white/[0.02] border border-white/5">
            <p className="text-xl text-white/40 mb-6">Your deck is empty. Go swipe on some opportunities.</p>
            <Link href="/">
              <button className="bg-white text-black px-6 py-3 rounded-full font-medium hover:bg-white/90 transition-colors">
                Start Swiping
              </button>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((item, index) => (
              <div 
                key={`${item.item_id}-${index}`} 
                className="bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-2xl p-6 flex flex-col"
              >
                <div className="flex-1 mb-6">
                  <div className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-2">
                    {item.source}
                  </div>
                  <h2 className="text-lg font-bold text-white mb-3 leading-tight line-clamp-2">
                    {item.title}
                  </h2>
                  <p className="text-sm text-white/70 line-clamp-3 leading-relaxed">
                    {item.snippet}
                  </p>
                </div>
                
                <a 
                  href={item.link} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="w-full"
                >
                  <button className="w-full bg-white text-black py-3 rounded-xl font-medium hover:bg-white/90 transition-colors text-sm">
                    View Opportunity
                  </button>
                </a>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
