// Holt den aktuellen Kurs von Euro zu einer anderen Währung.
// In der Sandbox braucht das eine Netzwerk-Regel:  sbx policy allow network api.frankfurter.app
export async function getRate(to) {
  const url = `https://api.frankfurter.app/latest?from=EUR&to=${encodeURIComponent(to)}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data.rates[to];
}
