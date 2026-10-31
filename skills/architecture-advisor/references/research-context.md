# Evaluate research before making a product claim

The architecture workflow is motivated by constrained optimization. The bundled scripts implement ordinary finite-catalog optimization and accounting. They do not implement a new subexponential SAT/counting algorithm and must never be described as an ETH-refutation engine.

## Research-to-product checklist

1. Establish the source, authorship, version and publication date from primary evidence.
2. State the exact problem, assumptions, size parameter, runtime/space claim and output type.
3. Distinguish proof artifacts, machine-checked statement, independent interpretation/review, implementation, and empirical benchmark.
4. Check the encoding from the business problem, including auxiliary variables and costs. A reduction may enlarge the relevant size parameter substantially.
5. Examine constants, preprocessing, arithmetic, memory, parameter ranges and fallback paths. Subexponential does not mean polynomial or practically fast.
6. Compare equivalent tasks: counting with counting; feasibility with feasibility; optimization with optimization. Include the complete execution and encoding cost.
7. Keep unvalidated research outside the critical decision path. Make an experimental backend replaceable and label all results experimental until independently checked.

Exact model counting is not the same as optimizing a weighted business objective. Counting assignments is not automatically counting distinct architectures: auxiliary variables and symmetric representations can duplicate one design. Use unique extensions or projected counting if that feature is needed. Uniform Boolean assignments need not be uniform business designs.

For the OpenAI ETH manuscript discussed in the originating use case, the October 2026 release materials distinguished the sharper manuscript bound from the formalization scope. Do not freeze that historical status as a current verdict. Verify the latest version and community status if the user asks about it.

Primary starting points:

- https://openai.com/index/building-scientific-understanding-with-academic-communities/
- https://github.com/openai/math/tree/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026
- https://github.com/openai/math/blob/main/lean/docs/378.md
- https://ethdiscussion.blog/

In an architecture review, mention research only if it materially affects the decision. Do not turn ordinary resource planning into an unnecessary discussion of complexity theory.
