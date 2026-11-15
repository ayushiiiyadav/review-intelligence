"use client";
import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const LABELS = {
  overall: "Overall",
  delivery: "Delivery",
  food_quality: "Food quality",
  support: "Support",
  refund_payment: "Refunds & payments",
  pricing_offers: "Pricing & offers",
  app_bugs: "App bugs",
};

function Bar({ value, color }) {
  if (value == null) return <span className="text-gray-400 text-sm">n/a</span>;
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 flex-1 rounded bg-gray-200">
        <div className={`h-2 rounded ${color}`} style={{ width: `${value}%` }} />
      </div>
      <span className="w-12 text-right text-sm tabular-nums">{value}%</span>
    </div>
  );
}

function verdictText(v) {
  if (v === "swiggy more negative") return "Swiggy higher";
  if (v === "zomato more negative") return "Zomato higher";
  if (v === "no clear difference") return "No clear difference";
  return "Not enough data";
}

export default function Home() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API}/compare`)
      .then((r) => r.json())
      .then(setData)
      .catch(() => setError("Could not reach the API. Is the backend running?"));
  }, []);

  if (error) return <main className="p-8 text-red-600">{error}</main>;
  if (!data) return <main className="p-8">Loading...</main>;

  const apps = Object.keys(data.overall);

  return (
    <main className="mx-auto max-w-4xl p-6 sm:p-10">
      <h1 className="text-3xl font-bold">Review Intelligence</h1>
      <p className="mt-1 text-gray-400">
        What public Play Store reviews say, {data.window}.
      </p>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        {apps.map((a) => (
          <div key={a} className="rounded-xl border p-5">
            <h2 className="text-xl font-semibold capitalize">{a}</h2>
            <p className="mt-2 text-4xl font-bold">{data.overall[a].avg_stars.toFixed(2)}</p>
            <p className="text-sm text-gray-400">
              average stars from {data.overall[a].reviews.toLocaleString()} reviews
            </p>
          </div>
        ))}
      </div>

      <h2 className="mt-10 text-xl font-semibold">Share of negative reviews by topic</h2>
      <p className="text-sm text-gray-400">
        Among text reviews that mention each topic. Lower is better.
      </p>

      <div className="mt-4 overflow-x-auto rounded-xl border">
        <table className="w-full text-left">
          <thead className="bg-white/10 text-sm">
            <tr>
              <th className="p-3">Topic</th>
              <th className="p-3 capitalize">{apps[0]}</th>
              <th className="p-3 capitalize">{apps[1]}</th>
              <th className="p-3">Is the gap real?</th>
            </tr>
          </thead>
          <tbody>
            {data.aspects.map((row) => (
              <tr key={row.aspect} className="border-t">
                <td className="p-3 font-medium">{LABELS[row.aspect] || row.aspect}</td>
                <td className="p-3 min-w-37.5">
                  <Bar value={row[`${apps[0]}_neg_pct`]} color="bg-orange-500" />
                  <span className="text-xs text-gray-400">{row[`${apps[0]}_n`]} reviews</span>
                </td>
                <td className="p-3 min-w-37.5">
                  <Bar value={row[`${apps[1]}_neg_pct`]} color="bg-red-500" />
                  <span className="text-xs text-gray-400">{row[`${apps[1]}_n`]} reviews</span>
                </td>
                <td className="p-3 text-sm">{verdictText(row.verdict)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="mt-8 text-xs text-gray-400">
        Results reflect a sample of public user reviews (text reviews of 5+ words)
        and not the actual performance of any company. Topics are matched by keywords,
        so some reviews may be misclassified. This project is not affiliated with or
        endorsed by any company.
      </p>
    </main>
  );
}