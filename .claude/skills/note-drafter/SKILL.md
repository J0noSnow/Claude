---
name: note-drafter
description: Use when the user wants Substack Notes and/or X posts drafted from their own material. That means ideas on the Eden Strategy or Plan board, an essay in the library, or a topic. Drafts are built on the structures of top-performing posts and filled with the user's real stories. Also use when the user wants posts that promote an essay, modeled on a named creator's promo notes.
---

# Note drafter

Turns the user's own material into Substack Notes and X posts that borrow the structure of posts that have already worked. The structure comes from research. The substance comes from the user's library, never from invention.

## 1. Pick the mode

| Mode | Source of ideas | Research target |
|---|---|---|
| Ideas | Plan board "Idea" column (`eden_get_plan`, stage `idea`) or Strategy angles (`eden_get_strategy`). The Plan board is what "ideas" usually means. Strategy angles are the fallback. | Top posts on the idea's topic |
| Essay promo | One essay the user names (`eden_search_workspace_items` then `eden_get_note_markdown`) | A named creator's promo notes |
| Topic | A topic the user types | Top posts on the topic |

If it's unclear whether "ideas" means the Plan cards or the Strategy angles, check the Plan board first and say which you used.

## 2. Gather the user's material
- Read every source idea or essay in full.
- Search the library for each theme (`eden_search_workspace_items`, substring on titles, so try several words). Read the journals, essays, and notes that match.
- Read the voice profile note ("The Wandering Philosopher voice profile") and follow it. Key rules: you-address, concrete images, confession then reframe, dry humor, no em dashes, no guru framing, none of the AI-tell words it lists.
- Check the user's own top notes (`eden_search_social_content`, creator scope) so the drafts don't repeat what already performed.

## 3. Research the structures
- **Ideas / Topic mode:** `eden_search_social_content`, scope `global`, `platforms: ["substack","twitter"]`, a query per topic, `minOutlierScore` 10 to 30, `orderBy: outlier`. Read the full body of the best ones with `eden_read_social_post` (set `attemptLiveFetch: false`).
- **Essay promo mode:** `eden_resolve_creator`, then `eden_search_social_content` with scope `creator`, ordered by outlier and by recent. Read the promo notes in full, since previews cut off the restacked-essay line. Compare the same format across months.
- Large results are saved to a file. Parse them with `python3 -I` and print only the fields you need (type, likes, outlier, URL, first 400 characters).
- Name the structure of each top post: the hook, the line shape, the ending, and the length. Note its outlier score and likes.

Caveats to state in the output:
- One search page is not a ranking.
- Small accounts can have inflated outlier scores. Say so.
- A format that repeats can decay. Check the trend before copying it.

## 4. Map and draft
- One draft per idea unless the user asks for more. Give each draft a different structure so a batch doesn't read as repeats.
- Each draft names its template (creator, outlier score), the Eden notes it draws on, a Substack version, and an X version (280 characters max).
- Substack: short (under about 70 words), first line a complete claim, one idea, no link or pitch unless it's a promo.
- X: the sharpest single line, a reversal, or a named cost. Pure encouragement is saturated, so name the cost where honest.
- Facts come from the library. If a line is inferred and not stated by the user, flag it in the notes. Never invent studies, numbers, or events.
- For promo mode, keep the structure and change the words: a feeling-as-fact hook, a concrete number, a soft ask, reply bait, and the essay attached as a card. If the essay's title hides a phrase, keep it hidden in at least one post.
- Check time-sensitive wording against today's date (counts of days left, "this month").

## 5. Deliver
- Write a markdown file under `drafts/` in the working directory.
- The user cannot open files in the cloud container. Also publish a page with copy buttons (Artifact) and send the file (`SendUserFile`). Don't point at a path alone.
- Lead the reply with the link, then a short summary: the structures used, the gaps, anything to check before posting.
- End with 2 or 3 pointed questions that challenge the user's assumptions (which draft they'd actually post and why, whether a claim is true to them).

## 6. Writing back to Eden
Only on the user's ask:
- `eden_update_plan` can append a note to a card, move its stage, and set its format. It never deletes and never edits existing notes, so finalize the text first.
- Put the Substack text in the card notes with a heading line the user can delete. Keep each card's original text, pillar, topic, and angle.
- If cards were deleted by hand, recreate them with their original text and metadata, and say which ones were recreated and which could not be.
- Save notes to the library only when asked.

## Pitfalls seen
- Reading "ideas" as Strategy angles when the user meant the Plan cards.
- Previews hide the end of a promo note. Read the full body.
- Re-using the user's already-posted notes as new ideas.
- Promo notes about craft underperform promos about the reader's inner life.
- Leaving the drafts only in a container file the user can't open.
