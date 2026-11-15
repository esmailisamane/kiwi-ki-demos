import { recipes } from "../data";

// Startzustand aus dem Video: nur eine graue Liste.
// Probiere in Claude Code: /design Startseite für Hobbyköche ... (siehe BRIEF_VORLAGE.md)
export default function Home() {
  return (
    <main style={{ fontFamily: "sans-serif", padding: 24, color: "#555" }}>
      <h2>Alle Rezepte</h2>
      {recipes.map((r) => (
        <p key={r.id}>{r.title}</p>
      ))}
    </main>
  );
}
