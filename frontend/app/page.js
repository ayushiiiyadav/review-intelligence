"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import "./review.css";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const LABELS = {
  overall: "All topics",
  delivery: "Delivery",
  food_quality: "Food quality",
  support: "Support",
  refund_payment: "Refunds & payments",
  pricing_offers: "Pricing & offers",
  app_bugs: "App bugs",
};
const TOPICS = ["delivery", "food_quality", "support", "refund_payment", "pricing_offers", "app_bugs"];
const AXIS_MIN = 30;

const nf = (n) => Number(n).toLocaleString("en-IN");
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
const pos = (v) => Math.min(100, Math.max(0, ((v - AXIS_MIN) / (100 - AXIS_MIN)) * 100));

function wilson(k, n, z = 1.96) {
  if (!n) return [0, 0];
  const p = k / n;
  const d = 1 + (z * z) / n;
  const c = (p + (z * z) / (2 * n)) / d;
  const m = (z * Math.sqrt((p * (1 - p)) / n + (z * z) / (4 * n * n))) / d;
  return [Math.max(0, c - m) * 100, Math.min(1, c + m) * 100];
}

function prepare(data) {
  const apps = Object.keys(data.overall);
  const rows = data.aspects.map((r) => {
    const per = {};
    apps.forEach((a) => {
      const pct = r[`${a}_neg_pct`];
      const n = r[`${a}_n`];
      if (pct == null || !n) {
        per[a] = null;
        return;
      }
      const [lo, hi] = wilson(Math.round((pct / 100) * n), n);
      per[a] = { pct, n, lo, hi };
    });
    const x = per[apps[0]];
    const y = per[apps[1]];
    let state = "unclear";
    if (x && y) {
      if (x.lo > y.hi) state = apps[0];
      else if (y.lo > x.hi) state = apps[1];
      else state = "none";
    }
    return { aspect: r.aspect, per, state };
  });
  return { apps, rows };
}

function buildSummary(apps, rows) {
  const [a, b] = apps;
  const out = [];
  const overall = rows.find((r) => r.aspect === "overall");
  if (overall && overall.per[a] && overall.per[b]) {
    if (overall.state === a || overall.state === b) {
      const hi = overall.state;
      const lo = hi === a ? b : a;
      out.push(
        `In this sample, ${cap(hi)} reviewers were more negative overall (${overall.per[hi].pct.toFixed(1)}% vs ${overall.per[lo].pct.toFixed(1)}%), and the gap is larger than sampling noise.`
      );
    } else {
      out.push(
        `In this sample, the two apps are too close overall to separate (${overall.per[a].pct.toFixed(1)}% vs ${overall.per[b].pct.toFixed(1)}% negative).`
      );
    }
  }
  const cands = rows.filter(
    (r) => TOPICS.includes(r.aspect) && r.per[a] && r.per[b] && r.per[a].n >= 100 && r.per[b].n >= 100
  );
  if (cands.length) {
    const best = cands.reduce((m, r) =>
      r.per[a].pct + r.per[b].pct > m.per[a].pct + m.per[b].pct ? r : m
    );
    out.push(
      `${LABELS[best.aspect]} was the most negative topic across both apps (${best.per[a].pct.toFixed(1)}% and ${best.per[b].pct.toFixed(1)}%).`
    );
  }
  return out;
}

function useInView(threshold = 0.2) {
  const ref = useRef(null);
  const [seen, setSeen] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (typeof IntersectionObserver === "undefined") {
      setSeen(true);
      return;
    }
    const io = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          setSeen(true);
          io.disconnect();
        }
      },
      { threshold }
    );
    io.observe(el);
    return () => io.disconnect();
  }, [threshold]);
  return [ref, seen];
}

function CountUp({ to, duration = 900 }) {
  const [ref, seen] = useInView(0.4);
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!seen) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setVal(to);
      return;
    }
    let raf;
    let start;
    const tick = (t) => {
      if (!start) start = t;
      const p = Math.min(1, (t - start) / duration);
      setVal(to * (1 - Math.pow(1 - p, 3)));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [seen, to, duration]);
  return <span ref={ref}>{nf(Math.round(val))}</span>;
}

