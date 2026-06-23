---
name: script-to-teleprompter
description: Convert a YouTube script to a teleprompter-only version (spoken text only, no production notes, slide cues, demo pointers, or markers), save it next to the original script, and upload to Google Drive as a Google Doc. Trigger when the user says "upload this script as a teleprompter version", "make a teleprompter version", "for my teleprompter", "teleprompter version of this script", "now let's upload this script as a teleprompter version", "convert to teleprompter", or similar.
argument-hint: [optional-path-to-script.md]
disable-model-invocation: true
---

# Script to Teleprompter Converter

Convert a full production script into a clean teleprompter version (spoken text only) and upload it to Google Drive.

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| Source script path | No | The most recently discussed script in the current conversation, or the most recently modified `script.md` under your content scripts folder if no context exists | Path to the production script to convert |

If unclear which script the user means, ask them to clarify with the folder name or full path.

## What to extract (KEEP)

- The cold-open hook lines you say to camera
- All `[ON-CAM]` and `[VO over slide]` text content (the words themselves, NOT the markers)
- Pull quotes you read aloud
- Old rule / New rule labels and their explanatory sentences (these are spoken with slide reads)
- Pre-demo skill explanations and post-demo wrap-up commentary
- All on-camera framing language ("So today I'm going to do three things...", "Quick context if you're new here...", etc.)

## What to strip (DELETE entirely)

- YAML/markdown frontmatter at top of script (Lane, Length target, Authority, etc.)
- "Working titles" section
- "Visual cue legend" section
- All bracketed cue markers: `[ON-CAM]`, `[B-ROLL]`, `[SCREEN]`, `[SLIDE: ...]`, `[CHAPTER: ...]`, `[QUOTE]`, `[VO over slide]`, `[VO/ON-CAM]`, `[VO]`
- All `[SCREEN RECORDING: ...]` placeholder blocks
- All "**Live demo pointers (capture in the recording, comment on during):**" sections and their bullet lists
- All beat headers like `## BEAT X: TITLE (10:30 - 14:00)`
- Everything after `# PRODUCTION NOTES` (demo checklist, motion slides list, chapters, description draft, hooks to test, word count, tone rules applied)
- Inline production notes within beats (Demo recording checklist references, B-roll cues, etc.)

## Output structure

Replace beat headers with navigation section markers in this format: `### [SECTION NAME IN CAPS]`. The bracketed-caps style signals "this is navigation, not teleprompter content" so you can scroll to find your place between takes.

Standard section progression (use whichever beats actually exist in the source):

1. `### [INTRO]` - cold open hook + 3-part promise
2. `### [CONTEXT + WHAT ANTHROPIC SHIPPED]` (or similar context section) - re-intro + what the announcement is
3. `### [SKILLS AND PLUGINS PRIMER]` if present
4. `### [THE 7 CONNECTORS]` (or whatever the breakdown section is)
5. `### [THE FLAGSHIP WORKFLOWS]` if present
6. `### [DEMO 1: NAME — SETUP]` - everything said BEFORE the screen recording
7. `### [• • • DEMO 1 SCREEN RECORDING PLAYS • • •]` - visual break, no text
8. `### [DEMO 1: NAME — WRAP]` - post-demo commentary
9. Repeat 6-8 for additional demos
10. `### [BEYOND THE 7 CONNECTORS]` or equivalent
11. `### [WHAT THIS CHANGES]` or equivalent reflection beat
12. `### [OUTRO]` - soft CTA + comment prompt + subscribe + close

Sections are separated by `---` horizontal rules.

## File handling

1. **Source identification**: If the user references a script we just worked on, use that path. Otherwise check the conversation context. If still unclear, ask: "Which script - point me at the folder or full path?"

2. **Output file**: Save to `script-teleprompter.md` in the same folder as the source `script.md`. Overwrite if it exists (this is a regeneration, not a versioned save).

3. **Upload**: Use the gdrive-upload skill's formatted uploader:
   ```bash
   python3 ~/.claude/skills/gdrive-upload/upload_formatted.py --file [path-to-script-teleprompter.md] --title "[Video title] - TELEPROMPTER (spoken only)"
   ```

   Title format: derive from the source script's H1 or folder name. Append " - TELEPROMPTER (spoken only)" to make the version obvious in your Drive.

4. **Return the link**: Print the Google Doc URL the upload script returns. That's the main deliverable.

## Quality rules

- **Spoken text only.** If you wouldn't say it aloud on camera, it doesn't belong in the teleprompter.
- **No staccato fragments in a row** ("two words. two words. two words."). Carry over from the source script - if the source has staccato, fix it on the way through. See the write-script skill for the full tone rules.
- **Demo breaks must be visually obvious.** Use the `• • •` dot pattern inside the bracketed header so you can spot the demo points instantly when scrolling.
- **No em dashes anywhere.** Use regular dashes (-) or rewrite. Keep this consistent across all your content.
- **Preserve the section flow.** Don't reorder beats or combine sections - just strip.

## Process

1. Read the source script file.
2. Walk it top to bottom. For each chunk:
   - If it's a marker, header, or production note - drop it.
   - If it's spoken text - keep it, append it to the current navigation section.
   - When you hit a beat boundary, start a new section with the matching `[CAPS BRACKETED]` header.
3. For demo sections, split into SETUP (pre-demo) and WRAP (post-demo) blocks, separated by a visual `• • • DEMO X SCREEN RECORDING PLAYS • • •` break.
4. Write the assembled teleprompter to `script-teleprompter.md` in the source folder.
5. Run the gdrive-upload command. Return the URL.

## Example trigger phrases (any of these should activate this skill)

- "Now let's upload this script as a teleprompter version"
- "Upload this for my teleprompter"
- "Make a teleprompter version"
- "Teleprompter version of this script"
- "Convert this to teleprompter"
- "Strip the production notes and upload for teleprompter"
- "Give me a teleprompter version of [script name]"
