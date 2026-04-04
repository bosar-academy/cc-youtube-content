---
name: generate-title
description: Analyze top-performing YouTube titles and generate optimized, high-CTR video titles that work synergistically with thumbnails. Use when the user asks to create a title, name a video, optimize a title, or brainstorm video titles.
argument-hint: [topic-or-script-path]
disable-model-invocation: true
---

# YouTube Title Generator

Analyze outlier titles from competitor research, apply proven CTR formulas, and generate 3 optimized titles that are clickable AND honest. Every title must work as a unit with the thumbnail — they tell one story together.

## Core Principle

**High CTR + High Retention = Algorithm Love. High CTR + Low Retention = Algorithm Punishment.**

Every title must pass the alignment test: "If someone clicks this title, will they feel satisfied after watching?" If no — rewrite it.

## Inputs

Ask the user for any missing information:

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| Topic | Yes | — | Video topic |
| Research brief | No | — | Path to research-brief.md (contains competitor title data) |
| Script | No | — | Path to script.md (for content-alignment check) |
| Thumbnail concepts | No | — | Brief description of thumbnail ideas (for synergy) |

## Prerequisites

If a research brief exists, read it first — it contains competitor titles with view counts.
If a script exists, read it — titles must accurately reflect what's in the video.

## Process

### Step 1: Analyze outlier titles from research

Read the research brief and extract all competitor titles with view counts. Identify **outliers** — titles that got significantly more views than the channel average or the topic average.

For each outlier title, analyze:
- **Structure**: What formula does it use? (list, challenge, story, bold claim, how-to)
- **Power words**: Which trigger words are present?
- **Specificity**: Does it use numbers, timeframes, dollar amounts?
- **Curiosity gap**: What question does it plant in the viewer's mind?
- **Voice**: Active or passive? First person ("I") or second person ("You")?
- **Length**: Character count, where does truncation hit?
- **Thumbnail synergy**: What thumbnail would naturally pair with this title?

Create a pattern table:

```markdown
## Outlier Title Analysis

| Title | Views | Formula | Power Words | Curiosity Gap | Why It Works |
|-------|-------|---------|-------------|---------------|-------------|
| ... | ... | ... | ... | ... | ... |
```

### Step 2: Extract winning patterns

From the analysis, identify the top 3-4 patterns that consistently outperform. These become the "formula bank" for title generation.

Common winning patterns in AI/tech/business:
1. **"I [verb] [impressive result]"** — Personal story with proof ("I Replaced My Entire Stack")
2. **"[Number] [Timeframe] of [Topic] in [Shorter Time]"** — Compression promise ("6 Months in 27 Min")
3. **"The [Framework/Method] to [Desirable Outcome]"** — Methodology promise
4. **"Why I [Controversial Action] (and What I Use Instead)"** — Pattern interrupt + curiosity
5. **"[Topic] for [Audience]: [Bold Promise]"** — Audience targeting + value
6. **"How [Specific Person/I] [Achievement] with [Tool]"** — Case study format
7. **"[Number] Ways to [Outcome] (That Actually Work)"** — List with credibility qualifier

### Step 3: Generate 3 title options

For each title, apply this checklist:

**Structure rules:**
- [ ] 70-100 characters total
- [ ] First 40 characters work standalone (mobile truncation)
- [ ] Active voice, simple words (MrBeast test: "Can anyone understand this?")
- [ ] Contains at least one specific number OR timeframe
- [ ] Primary keyword in first 50 characters
- [ ] At least one power word (but not overloaded)

**Power words to use strategically** (pick 1-2, never more):
- Curiosity: Secret, Hidden, Real, Actually, Truth
- Authority: Complete, Proven, Framework, System
- Urgency: Now, Today, 2026, Just, Finally
- Value: Free, Entire, Every, All
- Emotion: Changed, Replaced, Killed, Built, Destroyed

**Curiosity gap rules:**
- Create an information gap the viewer MUST close
- The gap must be closable by watching — not misleading
- Best gaps: "I did X" (viewer wants to know the result), "Why I stopped X" (viewer wants to know why), "X that nobody talks about" (viewer wants to be in the know)

