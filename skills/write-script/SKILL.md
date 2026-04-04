---
name: write-script
description: Write a full YouTube video script with hooks, curiosity gaps, open loops, and retention markers. Use when the user asks to write a script, create video content, draft a video, or plan a YouTube video.
argument-hint: [topic-or-research-brief-path]
disable-model-invocation: true
---

# YouTube Script Writer

Write publish-ready YouTube scripts for the Bo Sar channel (AI-First Framework niche). Produces a structured script with hooks, retention markers, B-roll cues, diagram cues, and a natural CTA bridge to AIF Academy.

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

Before writing, read these files for voice and context:

1. `~/.claude/context/identity.md` — Communication style, story, background
2. `~/Projects/content/CLAUDE.md` — Brand voice, content pillars, channel strategy
3. `~/Projects/content/scripts/My final scripts references/Script reference.docx` — **CRITICAL: Real scripts from Bohdan's live YouTube videos (3 videos, ~34K words). This is the ground truth for his speaking style, pacing, hook patterns, credibility stacking, and tone. Study these before writing ANY script.** Convert with textutil if needed: `textutil -convert txt -stdout "Script reference.docx"`
4. `~/Projects/content/brand_voice.md` — Brand voice rules, visual branding, platform-specific adjustments
5. Research brief (if provided) — Competitor analysis, gaps, recommended angles

### Script Reference Analysis (from real videos)

The reference file contains 3 real video scripts. Key patterns to replicate:

**Video #1 (~20K words)** - Comprehensive Claude Code course. Long-form tutorial.
- Hook: Personal testimony + bold claim ("genuinely that addictive") + roadmap preview
- Credibility: "building AI businesses for 2 years, $400K in last year"
- Structure: Concept explanation in plain English -> live demo -> recap -> next concept
- Pacing: Conversational, explains jargon immediately, uses analogies ("the phone is Claude Code, Node.js is the charger")
- Re-hooks: "This is where it gets really powerful", "And honestly, this changed everything for me"

**Video #2 (~6.5K words)** - "I run 3 businesses, 80% handled by AI" - Framework overview.
- Hook: Bold claim + disbelief framing ("most people don't believe me")
- Structure: 3-step framework (dive in -> build architecture -> scale with skills)
- Personal story: Shows actual tools (agency website, Gmail, dashboards) as proof
- Emotional resonance: "this was not possible 6 months ago, I can't hold it, I have to share this"
- CTA: Natural bridge to next video ("which I'll show you exactly how to do in the next video, subscribe")

**Video #3 (~8K words)** - LinkedIn outreach pipeline tutorial.
- Hook: Problem + specific opportunity ("LinkedIn has over a billion members") + contrarian take
- Structure: Shows full pipeline (5 steps), then builds each step live
- Credibility: "$36K/month in revenue with me personally doing outreach"
- Teaching style: "Some of you asked me to actually show the build process... knowing a skill exists is one thing, knowing how to build it yourself, that's where the real value is"
- Disclaimer section before execution (compliance awareness)

## Voice Guide

Every script MUST match this voice:

- **Enthusiastic but grounded** — showing real implementation, not hype
- **"Leading the way" energy** — pointing to the opportunity, inviting others in
- **"Wow" moments** — ChatGPT-moment-level reveals of what's possible
- **Direct and action-oriented** — doer energy, not academic
- **Simple, repeatable messaging** — every viewer should be able to explain the core idea to someone else
- **NOT copying Liam Otley** — our term is "AI-First Framework", NOT "AIOS"
- **Natural English** — conversational, slight accent-friendly phrasing (creator's second language is English)

## Process

### Step 1: Determine the video slug

Create a kebab-case slug from the topic (e.g., "claude-code-business-automation"). Create the output directory:

```bash
mkdir -p ~/Projects/content/scripts/[video-slug]/
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
- Feel authentic to Bo Sar's voice (not clickbait-y, but genuinely compelling)

### Step 4: Build the outline with retention architecture

Structure the video with built-in retention mechanics:

```
[0:00 - 0:30]  HOOK — Pattern interrupt + open loop
[0:30 - 2:00]  PROBLEM — What's broken / the opportunity most people miss
[2:00 - 3:00]  AGITATE — Why existing solutions fail + RE-HOOK #1
[3:00 - 6:00]  SOLUTION — AI-First Framework introduction + RE-HOOK #2
[6:00 - 10:00] PROOF — Live demo / case study / behind-the-scenes + RE-HOOK #3
[10:00 - 12:00] IMPLEMENTATION — Step-by-step what to do next
[12:00 - 13:00] CTA — Subscribe + natural AIF Academy bridge
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
| `[CTA]` | Call-to-action marker | `[CTA: Subscribe + AIF Academy mention]` |
| `[PAUSE]` | Dramatic pause for emphasis | `[PAUSE — let that sink in]` |
| `[ENERGY: up/down]` | Energy shift cue | `[ENERGY: up — get excited here]` |

**Writing rules:**
- Write as spoken word, not essay. Short sentences. Fragments are fine.
- Use "you" and "I" — direct address
- Include filler phrases naturally ("Look,", "Here's the thing,", "And honestly,")
- No jargon without immediate explanation
- Every section must earn the next 2 minutes of attention
- The CTA to AIF Academy must feel like a natural next step, never forced

### Step 6: Generate the diagram request list

Extract all `[DIAGRAM: name]` markers from the script and create a structured list:

```markdown
## Diagram Requests (for /generate-diagrams)
1. **ai-first-framework-overview** — High-level view of the AI-First Framework: inputs → Claude Code → outputs. Show the replacement of n8n/Zapier/Make.
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
~/Projects/content/scripts/[video-slug]/script.md
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

### [TIMESTAMP 3:00] THE SOLUTION: AI-FIRST FRAMEWORK

[DIAGRAM: ai-first-framework-overview]

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

[Natural bridge to AIF Academy — "If you want to go deeper..."]

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

## AIF Academy Bridge Templates

Use one of these natural transitions for the CTA (never sound salesy):

1. **The "Go Deeper" bridge**: "Everything I showed you today? That's just the surface. Inside AIF Academy, we build the complete system from scratch — and you walk out with a working product you can sell."
2. **The "Shortcut" bridge**: "You could figure all of this out on your own — it took me months. Or you could join the next AIF Academy cohort and have it built in 8 weeks."
3. **The "Proof" bridge**: "This is exactly what our AIF Academy students build in Module [X]. If you want the full playbook, link's in the description."
4. **The "Community" bridge**: "The hardest part of going AI-first isn't the tech — it's doing it alone. That's why we built AIF Academy as a cohort..."
