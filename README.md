# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

My system covers **UCSD campus dining experiences and practical food advice for students**. It answers questions about Dining Dollars, Triton Cash, campus markets, dining-plan rules, dorm cooking, food prices, and student recommendations.

This knowledge is valuable because official UCSD pages explain policies and locations, but they do not always answer the practical questions students ask. For example, students may want to know where they can spend leftover Dining Dollars, whether campus-market prices are worth it, or which location has a specific recommended meal. These details are scattered across official pages and student Reddit discussions, so the guide combines both types of sources in one searchable system.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | UCSD Dining Plan Overview | Official UCSD information | `documents/dining_plan_overview.txt` |
| 2 | Dining Dollars FAQ | Official UCSD information | `documents/dining_dollars_faq.txt` |
| 3 | Budgeting Dining Dollars and Triton Cash | Official UCSD information | `documents/budgeting_advice.txt` |
| 4 | Triton Cash Locations and Flexibility | Official UCSD information | `documents/triton_cash_locations.txt` |
| 5 | Leftover Dining Dollars Recommendations | Student opinion from r/UCSD | `documents/leftover_dining_dollars.txt` |
| 6 | Dorm Cooking Ideas | Student opinion from r/UCSD | `documents/dorm_cooking.txt` |
| 7 | Healthy and Affordable Food Options | Student opinion from r/UCSD | `documents/healthy_cheap_options.txt` |
| 8 | Student Opinions on Dining Hall Quality | Student opinion from r/UCSD | `documents/dining_hall_quality.txt` |
| 9 | Campus Market Pricing Discussion | Student opinion from r/UCSD | `documents/market_pricing.txt` |
| 10 | Foodworx Deep-Dish Pizza Recommendation | Student opinion from r/UCSD | `documents/foodworx_review.txt` |

---

## Chunking Strategy

**Chunk size:** Each cleaned `.txt` file is preserved as one chunk. The files are short, focused source excerpts rather than long articles, so I did not split them using a fixed character or token limit.

**Overlap:** I used no overlap because each document remains intact as one chunk. Overlap would repeat content without adding useful context.

**Why these choices fit your documents:** The corpus contains short reviews and focused factual excerpts. Keeping each source as one chunk prevents a recommendation from being separated from its explanation. For example, the Foodworx recommendation stays in the same chunk as the detail that it is recommended for deep-dish pizza. Before chunking, I manually removed unnecessary navigation text, usernames, repeated replies, and unrelated comments from the source excerpts. The loader also removes surrounding whitespace when reading each file.

**Final chunk count:** 10 chunks across 10 documents.
---

## Embedding Model

**Model used:** I used `all-MiniLM-L6-v2` through the `sentence-transformers` library. This model is lightweight, fast enough to run locally, and appropriate for comparing short text excerpts with student questions. The embeddings are stored in ChromaDB, and the system retrieves the top four most relevant chunks for each query using semantic similarity.

**Production tradeoff reflection:** If I were deploying this system for real users and cost was not a constraint, I would compare larger embedding models that may improve retrieval accuracy for slang, abbreviations, restaurant nicknames, and longer documents. I would also compare multilingual support because some students may ask questions in languages other than English. However, a larger model could increase latency, storage requirements, and API cost. I would weigh retrieval quality against response speed and decide whether a locally hosted model or an API-hosted model is the better fit.

---

## Grounded Generation

