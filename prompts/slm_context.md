You are helping review a transcript from a Singapore community support conversation.

Categorise the transcript into exactly these five segments:
- Health
- Social
- Financial
- WMTY
- Others

Definitions:
- Health: medical needs, mobility, caregiving, mental wellbeing, appointments, medication, disability, nutrition, safety at home.
- Social: family, friends, loneliness, community participation, activities, social support, living arrangements.
- Financial: employment, CPF, income, expenses, benefits, payouts, insurance, housing costs, debt, affordability.
- WMTY: "What Matters To You"; personal goals, hopes, values, preferences, fears, priorities, meaningful activities.
- Others: relevant information that does not fit the four categories above.

Return valid JSON only. Do not include markdown.

The JSON must use this exact shape:
{
  "Health": [
    {
      "summary": "short plain-English point",
      "evidence": ["short transcript evidence or paraphrase"]
    }
  ],
  "Social": [],
  "Financial": [],
  "WMTY": [],
  "Others": []
}

Use empty arrays when there is no useful information for a category.
Keep summaries concise. Do not invent facts that are not in the transcript.

Transcript:
{{TRANSCRIPT}}
