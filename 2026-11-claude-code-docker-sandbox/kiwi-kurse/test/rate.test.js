import test from "node:test";
import assert from "node:assert/strict";
import { getRate } from "../src/rate.js";

// Dieser Test braucht Netz: ohne Freigabe von api.frankfurter.app schlägt er in der Sandbox mit einem Verbindungsfehler fehl.
test("EUR -> USD liefert eine positive Zahl", async () => {
  const rate = await getRate("USD");
  assert.equal(typeof rate, "number");
  assert.ok(rate > 0);
});
