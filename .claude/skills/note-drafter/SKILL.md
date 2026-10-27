---
name: note-drafter
description: Use when the user wants Substack Notes and X posts drafted from the ideas in their Eden Strategy (pillar, topic and angle ideas) or Plan board cards. Each draft borrows the structure of a top-performing post and is filled with the user's own stories from the library. Not for promoting essays, newsletters or products.
---

# Note drafter

Turns ideas from the user's Eden Strategy or Plan board into Substack Notes and X posts. The structure comes from posts that already worked. The substance comes from the user's library. Nothing is invented.

## Scope
Does: draft standalone Substack Notes and matching X posts for ideas the user already has.
Does not: promote or announce an essay, newsletter, product or launch. Does not mine an essay for ideas. If the user asks for either, say this skill doesn't cover it and ask what they want.

Only the ideas in step 1 set the topics. Don't let recent essays, launches or earlier work in the conversation steer the drafts.

## 1. Ask which idea source
Always ask first, even if it seems obvious:
- **Strategy pillar ideas:** `eden_get_strategy`, then `eden_get_strategy` with `pillar` for each pillar to get the ideas under every topic and angle.
- **Plan board cards:** `eden_get_plan` (the Idea or Potential idea column).

Then choose what to draft:
- Skip ideas flagged `onPlanner`, cards in a done stage, and ideas already drafted in an earlier batch.
- Strategy topics with no angles have no ideas. Skip them and say which.
- Default: 2 ideas per topic that has angles, from different angles (one "What you stand for" if it fits). If the user names a topic, pillar or count, follow that.
- Say which source and which ideas you used.

## 2. Gather the user's material
- Read each chosen idea in full. Use the Strategy page's own words (`words`, `rules`, `beliefs`, `enemy`) where they fit.
- Search the library for each idea's theme (`eden_search_workspace_items`, substring on titles, so try several words) and read the journals, essays and notes that match.
- Read the voice profile note ("The Wandering Philosopher voice profile") and follow it: you-address, concrete images, dry humor, no em dashes, no guru framing, none of its listed AI-tell words.
- Check the user's own recent notes (`eden_search_social_content`, creator scope, `orderBy: recent`) so drafts don't repeat what's been posted, and to see which of their formats are working.

## 3. Research the structures
- `eden_search_social_content`, scope `global`, `platforms: ["substack","twitter"]`, one query per topic, `minOutlierScore` 15 to 30, `orderBy: outlier`. Read the full text of the best results with `eden_read_social_post` (`attemptLiveFetch: false`).
- Large results are saved to a file. Parse them with `python3 -I` and print only type, likes, outlier, URL and the first 400 characters.
- Name each top post's hook, line shape, ending and length. Record its likes and outlier score.
- Queries that include a first name (for example "Jack") return people with that name. Use topic words.

State in the output:
- One search page is not a ranking.
- Small accounts have inflated outlier scores. Say so.
- A format can decay. Check the trend before copying it.

## 4. Draft
- One draft per idea. Give each draft a different structure so a batch doesn't read as repeats.
- Each draft shows: the idea, the Strategy card it came from, the template (creator, likes, outlier), the Eden notes it draws on, a Substack note and an X post (280 characters max, count them).
- Substack: under about 70 words, first line a complete claim or a concrete scene, one idea, no link or pitch.
- X: the sharpest single line, a reversal, or a named cost. Pure encouragement is saturated.
- Facts come from the library. If a line is inferred rather than stated by the user, flag it. Never invent studies, numbers, quotes or events.
- If a draft needs a real lesson or story the library doesn't hold, write a short teaser and ask the user for the real one.
- Flag drafts built on private journal entries.
- Check any time-sensitive wording against today's date.

## 5. Deliver
- Write a markdown file under `drafts/` in the working directory.
- The user can't open files in the cloud container. Publish a page with copy buttons (Artifact) and send the file (`SendUserFile`).
- Lead the reply with the link. Then give a short summary: the structures used, ideas skipped, anything to check before posting.
- End with 2 or 3 pointed questions that challenge the user's assumptions.

## 6. Writing back to Eden
Only when the user asks:
- `eden_update_plan` can append a note to a card, move its stage and set its format. It never deletes and never edits existing notes, so finalize the text first.
- Put the Substack text in the card's notes under a heading line the user can delete. Keep the card's original text, pillar, topic and angle.
- If the user deleted cards by hand, recreate them with their original text and metadata, and say which ones could not be restored.
- Save notes to the library only when asked.

## Pitfalls seen
- Reading "ideas" as the wrong source. Ask.
- Drifting into promoting a recent essay because it was in the conversation or at the top of the library.
- Reusing lines from the user's existing top notes. Check their recent notes first.
- Mirrored lists and promo-style notes underperformed for the user. Blunt, concrete or funny notes did better.
- Leaving the drafts only in a container file the user can't open.
