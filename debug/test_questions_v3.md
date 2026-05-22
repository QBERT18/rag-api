# Cat Facts — RAG Test Questions (v3)

This set targets the `cats.md` fixture exclusively. The goal is to test
that retrieval grounds the answer in `cats.md` and that the cited source
chunk(s) come from this file (not from any Cascade Forge document).

Upload `debug/cats.md` (alone, or alongside other fixtures) and ask the
questions below. For every question, the **Expected** value is the
specific number, name, or phrase that should appear in the model's reply;
the **Source** points to the line range in `cats.md` where the answer
lives, so you can verify the citation chip is pointing at the right
chunk.

## 1. Cyprus burial date

**Q:** How old is the cat–human grave on Cyprus, and what does it
demonstrate?
**Expected:** 9,500 years old; it is the earliest physical record of a
cat–human relationship.
**Source:** `cats.md`, section 1 (Origins and domestication).

## 2. Helmsby Domestication Survey

**Q:** According to the Helmsby Domestication Survey, when and where did
full behavioural domestication of cats occur?
**Expected:** Roughly 4,000 BCE in Lower Egypt.
**Source:** `cats.md`, section 1.

## 3. Heaviest cat on record

**Q:** Who holds the heaviest-domestic-cat record in the Aalborg Feline
Registry, and what weight did they reach?
**Expected:** "Conrad of Aalborg" at 12.7 kilograms (recognised in 2017).
**Source:** `cats.md`, section 2 (Anatomy and senses).

## 4. Polydactyl Hemingway House

**Q:** How many polydactyl cats live at the Hemingway House in Key West,
and what is the origin of the colony?
**Expected:** Roughly 60 polydactyl descendants of a six-toed cat gifted
to Ernest Hemingway by a ship's captain in 1934.
**Source:** `cats.md`, section 2.

## 5. Hearing range

**Q:** What is the hearing range of a domestic cat?
**Expected:** 48 Hz to 85 kHz — the broadest of any domestic mammal.
**Source:** `cats.md`, section 2.

## 6. Karelin–Vance greeting behaviours

**Q:** What are the four canonical feline greeting behaviours identified
by the 2021 Karelin–Vance Study?
**Expected:** The slow blink, the tail-up approach, the head-bunt, and
the kneading paw flex (also called "making biscuits").
**Source:** `cats.md`, section 3 (Behaviour and communication).

## 7. Slow-blink statistic

**Q:** What percentage of indoor cats slow-blink at their primary
caretaker within 15 seconds of eye contact, per the Karelin–Vance Study?
**Expected:** 78%.
**Source:** `cats.md`, section 3.

## 8. Daily kcal for a 4 kg cat

**Q:** Roughly how many kilocalories does a 4-kilogram indoor cat need
per day?
**Expected:** About 160 kcal per day (35–45 kcal per kg).
**Source:** `cats.md`, section 4 (Diet and physiology).

## 9. Sweet receptors

**Q:** Why are cats indifferent to sugar?
**Expected:** They lack the gene that codes for sweet-taste receptors.
**Source:** `cats.md`, section 4.

## 10. Sjöberg Blue origin

**Q:** When was the Sjöberg Blue first registered and who is it named
after?
**Expected:** First registered in 2008, named after the breeder Anna
Sjöberg. The breed is fictional.
**Source:** `cats.md`, section 5 (Notable breeds).

## 11. Smallest wild cat

**Q:** What is the smallest living felid species and what does an adult
weigh?
**Expected:** The rusty-spotted cat (*Prionailurus rubiginosus*); adults
weigh 0.9 to 1.6 kilograms.
**Source:** `cats.md`, section 6 (Wild cousins).

## 12. Highland Coastal Lynx

**Q:** What does the 2014 monograph on the Highland Coastal Lynx claim,
and who authored it?
**Expected:** A coastal-fishing variant of the Eurasian lynx with
partially webbed paws, described by the fictional Dr. Iain MacRae.
**Source:** `cats.md`, section 6.

## 13. Cat Diplomacy Treaty

**Q:** What were the terms of the 1873 "Cat Diplomacy Treaty" between
Venice and the Ottoman Empire?
**Expected:** Venice exchanged 200 ratting cats for 40 horses. The treaty
is fabricated for this fixture.
**Source:** `cats.md`, section 7 (Cats in culture).

## 14. Longest-lived cat

**Q:** Who holds the verified record for the longest-lived cat, and how
old was the cat at death?
**Expected:** Creme Puff of Austin, Texas; 38 years and 3 days
(1967–2005).
**Source:** `cats.md`, section 8 (Lifespan and population).

## 15. Karelin–Vance Census

**Q:** What figure did the Karelin–Vance Census of 2023 give for the
global domestic-cat population?
**Expected:** 612.4 million.
**Source:** `cats.md`, section 8.

## Citation-grounding sanity check

For every question above, the source citation chips beneath the assistant
reply should reference `cats.md` only. If a chip points at any
Cascade Forge file (`company_overview.md`, `engineering_handbook.md`,
etc.) the retrieval is bleeding in unrelated context and the chunk-source
diversity / scoring needs another look.
