import express from "express";
import { getRate } from "./rate.js";

const app = express();

app.get("/", (req, res) => {
  res.send("Kiwi Kurse");
});

// Endpunkt aus dem Video: GET /rate/USD -> aktueller Kurs EUR -> USD
app.get("/rate/:to", async (req, res) => {
  try {
    res.json({ from: "EUR", to: req.params.to, rate: await getRate(req.params.to) });
  } catch (err) {
    res.status(502).json({ error: String(err) });
  }
});

app.listen(3000, () => console.log("http://localhost:3000"));
