"use client";

import { useState, useEffect } from "react";
import { useAuth, SignInButton, UserButton } from "@clerk/nextjs";
import Link from "next/link";
import RecommendationCard from "../components/ui/RecommendationCard";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function Home() {
  const { isSignedIn, userId: clerkUserId } = useAuth(); 
  const [userId, setUserId] = useState("");
  const [profileText, setProfileText] = useState("");
  const [isStarted, setIsStarted] = useState(false);
  const [queue, setQueue] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasViewedCurrent, setHasViewedCurrent] = useState(false);

  useEffect(() => {
    const initializeSession = async () => {
      const localId = localStorage.getItem("nexus_user_id");

      // --- STEP 1: RESOLVE IDENTITY & MIGRATE ---
      if (clerkUserId) {
        if (localId && localId !== clerkUserId) {
          try {
            // AWAIT the migration to finish so SQLite doesn't lock up!
            await fetch(`${API_BASE}/api/migrate`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ old_user_id: localId, new_user_id: clerkUserId }),
            });
            localStorage.removeItem("nexus_user_id"); 
          } catch (error) {
            console.error("Migration failed:", error);
          }
        }
        setUserId(clerkUserId);
      } else {
        if (!localId) {
          const newLocalId = "user_" + Math.random().toString(36).substring(7);
          localStorage.setItem("nexus_user_id", newLocalId);
          setUserId(newLocalId);
        } else {
          setUserId(localId);
        }
      }

      // --- STEP 2: RESTORE QUEUE ---
      const savedQueue = localStorage.getItem("nexus_saved_queue");
      if (savedQueue) {
        try {
          const parsed = JSON.parse(savedQueue);
          if (Array.isArray(parsed) && parsed.length > 0) {
            setQueue(parsed);
            setIsStarted(true);
          }
        } catch { /* ignore parse errors */ }
        localStorage.removeItem("nexus_saved_queue");
      }

      // --- STEP 3: EXECUTE AUTO-SAVE & TRACK INTERACTION ---
      if (clerkUserId) {
        const rawSave = localStorage.getItem("nexus_pending_save");
        if (rawSave) {
          try {
            const card = JSON.parse(rawSave);
            localStorage.removeItem("nexus_pending_save");

            const payload = {
              user_id: clerkUserId,
              item_id: card.link,
              title: card.title || "Unknown Title",
              snippet: card.snippet || card.description || card.content || "No description",
              link: card.link,
              source: card.source || "unknown",
            };

            // AWAIT the save so we know the database is free
            await fetch(`${API_BASE}/api/save`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload),
            });

            // CRITICAL: Record the interaction so the AI vector shifts!
            await fetch(`${API_BASE}/api/interact`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ user_id: clerkUserId, link: card.link, action: "like" }),
            });

            // Safely advance the queue only after successful backend writes
            setQueue((prev) => prev.slice(1));
          } catch (err) {
            console.error("Auto-save failed:", err);
          }
        }
      }
    };

    initializeSession();
  }, [clerkUserId]);

  const fetchRecommendations = async (queryToUse: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/recommend`, {
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
    // Optimistically remove the card
    setQueue((prev) => prev.slice(1));

    try {
      await fetch(`${API_BASE}/api/interact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, link: link, action: action }),
      });
    } catch (error) {
      console.error("Interaction failed", error);
    }

    if (queue.length <= 2) {
      fetchRecommendations(profileText);
    }
  };

  const logTelemetry = async (novelty: number, utility: number) => {
    if (!queue[0]) return;
    try {
      await fetch(`${API_BASE}/api/telemetry`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          item_id: queue[0].link,
          vibe_query: profileText,
          novelty,
          utility
        }),
      });
    } catch (error) {
      // Ignored
    }
  };

  const handleNext = () => {
    if (!queue[0]) return;
    if (hasViewedCurrent) {
      logTelemetry(1, 1);
      // Viewed, assume utility=1 is a 'like'
      handleInteract("like", queue[0].link);
    } else {
      logTelemetry(1, 0);
      handleInteract("skip", queue[0].link);
    }
    setHasViewedCurrent(false);
  };

  const handleAlreadyKnow = () => {
    if (!queue[0]) return;
    logTelemetry(0, 1);
    handleInteract("like", queue[0].link);
    setHasViewedCurrent(false);
  };

  // Safely open the link without interrupting React's state update
  const handleViewOpportunity = (e: React.MouseEvent, link: string) => {
    e.preventDefault();
    setHasViewedCurrent(true);
    window.open(link, "_blank", "noopener,noreferrer");
  };

  const handleFlagIssue = async () => {
    if (!queue[0]) return;
    try {
      await fetch(`${API_BASE}/api/flag`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_id: queue[0].link }),
      });
    } catch (error) {
      // Ignored
    }
  };

