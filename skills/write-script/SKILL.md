---
name: write-script
description: Write a full YouTube video script with hooks, curiosity gaps, open loops, and retention markers. Use when the user asks to write a script, create video content, draft a video, or plan a YouTube video.
argument-hint: [topic-or-research-brief-path]
disable-model-invocation: true
---

# YouTube Script Writer

Write publish-ready YouTube scripts in your authentic voice. Produces a structured script with hooks, retention markers, B-roll cues, diagram cues, and a natural CTA.

## Setup Required

Before first use, create these files in your content workspace (set `$CONTENT_DIR` environment variable, or Claude will ask for the path):

1. **`$CONTENT_DIR/brand_voice.md`** - Your brand voice rules, visual branding, platform-specific adjustments. Define your tone, energy, language patterns, and what makes your content distinct.

2. **`$CONTENT_DIR/identity.md`** - Your background, communication style, story, and credibility markers. This tells the script writer WHO is speaking.

3. **`$CONTENT_DIR/script_references/`** - A folder with 1-3 of your real, published video scripts (or transcripts). These are the ground truth for your speaking style, pacing, hook patterns, and tone. Supported formats: `.md`, `.txt`, `.docx` (convert with `textutil -convert txt -stdout` if needed).

If any of these files are missing, Claude will ask you to provide them or skip that context.

## Inputs

Ask the user for any missing information:

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| Topic | Yes | — | Video topic or keyword (e.g., "Claude Code for business automation") |
| Research brief | No | — | Path to research-brief.md from `/research-brief` skill |
| Target length | No | 12 min | Estimated video length in minutes |
| Content pillar | No | auto-detect | One of: framework-adoption, build-business, tutorial, use-cases, behind-scenes |
| Audience | No | both | "business-owners", "builders", or "both" |

## Prerequisites

Before writing, read these files for voice and context (set `$CONTENT_DIR` env var or ask the user for their content workspace path):

1. `$CONTENT_DIR/identity.md` - Communication style, story, background
2. `$CONTENT_DIR/brand_voice.md` - Brand voice rules, visual branding, platform-specific adjustments
3. `$CONTENT_DIR/script_references/` - **CRITICAL: Real scripts from the creator's published videos. This is the ground truth for speaking style, pacing, hook patterns, credibility stacking, and tone. Study these before writing ANY script.** Convert `.docx` files with: `textutil -convert txt -stdout "filename.docx"`
4. Research brief (if provided) - Competitor analysis, gaps, recommended angles

If `$CONTENT_DIR` is not set, ask the user: "Where is your content workspace? (e.g., ~/Projects/content)"

### Script Reference Analysis

After reading the script references, extract and note these patterns before writing:

- **Hook patterns**: How does the creator open videos? (bold claims, stories, questions, pattern interrupts)
- **Credibility stacking**: What proof points do they use? (revenue, experience, results)
- **Structure**: How do they organize content? (concept -> demo -> recap, step-by-step, etc.)
- **Pacing**: Conversational? Academic? High-energy? How do they handle jargon?
- **Re-hook patterns**: What phrases do they use to maintain retention?
- **CTA style**: How do they bridge to calls-to-action? Natural or direct?

## Voice Guide

Derive the voice from the creator's `identity.md` and `brand_voice.md` files. Every script MUST match the creator's authentic voice. General principles:

- **Match the creator's energy level** - study their reference scripts for tone
- **Use their vocabulary and phrasing patterns** - don't introduce language they wouldn't use
- **Mirror their teaching style** - some creators explain step-by-step, others tell stories first
- **Respect their positioning** - use their frameworks and terminology, not competitors'
- **Match their natural speech patterns** - sentence length, use of fragments, filler phrases

## Process

### Step 1: Determine the video slug

Create a kebab-case slug from the topic (e.g., "claude-code-business-automation"). Create the output directory:

```bash
mkdir -p ./[video-slug]/
```

### Step 2: Read context files

