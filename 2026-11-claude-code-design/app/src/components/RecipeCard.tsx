import type { Recipe } from "../data";
import { colors } from "../styles/colors";

// Vorhandene Komponente: im Brief mit Namen nennen, damit Claude sie benutzt.
export function RecipeCard({ recipe }: { recipe: Recipe }) {
  return (
    <article style={{ background: colors.card, borderRadius: 18, padding: 16, display: "flex", gap: 16, alignItems: "center" }}>
      <div style={{ width: 96, height: 96, borderRadius: 14, background: colors.photo }} />
      <div>
        <h3 style={{ margin: 0, color: colors.text }}>{recipe.title}</h3>
        <p style={{ margin: "6px 0", color: colors.muted }}>{recipe.minutes} min</p>
        <button style={{ background: colors.primary, color: "#fff", border: 0, borderRadius: 12, padding: "10px 16px", fontWeight: 700 }}>
          Rezept speichern
        </button>
      </div>
    </article>
  );
}