function Receipt({ app, side, reviews, written, stars, rows, hot, setHot }) {
  const top = rows
    .filter((r) => r.n >= 100)
    .reduce((m, r) => (!m || r.pct > m.pct ? r : m), null);
  return (
    <article className={`receipt ${side}`}>
      <div className="receipt-paper">
        <header className="r-head">
          <h2>{cap(app)}</h2>
          <p>{nf(reviews)} reviews in window</p>
        </header>
        <div className="r-rule" />
        <p className="r-sub">Negative share of {nf(written)} written reviews, by topic</p>
        <ul className="r-lines">
          {rows.map((r) => {
            const isTop = top && top.aspect === r.aspect;
            return (
              <li
                key={r.aspect}
                tabIndex={0}
                className={`${hot === r.aspect ? "is-hot" : ""} ${isTop ? "is-top" : ""}`}
                onMouseEnter={() => setHot(r.aspect)}
                onMouseLeave={() => setHot(null)}
                onFocus={() => setHot(r.aspect)}
                onBlur={() => setHot(null)}
              >
                <span className="r-name">{LABELS[r.aspect]}</span>
                <span className="r-dots" aria-hidden="true" />
                <span className="r-val">{r.pct.toFixed(1)}%</span>
                <span className="r-bar" aria-hidden="true">
                  <i style={{ width: `${r.pct}%` }} />
                </span>
                <span className="r-n">
                  {nf(r.n)} reviews{isTop ? " · highest on this receipt" : ""}
                </span>
              </li>
            );
          })}
        </ul>
        <div className="r-rule" />
        <dl className="r-total">
          <dt>Average stars, all reviews</dt>
          <dd>{stars.toFixed(2)}</dd>
        </dl>
        <div className="r-barcode" aria-hidden="true" />
      </div>
    </article>
  );
}