Read the three files listed in Prerequisites. Extract:
- Voice patterns and phrasing style
- Current content pillars and strategy
- If research brief exists: competitor gaps, recommended angle, hook ideas

### Step 3: Generate 4 hook options

Write 4 distinct hooks (each 15-30 seconds when spoken):

| Hook Type | Pattern | Example Opening |
|-----------|---------|-----------------|
| **Pattern Interrupt** | Start with something unexpected that breaks the scroll | "I just deleted every automation tool I've used for the last 3 years." |
| **Bold Claim** | Make a specific, provable claim | "I replaced a $2,000/month tech stack with one tool — and it took me 45 minutes." |
| **Story** | Start with a mini personal story | "Last week, a client asked me to build something that should've taken 2 months..." |
| **Question** | Pose a question that creates a curiosity gap | "What if I told you that the $50B automation industry is about to become irrelevant?" |

Each hook must:
- Create immediate curiosity (why should I keep watching?)
- Plant an open loop that gets resolved later in the video
- Feel authentic to the creator's voice (not clickbait-y, but genuinely compelling)

### Step 4: Build the outline with retention architecture

Structure the video with built-in retention mechanics:

```
[0:00 - 0:30]  HOOK — Pattern interrupt + open loop
[0:30 - 2:00]  PROBLEM — What's broken / the opportunity most people miss
[2:00 - 3:00]  AGITATE — Why existing solutions fail + RE-HOOK #1
[3:00 - 6:00]  SOLUTION — Your framework/method introduction + RE-HOOK #2
[6:00 - 10:00] PROOF — Live demo / case study / behind-the-scenes + RE-HOOK #3
[10:00 - 12:00] IMPLEMENTATION — Step-by-step what to do next
[12:00 - 13:00] CTA — Subscribe + natural your offer/product bridge
```

**Retention rules:**
- **RE-HOOK every 2-3 minutes** — tease what's coming ("But the real game-changer is what I'm about to show you...")
- **Open loops** — introduce a concept early, resolve it later ("I'll show you exactly how in a minute")
- **Curiosity gaps** — create information asymmetry ("There's one thing that makes this 10x more powerful...")
- **Pattern breaks** — change energy, pace, or visual every 2-3 minutes

### Step 5: Write the full script

Write the complete script with these markers embedded:

| Marker | Purpose | Example |
|--------|---------|---------|
| `[TIMESTAMP X:XX]` | Section timing | `[TIMESTAMP 0:00]` |
| `[B-ROLL: description]` | Visual insert cue | `[B-ROLL: Quick montage of n8n, Zapier, Make dashboards]` |
| `[SCREEN: description]` | Screen recording cue | `[SCREEN: Show Claude Code terminal with the command running]` |
| `[DIAGRAM: concept-name]` | Excalidraw diagram cue (feeds /generate-diagrams) | `[DIAGRAM: ai-first-framework-overview]` |
| `[RE-HOOK]` | Retention re-hook point | `[RE-HOOK: "But here's where it gets really interesting..."]` |
| `[CTA]` | Call-to-action marker | `[CTA: Subscribe + your offer/product mention]` |
| `[PAUSE]` | Dramatic pause for emphasis | `[PAUSE — let that sink in]` |
| `[ENERGY: up/down]` | Energy shift cue | `[ENERGY: up — get excited here]` |

**Writing rules:**
- Write as spoken word, not essay. Short sentences. Fragments are fine.
- Use "you" and "I" — direct address
- Include filler phrases naturally ("Look,", "Here's the thing,", "And honestly,")
- No jargon without immediate explanation
- Every section must earn the next 2 minutes of attention
- The CTA to your offer/product must feel like a natural next step, never forced

### Step 6: Generate the diagram request list

Extract all `[DIAGRAM: name]` markers from the script and create a structured list:

```markdown
## Diagram Requests (for /generate-diagrams)
1. **framework-overview** — High-level view of your framework/method: inputs, process, outputs.
2. **before-after-workflow** — Side-by-side: "Before" (5 tools, complex) vs "After" (1 tool, simple). Red vs green.
3. **cost-comparison** — Bar chart style: old stack costs vs AI-first costs per month.
```

