Agentic definitions determine how agents think/act, not just what they do. Weak definitions lead to generic outputs; strong ones enable structured, domain-aware reasoning.

Key Takeaway: Agentic definitions act as "cognitive scaffolds." The more they encode domain knowledge, validation rules, and self-awareness, the less reliant agents become on post-hoc human fixes.


# Deep Dive: Improving Agentic Definitions

Agentic definitions determine how agents think/act, not just what they do. Weak definitions lead to generic outputs; strong ones enable structured, domain-aware reasoning.
Problem Patterns in Agentic Definitions

Bad Example (Research Agent):

```yaml
prompt: "Research {topic}"  
abilities: [web-search]  
```

Flaws:

    No criteria for source quality (e.g., ".edu/.gov preferred")
    No instruction to compare/contrast findings
    No output structure (e.g., "table of pros/cons")

Good Example:

```yaml
prompt: |  
  Investigate {topic} using 3+ peer-reviewed sources and 2 industry reports.  
  Flag conflicts between sources. Output:  
  - Summary (≤100 words)  
  - Confidence score (1-10) based on evidence consistency  
  - Unknowns requiring human verification  
abilities: [web-search, fact-check]  
constraints: [max_duration: 20m, max_sources: 8]
```

