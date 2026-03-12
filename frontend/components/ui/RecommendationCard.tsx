"use client";

import { useState, useEffect } from "react";
import { useAuth, SignInButton } from "@clerk/nextjs";

interface Props {
  currentCard: any;
  displayDescription: string;
  onNext: () => void;
  onView: (e: React.MouseEvent<HTMLButtonElement>, link: string) => void;
  onSaveClicked: () => void;
  onAlreadyKnow: () => void;
  onFlagClicked: () => void;
}

export default function RecommendationCard({
  currentCard,
  displayDescription,
  onNext,
  onView,
  onSaveClicked,
  onAlreadyKnow,
  onFlagClicked
}: Props) {
  const { isSignedIn } = useAuth();
  const [isFlagged, setIsFlagged] = useState(false);
  const [intentToSave, setIntentToSave] = useState(false);

  const handleLoginIntent = () => {
    setIntentToSave(true);
  };

  useEffect(() => {
    if (isSignedIn && intentToSave) {
      onSaveClicked();
      setIntentToSave(false); // Reset intent
    }
  }, [isSignedIn, intentToSave, onSaveClicked]);

  useEffect(() => {
    setIsFlagged(false);
  }, [currentCard?.title, currentCard?.link]);

  const handleFlagClick = () => {
    setIsFlagged(true);
    onFlagClicked();
  };

  if (!currentCard) return null;

  return (
    <div className="flex-grow bg-white rounded-[2rem] shadow-2xl overflow-hidden flex flex-col border border-white/20 transform transition-all hover:scale-[1.01] max-h-[75vh] relative">

      {/* Card Content Area */}
      <div className="flex-grow p-8 sm:p-12 overflow-y-auto min-h-[250px]">
        <div className="flex items-start justify-between mb-6 gap-4">
          <span className="inline-flex items-center px-4 py-1.5 rounded-full text-sm font-semibold bg-blue-50 text-blue-700 border border-blue-100 uppercase tracking-wide">
            {currentCard.source?.replace(/_/g, " ")}
          </span>
          <span className="flex items-center gap-1 text-sm font-bold text-slate-400 bg-slate-50 px-3 py-1 rounded-full mr-20">
            Match <span className="text-emerald-500">{currentCard.match_score || "N/A"}%</span>
          </span>
        </div>

        <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 leading-tight mb-6 pr-12">
          {currentCard.title}
        </h2>
        
        <div className="prose prose-lg text-slate-600 leading-relaxed">
          <p className="line-clamp-5">{displayDescription}</p>
        </div>
      </div>

      <div className="bg-white px-8 sm:px-12 pb-4 flex justify-end shrink-0">
        <button
          onClick={handleFlagClick}
          disabled={isFlagged}
          className="flex items-center gap-1.5 text-xs text-neutral-400 hover:text-orange-500 transition-colors disabled:text-neutral-300 disabled:cursor-not-allowed"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          {isFlagged ? "Flagged" : "Flag Issue"}
        </button>
      </div>

      {/* Actions */}
      <div className="bg-slate-50 p-8 sm:p-12 shrink-0 border-t border-slate-100 rounded-b-[2rem]">
        <div className="flex gap-4">
          <button
            onClick={onNext}
            className="flex-1 py-5 rounded-xl text-lg font-bold text-slate-600 bg-white border-2 border-slate-200 hover:bg-slate-100 transition-all shadow-sm"
          >
            Next
          </button>
          
          {isSignedIn ? (
            <button
              onClick={onSaveClicked}
              className="flex-1 py-5 rounded-xl text-lg font-bold text-white bg-emerald-500 hover:bg-emerald-600 transition-all shadow-sm"
            >
              Save
            </button>
          ) : (
            <SignInButton 
              mode="modal" 
              fallbackRedirectUrl="" 
              forceRedirectUrl=""
            >
              <button 
                onClick={handleLoginIntent}
                className="flex-1 py-5 rounded-xl text-lg font-bold text-slate-400 bg-white border-2 border-slate-200 hover:bg-slate-50 hover:text-slate-500 transition-all shadow-sm"
              >
                Log in to Save
              </button>
            </SignInButton>
          )}

          <button
            onClick={(e) => onView(e, currentCard.link)}
            className="flex-[2] py-5 rounded-xl text-lg font-bold text-white bg-blue-600 hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/30 transform hover:-translate-y-0.5"
          >
            View Opportunity
          </button>
        </div>

        <div className="pb-4 px-6 text-center mt-4">
          <button 
            onClick={onAlreadyKnow}
            className="text-sm text-slate-400 hover:text-slate-600 font-medium transition-colors"
          >
            I already know about this.
          </button>
        </div>
      </div>
    </div>
  );
}