**System prompt grounding instruction:** The generation step uses Groq's `llama-3.3-70b-versatile` model. Before generating an answer, the system retrieves the top four relevant chunks from ChromaDB and formats them as context. The system prompt tells the model: `Answer the user's question using only the retrieved source excerpts. Do not invent facts or rely on outside knowledge. Clearly distinguish between official UCSD information and student opinions from Reddit discussions. If the retrieved sources do not contain enough information to answer the question, say that the collected sources do not provide enough information.` This limits the response to the evidence stored in the corpus.

**How source attribution is surfaced in the response:** Each stored chunk includes source metadata. The retrieved context includes the source filename and the chunk text, and the prompt instructs the model to include a short `Sources` section at the end of each answer. This lets the user see which file supported the response and whether the information came from an official UCSD source or a student-opinion source.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Is UCSD's residential dining-plan system unlimited or à la carte? | UCSD uses an à la carte dining-plan system rather than an unlimited all-you-care-to-eat system. | The system explained that UCSD uses an à la carte system and that students choose how to spend their Dining Dollars throughout the year. | Relevant | Accurate |
| 2 | Where can Dining Dollars be used, and how is Triton Cash different? | Dining Dollars can be used at HDH Dining locations. Triton Cash can also be used at more than 60 participating on- and off-campus locations. | The system stated that Dining Dollars are for HDH Dining locations and explained that Triton Cash is more flexible because it can be used at additional participating locations on and off campus. | Relevant | Accurate |
| 3 | Why does UCSD recommend saving some Triton Cash for academic breaks? | Some dining locations close or operate with limited hours during breaks and holidays. Triton Cash provides additional flexibility during those periods. | The system explained that some dining locations may close or have limited hours during breaks and that saving Triton Cash gives students more options during those periods. | Relevant | Accurate |
| 4 | Where can I get deep-dish pizza with leftover Dining Dollars? | Foodworx. | The system recommended Foodworx for deep-dish pizza and identified the student-opinion source that supported the recommendation. | Relevant | Accurate |
| 5 | What ingredients can students buy from campus markets for cooking in a dorm? | The dorm-cooking source mentions pasta, pizza crust, chicken, beef, vegetables, and Hawaiian rolls. | The system listed pasta, pizza crust, chicken, beef, vegetables, and Hawaiian rolls as ingredients mentioned in the dorm-cooking source. | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** Which UCSD dining hall has the shortest wait time during lunch?

**What the system returned:** The retrieval step returned general dining-hall and food-quality excerpts, but none of them contained lunch wait-time data. The generated answer could not identify a dining hall with the shortest lunch wait and stated that the collected sources did not provide enough information.

**Root cause (tied to a specific pipeline stage):** The limitation comes from the document-ingestion stage. My 10-document corpus does not contain reliable information about lunch wait times. Because the relevant evidence is missing before embedding and retrieval occur, the semantic search step cannot return an accurate answer. The model correctly avoided inventing an answer, but the system still fails to answer the user's question.

**What you would change to fix it:** I would add more documents focused on wait times, such as recent student discussions about dining-hall lines and regularly updated dining-location data. I would also attach timestamps to sources so the system could prioritize recent information, since wait times can change depending on the quarter, day of the week, and time of day.

---

## Spec Reflection

**One way the spec helped you during implementation:** The planning document helped me define my domain, source files, embedding model, retrieval count, and evaluation questions before writing the full pipeline. This made the implementation easier to build in stages. I could first verify that all 10 text files loaded correctly, then confirm that ChromaDB stored 10 embeddings, and finally test whether the retrieved sources supported the generated answers.

**One way your implementation diverged from the spec, and why:** My initial planning document discussed using fixed-size chunks with overlap for longer documents. During implementation, I simplified the strategy and preserved each cleaned text file as one chunk with no overlap. This was a better fit because my source files are short and focused. Splitting them further could separate a useful detail, such as a restaurant recommendation, from the reason it was recommended.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* I gave the AI my document list, my chunking-strategy section from `planning.md`, and the requirement that each short review should remain intact.
- *What it produced:* The AI helped generate a Python document-loading pipeline that reads the 10 `.txt` files from the `documents` folder and converts each file into one chunk.
- *What I changed or overrode:* I chose the simpler one-document-per-chunk strategy instead of splitting each document into fixed-size pieces with overlap. My cleaned documents were short enough that additional splitting would have made retrieval less useful.

**Instance 2**

- *What I gave the AI:* I gave the AI my retrieval requirements: use `all-MiniLM-L6-v2`, store embeddings in ChromaDB, retrieve the top four chunks, and print distance scores with source metadata.
- *What it produced:* The AI helped generate `retrieval_pipeline.py`, which builds the vector store and tests semantic retrieval with my five evaluation questions.
- *What I changed or overrode:* The first version expected metadata fields such as `title` that were not available in my pipeline, which caused a `KeyError`. I changed the printing logic to use the available `source` metadata so the retrieval results would display correctly.

**Instance 3**

- *What I gave the AI:* I gave the AI my grounded-generation requirements, my retrieval function, and the requirement to use Groq's `llama-3.3-70b-versatile` model with a Gradio interface.
- *What it produced:* The AI helped generate `app.py`, which sends retrieved context to the Groq model, asks the model to answer only from the provided sources, includes source attribution, and displays the response in a Gradio interface.
- *What I changed or overrode:* I tested both supported and unsupported questions manually. I kept the instruction that the model should say the sources do not provide enough information when the retrieved documents cannot support an answer.
