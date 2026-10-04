# Screen review prompt

Review this Evoloom-based iOS screen for the stated user task. First describe
the information hierarchy, related groups, primary action and flow. Identify
where native NavigationStack, List, Form, search, sheet or system alert serves
that flow. Use `DESIGN.md` and the public component APIs for repeated visual
decisions; keep product-specific screen structure in the product.

Check Dynamic Type, narrow width, English/Japanese length, dark mode and
Increased Contrast. Review likely VoiceOver order, contextual labels, error
recovery, disabled/loading behavior and focus changes, but do not claim an
actual VoiceOver result without a run in the integrating product. For each
finding label the evidence as an observed fact, a testable hypothesis or a
preference. Cite the screenshot, code path or test result for observations.
Suggest the smallest change tied to the user task and how to verify it.

If a product-specific decision proves reusable, record the screen context,
observed problem, proposed rule and validation in the product first. Propose
an Evoloom token or component change only after checking another applicable
context; do not create an untested global rule from one screen.
