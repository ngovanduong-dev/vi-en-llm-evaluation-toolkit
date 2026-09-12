# Vietnamese-English Language QA Rubric

Use this checklist for bilingual prompts, translation-style tasks, and
Vietnamese localization review.

## Checklist

- Natural Vietnamese phrasing
- Formality and tone consistency
- Mistranslated intent
- Over-literal translation
- Cultural or contextual mismatch
- Fluent but contextually wrong answer
- Missing constraint from the original prompt
- Hallucinated factual claim

## Severity Guide

- **Low:** Minor wording issue that does not change the user's intent.
- **Medium:** Noticeable tone, localization, or constraint issue.
- **High:** Meaning changes, important constraint is lost, or the response could mislead the user.

Evaluator rationales should be short, specific, and tied to the prompt rather
than personal preference.

## Dimension Boundaries

Use the general rubric's seven dimensions when assigning general scores.
Naturalness and register belong under language naturalness; changed meaning
belongs under correctness; an omitted source component belongs under
completeness. Poor wording can impair clarity without omitting information.
Formatting concerns structure, and safety needs a concrete relevant risk.
Explain each affected dimension separately rather than spreading a language
penalty across unrelated fields. Severity describes impact, not a winner rule.