function GapChart({ apps, rows, hot, setHot }) {
  const [ref, seen] = useInView(0.15);
  const ticks = [40, 60, 80, 100];
  const colors = ["var(--a)", "var(--b)"];
  return (
    <section className="ri-section" aria-labelledby="gap-h">
      <h2 id="gap-h">Are the gaps real?</h2>
      <p className="ri-sub">
        Each bar is a 95% confidence range for the share of negative reviews, and the dot is the
        measured value. When two ranges overlap, this sample can&apos;t tell the apps apart on that
        topic. The axis starts at 30%.
      </p>
      <div className="gap-legend">
        {apps.map((a, i) => (
          <span key={a} style={{ "--c": colors[i] }}>
            {cap(a)}
          </span>
        ))}
      </div>
      <div ref={ref} className={`gap-rows ${seen ? "is-seen" : ""}`}>
        <div className="gap-row gap-axis-row" aria-hidden="true">
          <span />
          <div className="gap-axis">
            {ticks.map((t, i) => (
              <span key={t} className={i === ticks.length - 1 ? "last" : ""} style={{ left: `${pos(t)}%` }}>
                {t}%
              </span>
            ))}
          </div>
          <span />
        </div>
        {rows.map((r, i) => {
          const x = r.per[apps[0]];
          const y = r.per[apps[1]];
          let verdict = "Too few reviews";
          if (r.state === "none") verdict = "Can't tell apart";
          else if (r.state !== "unclear") verdict = `Gap holds: ${cap(r.state)} higher`;
          const nums = x && y ? `${x.pct.toFixed(1)}% vs ${y.pct.toFixed(1)}%` : "";
          return (
            <div
              key={r.aspect}
              className={`gap-row ${hot === r.aspect ? "is-hot" : ""}`}
              style={{ "--i": i }}
              onMouseEnter={() => setHot(r.aspect)}
              onMouseLeave={() => setHot(null)}
            >
              <div className="gap-name">{LABELS[r.aspect]}</div>
              <div
                className="gap-track"
                role="img"
                aria-label={`${LABELS[r.aspect]}: ${nums}. ${verdict}.`}
              >
                {apps.map((a, li) => {
                  const d = r.per[a];
                  if (!d) return null;
                  return (
                    <div key={a} className={`gap-lane l${li + 1}`} style={{ "--c": colors[li] }}>
                      <span
                        className="gap-range"
                        style={{ left: `${pos(d.lo)}%`, width: `${pos(d.hi) - pos(d.lo)}%` }}
                      />
                      <span className="gap-dot" style={{ left: `${pos(d.pct)}%` }} />
                    </div>
                  );
                })}
              </div>
              <div className={`gap-verdict ${r.state === "none" || r.state === "unclear" ? "" : "holds"}`}>
                {verdict}
                <span className="gap-nums">{nums}</span>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function Pipeline({ data, apps, rows }) {
  const totalReviews = apps.reduce((s, a) => s + data.overall[a].reviews, 0);
  const overall = rows.find((r) => r.aspect === "overall");
  const written = apps.reduce((s, a) => s + (overall?.per[a]?.n || 0), 0);
  return (
    <section className="ri-section" aria-labelledby="how-h">
      <h2 id="how-h">How this was made</h2>
      <ol className="steps">
        <li className="step">
          <div>
            <h3>Collect public reviews</h3>
            <p>Play Store reviews for both apps, cut to the same dates so neither gets a head start.</p>
            <div className="step-stat">
              <CountUp to={totalReviews} /> reviews, {data.window}
            </div>
          </div>
        </li>
        <li className="step">
          <div>
            <h3>Keep the written ones</h3>
            <p>
              Star averages use every review. The topic analysis uses reviews of five or more words,
              because a lone &quot;good&quot; says nothing about why.
            </p>
            <div className="step-stat">
              <CountUp to={written} /> written reviews
            </div>
          </div>
        </li>
        <li className="step">
          <div>
            <h3>Read the tone</h3>
            <p>
              A multilingual sentiment model labels each written review positive, neutral or negative.
              Romanised Hindi is its weak spot, so some Hinglish reviews may be misread.
            </p>
          </div>
        </li>
        <li className="step">
          <div>
            <h3>Tag the topics</h3>
            <p>
              Keyword lists sort reviews into six topics. A review that mentions two topics counts
              toward both.
            </p>
          </div>
        </li>
        <li className="step">
          <div>
            <h3>Test the gaps</h3>
            <p>
              Every percentage gets a 95% confidence range. When two ranges overlap, the page says it
              can&apos;t tell the apps apart.
            </p>
          </div>
        </li>
      </ol>
    </section>
  );
}

export default function Home() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [hot, setHot] = useState(null);

  const load = useCallback(() => {
    fetch(`${API}/compare`)
      .then((r) => {
        if (!r.ok) throw new Error("bad response");
        return r.json();
      })
      .then(setData)
      .catch(() =>
        setError("Couldn't load the results. The server may be waking up, so try again in a minute.")
      );
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  if (error) {
    return (
      <main className="ri">
        <div className="ri-wrap ri-status">
          <h1>Review Intelligence</h1>
          <p>{error}</p>
          <button
            className="ri-btn"
            onClick={() => {
              setError("");
              load();
            }}
          >
            Try again
          </button>
        </div>
      </main>
    );
  }
  if (!data) {
    return (
      <main className="ri">
        <div className="ri-wrap ri-status">
          <h1>Review Intelligence</h1>
          <p>Loading results. If the server was idle, this can take up to a minute.</p>
        </div>
      </main>
    );
  }

  const { apps, rows } = prepare(data);
  const summary = buildSummary(apps, rows);
  const overall = rows.find((r) => r.aspect === "overall");
  const rowsFor = (app) =>
    TOPICS.map((t) => rows.find((r) => r.aspect === t))
      .filter((r) => r && r.per[app])
      .map((r) => ({ aspect: r.aspect, ...r.per[app] }));

  return (
    <main className="ri">
      <div className="ri-wrap">
        <header>
          <h1>Review Intelligence</h1>
          {summary.map((s, i) => (
            <p key={i} className="ri-lede">
              {s}
            </p>
          ))}
          <p className="ri-window">Public Play Store reviews, {data.window}.</p>
        </header>

        <div className="printer" aria-hidden="true" />
        <div className="receipts">
          {apps.map((a, i) => (
            <Receipt
              key={a}
              app={a}
              side={i === 0 ? "side-a" : "side-b"}
              reviews={data.overall[a].reviews}
              written={overall?.per[a]?.n || 0}
              stars={data.overall[a].avg_stars}
              rows={rowsFor(a)}
              hot={hot}
              setHot={setHot}
            />
          ))}
        </div>
        <p className="ri-note">
          Star averages use every review in the window. Topic percentages use only written reviews of
          five or more words, which skew negative because people write more when something went wrong.
        </p>

        <GapChart apps={apps} rows={rows} hot={hot} setHot={setHot} />
        <Pipeline data={data} apps={apps} rows={rows} />

        <p className="ri-foot">
          Results reflect a sample of public user reviews, not the actual performance of any company.
          Topics are matched by keywords, so some reviews may be misclassified. This project is not
          affiliated with or endorsed by any company.
        </p>
      </div>
    </main>
  );
}