**Content alignment rules:**
- Title must describe something that actually happens in the video
- If the title says "framework" — the video must teach a framework
- If the title says a number — the video must deliver that many items
- If the title implies a transformation — the video must show before/after
- **Test**: Read the title, then read the script outline. Does the script deliver on the title's promise? If not, adjust the title to match what the script actually delivers.

**Thumbnail synergy rules:**
- Title and thumbnail must tell ONE story together
- They should COMPLEMENT, not duplicate — don't repeat the same words
- If thumbnail shows your face with shocked expression → title explains what's shocking
- If thumbnail shows before/after → title names the transformation
- If thumbnail has a tool logo (Claude Code) → title explains the outcome, not the tool

### Step 4: Score each title

Rate each title 1-10 on these dimensions:

| Dimension | Weight | Question |
|-----------|--------|----------|
| **Clickability** | 25% | Would you click this in a feed of 20 thumbnails? |
| **Clarity** | 20% | In 2 seconds, do you know what the video is about? |
| **Content alignment** | 25% | Does the script actually deliver on this promise? |
| **Thumbnail synergy** | 15% | Does this pair naturally with a strong thumbnail concept? |
| **Uniqueness** | 15% | Does this stand out from the competitor titles analyzed? |

### Step 5: Present with thumbnail pairing

For each title, suggest the thumbnail concept it pairs with:

```markdown
## Title Option 1: "[Title Here]"
- Characters: [count]
- Formula: [which pattern]
- Score: [X/10]
- Thumbnail pairing: [2-sentence description of the ideal thumbnail]
- Why it works: [1 sentence]
- Risk: [potential weakness]
```

## Output Format

Save to the same directory as the script/research brief:

```
./[video-slug]/titles.md
```

```markdown
# Title Options: [Topic]

**Generated**: [date]
**Based on**: [research brief / script / topic]

---

## Outlier Analysis

| Title | Views | Formula | Why It Works |
|-------|-------|---------|-------------|
| ... | ... | ... | ... |

### Winning Patterns Identified
1. [Pattern + evidence]
2. [Pattern + evidence]
3. [Pattern + evidence]

---

## Title Option 1 (Recommended)

**"[Title Here]"**

- Characters: [count] (first 40: "[truncated version]")
- Formula: [pattern used]
- Power words: [which ones]
- Curiosity gap: [what question it plants]
- Content alignment: [how the script delivers on this]
- Thumbnail pairing: [ideal thumbnail concept — 2 sentences]
- Score: [X/10] (Clickability: X, Clarity: X, Alignment: X, Synergy: X, Unique: X)

---

## Title Option 2

**"[Title Here]"**

[Same structure as above]

---

## Title Option 3

**"[Title Here]"**

[Same structure as above]

---

## Recommendation

**Go with Option [X]** because [1-2 sentence reasoning tied to the research data].

Thumbnail brief for the winning title: [3-4 sentence description that can feed into /generate-thumbnails]
```

## Anti-Clickbait Guardrails

NEVER generate titles that:
- Promise "secrets" or "hacks" without delivering specific, actionable content
- Use extreme superlatives ("BEST EVER", "MOST AMAZING") without evidence
- Imply false scarcity or urgency ("Before It's Too Late!") for evergreen content
- Bait-and-switch: promise one topic, deliver another
- Use ALL CAPS for more than 2 words
- Promise results the viewer can't realistically achieve from watching

ALWAYS ensure:
- The script/content ACTUALLY delivers what the title promises
- The curiosity gap is resolved within the video
- The title would still work if the viewer has already watched (no regret)
- A viewer who watches to 50% would still feel the title was honest

## Red Flag Test

Before finalizing, run this mental test for each title:

> "If 1,000 people click this title, watch the video, and then see the title again — would most of them think 'yeah, that was accurate' or 'that was misleading'?"

If the answer is "misleading" for even 20% of viewers — rewrite.
