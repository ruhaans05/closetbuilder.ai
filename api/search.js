import { OpenAI } from "openai";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const data = req.body;

  const prompt = `
You're a fashion shopping assistant. Based on this user's preferences:

- Shirt Size: ${data.shirtSize}
- Gender: ${data.gender}
- Country: ${data.country}
- Shopping Preference: ${data.channel}
- Price Range: $${data.minPrice} to $${data.maxPrice}
- Query: ${data.query}

Find 20 clothing items available online that match these filters.
Each item must include:
- name
- size
- price
- link (real product link)

If fewer than 20 are found, fill in the rest with similar items. Return as JSON:
[{"name": "...", "size": "...", "price": ..., "link": "..."}, ...]
`;

  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.7
    });

    const raw = completion.choices[0].message.content;

    // try to safely parse LLM output
    const results = JSON.parse(raw);
    res.status(200).json({ results });
  } catch (err) {
    console.error("OpenAI error:", err);
    res.status(500).json({
      error: "Failed to generate results",
      detail: err.message
    });
  }
}
