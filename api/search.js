const { Configuration, OpenAIApi } = require("openai");

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});

const openai = new OpenAIApi(configuration);

module.exports = async (req, res) => {
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
    const completion = await openai.createChatCompletion({
      model: "gpt-4",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.7,
    });

    const responseText = completion.data.choices[0].message.content;

    let results;
    try {
      results = JSON.parse(responseText);
    } catch (e) {
      console.error("Fallback to eval due to JSON.parse error");
      results = eval(responseText); // fallback
    }

    res.status(200).json({ results });
  } catch (err) {
    console.error("OpenAI error:", err.message);
    res.status(500).json({
      error: "Failed to generate results",
      detail: err.message,
    });
  }
};
