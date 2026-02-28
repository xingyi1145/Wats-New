"use client";

import { useState } from "react";

export default function Home() {
  // Generate a random user ID for this session
  const [userId] = useState(() => "user_" + Math.random().toString(36).substring(7));
  const [profileText, setProfileText] = useState("");
  const [isStarted, setIsStarted] = useState(false);
  const [queue, setQueue] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Function to pull unseen recommendations from the Python API
  const fetchRecommendations = async (queryToUse: string) => {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: queryToUse, top_k: 5, user_id: userId }),
      });
      const data = await res.json();
      setQueue((prev) => [...prev, ...data.results]);
    } catch (error) {
      console.error("Failed to fetch", error);
    } finally {
      setLoading(false);
    }
  };

  const handleStart = (e: React.FormEvent) => {
    e.preventDefault();
    if (!profileText.trim()) return;
    setIsStarted(true);
    fetchRecommendations(profileText);
  };

  const handleInteract = async (action: "like" | "skip", link: string) => {
    // 1. Optimistically pop the top card off the queue for instant UI response
    setQueue((prev) => prev.slice(1));

    // 2. Tell the Python backend to update its memory
    try {
      await fetch("http://127.0.0.1:8000/api/interact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, link: link, action: action }),
      });
    } catch (error) {
      console.error("Interaction failed", error);
    }

    // 3. If we are running out of cards, fetch more in the background
    if (queue.length <= 2) {
      fetchRecommendations(profileText);
    }
  };

  // --- VIEW 1: ONBOARDING ---
  if (!isStarted) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="max-w-xl w-full bg-white p-8 rounded-2xl shadow-lg text-center border border-gray-100">
          <h1 className="text-4xl font-extrabold text-gray-900 mb-4">UW Nexus</h1>
          <p className="text-gray-500 mb-8">
            Stop searching. Start discovering. Tell us your major, your hobbies, and what you want to build.
          </p>
          <form onSubmit={handleStart}>
            <textarea
              value={profileText}
              onChange={(e) => setProfileText(e.target.value)}
              placeholder="e.g., I'm a CS student interested in open source, AI, and maybe joining a music club..."
              className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 min-h-[150px] resize-none mb-6 text-gray-800"
              required
            />
            <button
              type="submit"
              className="w-full bg-blue-600 text-white font-bold py-4 rounded-xl hover:bg-blue-700 transition-all text-lg"
            >
              Initialize My Feed
            </button>
          </form>
        </div>
      </main>
    );
  }

  // --- VIEW 2: THE DISCOVERY DECK ---
  const currentCard = queue[0];

  return (
    <main className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md">
        
        {/* Header */}
        <div className="flex justify-between items-center mb-6 px-2">
          <h1 className="text-2xl font-bold text-gray-800">For You</h1>
          <span className="text-xs font-bold text-gray-400 bg-gray-200 px-3 py-1 rounded-full uppercase tracking-wider">
            {userId.substring(0, 9)}
          </span>
        </div>

        {/* The Card */}
        {currentCard ? (
          <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-gray-200 transition-all">
            <div className="p-8 min-h-[350px] flex flex-col justify-center">
              <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-bold uppercase tracking-wide mb-4 w-max">
                {currentCard.source.replace("_", " ")}
              </span>
              <h2 className="text-3xl font-extrabold text-gray-900 mb-4 leading-tight">
                {currentCard.title}
              </h2>
              <div className="mt-auto pt-6 border-t border-gray-100">
                <span className="text-sm font-semibold text-gray-500">
                  AI Match Score: <span className="text-green-600">{currentCard.match_score}%</span>
                </span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex border-t border-gray-100">
              <button
                onClick={() => handleInteract("skip", currentCard.link)}
                className="flex-1 py-6 text-xl font-bold text-gray-400 hover:bg-red-50 hover:text-red-500 transition-colors"
              >
                Skip
              </button>
              <div className="w-px bg-gray-100"></div>
              <button
                onClick={() => {
                  window.open(currentCard.link, "_blank");
                  handleInteract("like", currentCard.link);
                }}
                className="flex-1 py-6 text-xl font-bold text-blue-500 hover:bg-blue-50 hover:text-blue-600 transition-colors"
              >
                Save & View
              </button>
            </div>
          </div>
        ) : (
          /* Empty State / Loading State */
          <div className="bg-white rounded-3xl shadow-lg p-12 text-center border border-gray-200 min-h-[400px] flex flex-col items-center justify-center">
            {loading ? (
              <div className="animate-pulse flex flex-col items-center">
                <div className="h-12 w-12 bg-blue-200 rounded-full mb-4"></div>
                <p className="text-gray-500 font-medium">Scanning vectors for more...</p>
              </div>
            ) : (
              <div>
                <h3 className="text-2xl font-bold text-gray-800 mb-2">You beat the algorithm!</h3>
                <p className="text-gray-500">We've run out of highly relevant matches for this specific vibe.</p>
                <button 
                  onClick={() => window.location.reload()}
                  className="mt-6 px-6 py-2 bg-gray-900 text-white rounded-lg font-medium"
                >
                  Start Over
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}