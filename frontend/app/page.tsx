"use client";

import { useState } from "react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    setResults([]);

    try {
      // This hits your local Python server!
      const response = await fetch("http://127.0.0.1:8000/api/recommend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query, top_k: 5 }),
      });

      if (!response.ok) {
        throw new Error("Failed to connect to the Opportunity Engine.");
      }

      const data = await response.json();
      setResults(data.results);
    } catch (err: any) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 text-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl">
            WAT's NEW
          </h1>
          <p className="mt-4 text-xl text-gray-500">
            Break the information bubble. Tell us what you care about in a few sentences, and we'll find your next opportunity.
          </p>
        </div>

        {/* Search Box */}
        <form onSubmit={handleSearch} className="mb-10 bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., I love software engineering and coding, but I also want to get involved with music and performing arts..."
            className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[120px] resize-none"
          ></textarea>
          <div className="mt-4 flex justify-end">
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:bg-blue-300 disabled:cursor-not-allowed"
            >
              {loading ? "Searching Vector Space..." : "Discover"}
            </button>
          </div>
        </form>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6 border border-red-200">
            {error}
          </div>
        )}

        {/* Results List */}
        <div className="space-y-4">
          {results.map((result: any, index: number) => (
            <div key={index} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start gap-4">
                <h2 className="text-xl font-bold text-gray-900">
                  <a href={result.link} target="_blank" rel="noopener noreferrer" className="hover:text-blue-600 hover:underline">
                    {result.title}
                  </a>
                </h2>
                <span className="bg-blue-100 text-blue-800 text-sm font-semibold px-3 py-1 rounded-full whitespace-nowrap">
                  {result.match_score}% Match
                </span>
              </div>
              <div className="mt-2 text-sm text-gray-500 flex items-center gap-2 font-medium">
                <span className="uppercase tracking-wider px-2 py-1 bg-gray-100 rounded-md text-xs">{result.item_type || 'Opportunity'}</span>
                <span>•</span>
                <span>{result.source}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}