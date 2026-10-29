---
name: journal-to-eden
description: Transcribe photos of handwritten journal pages into faithful, neatly formatted text, review it with the user, then save each entry as a document in their Eden Library. Use when the user shares journal photos, handwritten pages, or asks to scan, transcribe or upload journal entries to Eden.
---

# Journal → Eden

Pipeline: **journal → photo → Claude → Eden** (→ Substack later, with light editing by the user).

## 1. Order the pages

- Sort photos by the printed page number, not by attachment order. Say so if the order differs.
- If a page number is hidden or unreadable, work out the order from the content: sentences that continue across pages, the date line, and the mirror-image text showing through from the back of the page. Explain how you worked it out. If the order is still unclear, flag it and ask.
- Photos may be rotated. Read them in the page's own orientation.
- Group pages into entries. A new entry starts at a date line (e.g. "Wed 29th July") or a new heading.
- Short notes that follow an entry without their own date (e.g. "Bones", "Obsessions") belong to the entry before them. Ask if unsure.

## 2. What to transcribe

- Only text inside the page's own boundaries. Treat each page as a single page.
- **Exception: drawn connectors.** If the user draws a line or arrow carrying one idea across the fold onto the facing page, follow it. Join the continued text to where the line starts, and say that you did.
- Keep the user's own marks (arrows, symbols, `#1`) where they're written. Don't re-link or merge them into an interpretation without asking.
- Start at the entry's date line. **Ignore anything above the date line** (the tail of the previous entry).
- Ignore the facing page, text bleeding through from the other side, and anything outside the page edges.
- If a sentence is cut off at the top or bottom of a photo, mark it `[cut off]` and ask for the neighbouring page.

## 3. How to transcribe

Keep the messiness and format it neatly:

- **Verbatim.** Keep the user's wording, grammar, misspellings, capitals, swearing and repeated words. Don't correct anything.
- **Crossed-out words:** `~~word~~` when readable, `~~[crossed out]~~` when not.
- **Unclear words:** `[word?]`, or `[option a? option b?]` for two readings. Unreadable: `[illegible]`. Words running off the page: `permiss[ion – runs off page]`.
- **Layout:** join wrapped lines into paragraphs, keep the user's paragraph breaks, drop page numbers.
- **Structure:** a `###` heading for the entry's own title (if written), the date in bold, and `→` for arrows.
- **Drawings and diagrams** (funnels, flows, mind maps): redraw as ASCII art inside a fenced code block, using `\ / | _ -` and `<-` for annotations. Check that the columns line up.

## 4. Dates

- Use the date as written. If the year is missing, work it out from the weekday (e.g. Wed 29 July is 2026) and state the assumption.
- If the weekday and date don't match any recent year, ask for the year.

## 5. Review before upload (required)

Paste each transcription into the chat, then list under it:

- uncertain words and the gaps that matter
- the assumed date and year
- the proposed title

**Confirm each entry separately and don't upload until the user approves.** Apply their corrections. When they fill in a gap, remove the `?` marker. Leave every other marker as it is unless they say otherwise.

## 6. Upload to Eden

- Tool: `eden_create_note` (load it with ToolSearch if needed), with `destination: {"kind": "library"}` and `presentation: "document"`.
- **Title:** always `Journal – <date> – <summarised title>`, e.g. `Journal – Thursday 29th Oct 2026 – Back to "You Are an Artist"`. Use the entry's own title as the summarised title if it has one, otherwise write a short summary of the entry. Use the user's title if they give one.
- **Body:** `# <title>`, then the bold date line, then the entry. Put no blank lines between blocks (Eden adds the spacing), except inside code blocks.
- Don't add the note to a board unless asked.
- After uploading, say it's in **AI drafts** and that Eden archives untouched drafts after 30 days unless the user edits, keeps, or adds them to a board.

## Tips to pass on when photos are hard to read

- Shoot each page flat and from directly above, in even light.
- Include the bottom of the page before and the top of the page after, so sentences that cross pages are complete.
- Write the year in the date line.