const handleSaveItem = async () => {
    // Grab the active card from your queue
    const currentItem = queue[0];

    // 1. Guard against nulls
    if (!userId) {
      console.error("Debug: Cannot save, userId is null. Is Clerk loaded?");
      return;
    }
    if (!currentItem) {
      console.error("Debug: Cannot save, currentItem is null.");
      return;
    }

    try {
      // 2. Map the payload using your actual JSON keys
      const payload = {
        user_id: userId,
        item_id: currentItem.link,
        title: currentItem.title || "Unknown Title",
        snippet: currentItem.snippet || currentItem.description || currentItem.content || "No description",
        link: currentItem.link,
        source: currentItem.source || "unknown"
      };
      
      console.log("Debug: Sending payload to backend...", payload);

      // Make sure your API_BASE URL matches your actual Python backend URL
      const response = await fetch(`${API_BASE}/api/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
          // Catch FastAPI rejections (e.g., 422 Unprocessable Entity)
          const errorText = await response.text();
          console.error(`Debug: Backend rejected the save (Status ${response.status}):`, errorText);
      } else {
          console.log("Debug: Save successful!");
      }
    } catch (error) {
      // Catch Network/CORS errors
      console.error("Debug: Network fetch failed:", error);
    }

    // Advance the card to keep the UI moving
    handleNext(); 
  };

  const triggerLoginIntent = () => {
    localStorage.setItem("nexus_saved_queue", JSON.stringify(queue));
  };

  // --- VIEW 1: ONBOARDING ---
  if (!isStarted) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex flex-col">
        <nav className="w-full flex items-center justify-between px-6 py-4">
          <span className="text-xl font-bold text-slate-900 tracking-tight">Wats-New</span>
          <div className="flex items-center gap-4">
            {isSignedIn ? (
              <>
                <Link href="/deck" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">My Deck</Link>
                <UserButton />
              </>
          ) : (
              <SignInButton mode="modal">
                <button className="px-4 py-2 bg-white text-slate-900 text-sm font-semibold rounded-lg border border-slate-200 hover:bg-slate-50 transition-colors shadow-sm">
                  Sign In
              </button>
            </SignInButton>
          )}
          </div>
        </nav>
        <div className="flex-grow flex items-center justify-center p-4">
        <div className="max-w-2xl w-full bg-white/80 backdrop-blur-xl p-10 rounded-3xl shadow-2xl border border-white/40 text-center">
          <div className="w-16 h-16 bg-blue-600 rounded-2xl mx-auto mb-6 flex items-center justify-center shadow-lg shadow-blue-200">
            <span className="text-3xl text-white font-bold">W</span>
          </div>
          <h1 className="text-5xl font-extrabold text-slate-900 mb-4 tracking-tight">Wats-New</h1>
          <p className="text-lg text-slate-500 mb-10 max-w-lg mx-auto leading-relaxed">
            Stop searching. Start discovering. Tell us your major, your hobbies, and what you want to build.
          </p>
          <form onSubmit={handleStart} className="relative">
            <textarea
              value={profileText}
              onChange={(e) => setProfileText(e.target.value)}
              placeholder="e.g., I'm a CS student interested in open source, AI, and maybe joining a music club..."
              className="w-full p-6 border-2 border-slate-100 rounded-2xl focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 min-h-[160px] resize-none mb-6 text-slate-800 text-lg transition-all shadow-inner"
              required
            />
            <button
              type="submit"
              className="w-full bg-slate-900 text-white font-bold py-5 rounded-2xl hover:bg-blue-600 transition-colors text-xl shadow-xl hover:shadow-blue-500/30"
            >
              Initialize Engine
            </button>
          </form>
        </div>
        </div>
      </main>
    );
  }

  // --- VIEW 2: THE DISCOVERY DECK ---
  const currentCard = queue[0];

  // Defensive fallback for messy data
  const displayDescription = currentCard?.snippet || currentCard?.description || currentCard?.content || "No detailed description provided by the source.";

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex flex-col">
      
      {/* Nav Bar */}
      <nav className="w-full flex items-center justify-between px-6 py-4 relative z-20">
        <span className="text-xl font-bold text-white tracking-tight">Wats-New</span>
        <div className="flex items-center gap-4">
          {isSignedIn ? (
            <>
              <Link href="/deck" className="text-sm font-medium text-blue-200 hover:text-white transition-colors">My Deck</Link>
              <UserButton />
            </>
          ) : (
            <SignInButton mode="modal">
              <button className="px-4 py-2 bg-white text-slate-900 text-sm font-semibold rounded-lg hover:bg-slate-100 transition-colors shadow-sm">
                Sign In
              </button>
            </SignInButton>
          )}
        </div>
      </nav>

      {/* Dynamic Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-500/20 rounded-full blur-[120px] pointer-events-none"></div>

      <div className="flex-grow flex flex-col items-center justify-center p-4 sm:p-8">
      <div className="w-full max-w-3xl relative z-10 flex flex-col h-full max-h-[900px]">
        
        {/* Header */}
        <div className="flex justify-between items-center mb-8 px-4">
          <h1 className="text-3xl font-bold text-white tracking-tight">Discovery Feed</h1>
          <div className="flex items-center gap-3">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </span>
            <span className="text-sm font-medium text-blue-200 uppercase tracking-widest bg-white/10 px-4 py-2 rounded-full backdrop-blur-sm border border-white/5">
              ID: {userId.substring(0, 9)}
            </span>
          </div>
        </div>

        {/* The Card */}
        {currentCard ? (
          <RecommendationCard 
            currentCard={currentCard}
            displayDescription={displayDescription}
            onNext={() => handleInteract("skip", currentCard.link)}
            onView={handleViewOpportunity}
            onSaveClicked={handleSaveItem}
            onLoginIntent={triggerLoginIntent}
            onAlreadyKnow={handleAlreadyKnow}
            onFlagClicked={handleFlagIssue}
          />
        ) : (
          /* Loading / Empty State */
          <div className="flex-grow bg-white/10 backdrop-blur-xl rounded-[2rem] border border-white/10 p-12 text-center flex flex-col items-center justify-center shadow-2xl">
            {loading ? (
              <div className="animate-pulse flex flex-col items-center">
                <div className="h-16 w-16 bg-blue-500/50 rounded-full mb-6 flex items-center justify-center">
                  <div className="h-8 w-8 bg-white rounded-full animate-bounce"></div>
                </div>
                <p className="text-xl text-blue-100 font-medium">Computing vectors...</p>
              </div>
            ) : (
              <div className="max-w-md">
                <div className="text-6xl mb-6">🎯</div>
                <h3 className="text-3xl font-bold text-white mb-4">You beat the algorithm!</h3>
                <p className="text-blue-200 text-lg mb-8 leading-relaxed">We've run out of highly relevant matches for this specific vibe. Time to cast a wider net.</p>
                <button 
                  onClick={() => window.location.reload()}
                  className="px-8 py-4 bg-white text-slate-900 rounded-xl font-bold text-lg hover:bg-blue-50 transition-colors shadow-lg"
                >
                  Start a New Search
                </button>
              </div>
            )}
          </div>
        )}
      </div>
      </div>
    </main>
  );
}