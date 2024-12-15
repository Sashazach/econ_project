from openai import OpenAI
from interests import INTERESTS
client = OpenAI(api_key="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")

def analyzeAgreement(topic, compromise):
    completion = client.chat.completions.create(
        model="o1-mini",
        messages=[
            {"role": "user", "content": "You are an objective judge of compromises between parties."},
            {
                "role": "user",
                "content": f"""Here are the interests of each of the six teams regarding {topic}:
**Team 1:**
- {INTERESTS[0]}

**Team 2:**
- {INTERESTS[1]}

**Team 3:**
- {INTERESTS[2]}

**Team 4:**
- {INTERESTS[3]}

**Team 5:**
- {INTERESTS[4]}

**Team 6:**
- {INTERESTS[5]}

**Agreed Compromise:**
- {compromise}

Based on the above information, assign points to each of the six teams according to how much they benefit from the agreed compromise. Output the points as a comma-separated list without any spaces or additional text. Points should add up to 20 every time."""
            }
        ]
    )
    print(completion.choices[0].message.content)
    return [int(i) for i in completion.choices[0].message.content.split(',')]