### Step 7: Generate the B-roll shot list

Extract all `[B-ROLL]` and `[SCREEN]` markers into a consolidated list:

```markdown
## B-Roll & Screen Recording Shot List
1. [0:05] B-ROLL: Quick montage of automation tool dashboards
2. [1:30] SCREEN: Show the problem scenario in real tool
3. [3:15] SCREEN: Claude Code terminal — first command
...
```

### Step 8: Save outputs

Save the complete script to:
```
./[video-slug]/script.md
```

## Output Format

The final `script.md` should follow this structure:

```markdown
# [Video Title]

**Generated**: [date]
**Topic**: [topic]
**Target length**: [X] minutes
**Content pillar**: [pillar]
**Audience**: [audience]

---

## Hook Options

### Option A: Pattern Interrupt
[Full hook text, 15-30s spoken]

### Option B: Bold Claim
[Full hook text, 15-30s spoken]

### Option C: Story
[Full hook text, 15-30s spoken]

### Option D: Question
[Full hook text, 15-30s spoken]

**Recommended**: Option [X] — [1-line reason]

---

## Full Script

### [TIMESTAMP 0:00] HOOK
[ENERGY: up]

[Hook text — using recommended option]

[B-ROLL: description]

---

### [TIMESTAMP 0:30] THE PROBLEM

[Script text...]

[SCREEN: description]

---

### [TIMESTAMP 2:00] AGITATE

[RE-HOOK: "But here's what most people don't realize..."]

[Script text...]

---

### [TIMESTAMP 3:00] THE SOLUTION

[DIAGRAM: framework-overview]

[Script text...]

[RE-HOOK: "And I'm about to show you exactly how this works..."]

---

### [TIMESTAMP 6:00] PROOF — LIVE DEMO

[SCREEN: description]

[Script text with step-by-step narration...]

[RE-HOOK: "Now here's the part that really blew my mind..."]

---

### [TIMESTAMP 10:00] YOUR NEXT STEPS

[Script text — actionable implementation steps...]

---

### [TIMESTAMP 12:00] CTA

[CTA: Subscribe]

[Natural bridge to your offer/product — "If you want to go deeper..."]

---

## Diagram Requests
[Numbered list with name + description for each]

## B-Roll & Screen Recording Shot List
[Numbered list with timestamp + description for each]
```

## Content Pillar Reference

Match the script angle to one of these pillars:

| Pillar | Angle | Example Topics |
|--------|-------|----------------|
| **Framework Adoption** | How to transform YOUR business | "Replace your entire automation stack with Claude Code" |
| **Build a Business** | How to monetize the opportunity | "Start an AI-first agency in 2026" |
| **Tutorial** | Hands-on implementation | "Build a lead gen system with Claude Code in 30 minutes" |
| **Use Cases & Niches** | Where the opportunity lies | "5 industries desperate for AI-first solutions" |
| **Behind the Scenes** | How I'm building with AI-first | "I rebuilt my entire business in one week — here's what happened" |

## CTA Bridge Templates

Use one of these natural transitions for the CTA (never sound salesy). Adapt the product/offer name to match the creator's actual offering (from `brand_voice.md` or `identity.md`):

1. **The "Go Deeper" bridge**: "Everything I showed you today? That's just the surface. Inside [product], we build the complete system from scratch - and you walk out with a working [result]."
2. **The "Shortcut" bridge**: "You could figure all of this out on your own - it took me months. Or you could join the next [product] cohort and have it built in [timeframe]."
3. **The "Proof" bridge**: "This is exactly what our [product] students build in Module [X]. If you want the full playbook, link's in the description."
4. **The "Community" bridge**: "The hardest part of [topic] isn't the [skill] - it's doing it alone. That's why we built [product] as a cohort..."

If the creator doesn't have a product to promote, use a simple subscribe + next video CTA instead.
