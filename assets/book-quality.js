/* Small, runtime-independent safeguards for converted mathematics activities. */
(() => {
  const pageAnswers = { ...(window.correctAnswers || {}) };
  const normalize = value => String(value ?? "")
    .normalize("NFKC")
    .trim()
    .replace(/\s+/g, " ")
    .replace(/[−–—]/g, "-")
    .toLocaleLowerCase("sw-TZ");

  const applyQualityRules = () => {
    const answers = pageAnswers;

    /* Recover placeholders that a converter incorrectly encoded as MathML letters. */
    const insertedAfterMath = new Map();
    [...document.querySelectorAll("math mrow")].forEach(row => {
      const match = row.textContent.replace(/[−–—]/g, "-").match(/^\[\[blank:(item-\d+)\]\]$/);
      if (!match || document.querySelector(`[data-activity-item="${match[1]}"]`)) return;
      const math = row.closest("math");
      const input = document.createElement("input");
      input.type = "text";
      input.dataset.activityItem = match[1];
      input.className = "mx-2 inline-block h-11 w-28 rounded-xl border-2 border-green-300 bg-white px-2 text-center align-middle";
      input.setAttribute("aria-label", `Jibu la ${match[1]}`);
      row.textContent = "";
      const anchor = insertedAfterMath.get(math) || math;
      anchor.insertAdjacentElement("afterend", input);
      insertedAfterMath.set(math, input);
    });

    /* Recover decorative answer lines when answer keys exist but controls do not. */
    const used = new Set([...document.querySelectorAll("[data-activity-item]")].map(el => el.dataset.activityItem));
    const missing = Object.keys(answers).filter(key => !used.has(key));
    const recoverDecorativeLines = () => {
      const active = new Set([...document.querySelectorAll("[data-activity-item]")].map(el => el.dataset.activityItem));
      const pending = Object.keys(answers).filter(key => !active.has(key));
      const lines = [...document.querySelectorAll('section[data-section-type^="activity_"] span.border-b-2')]
        .filter(line => !line.textContent.trim() && !line.querySelector("input"));
      pending.forEach((key, index) => {
        const line = lines[index];
        if (!line) return;
        const input = document.createElement("input");
        input.type = "text";
        input.dataset.activityItem = key;
        input.className = "h-10 w-28 rounded-lg border-2 border-green-300 bg-white px-2 text-center align-middle";
        input.setAttribute("aria-label", `Jibu la ${key}`);
        line.replaceWith(input);
      });
    };
    recoverDecorativeLines();
    setTimeout(recoverDecorativeLines, 500);
    setTimeout(recoverDecorativeLines, 1500);

    document.querySelectorAll("input[data-activity-item], textarea[data-activity-item]").forEach(field => {
      field.setAttribute("inputmode", field.inputMode || "text");
      field.setAttribute("autocomplete", "off");
      field.setAttribute("spellcheck", "false");
    });

    /* Preserve the proper division glyph in MathML operator nodes. */
    document.querySelectorAll("math mo").forEach(operator => {
      if (operator.textContent.trim() === "/") operator.textContent = "÷";
    });

    document.addEventListener("click", event => {
      const button = event.target.closest("button");
      if (!button || normalize(button.textContent) !== "tuma") return;
      document.querySelectorAll("[data-activity-item]").forEach(field => {
        const expected = answers[field.dataset.activityItem];
        if (expected == null || !(field instanceof HTMLInputElement || field instanceof HTMLTextAreaElement)) return;
        const valid = String(expected).split("||").some(answer => normalize(answer) === normalize(field.value));
        field.dataset.answerState = valid ? "correct" : "incorrect";
        field.setAttribute("aria-invalid", valid ? "false" : "true");
      });
    }, true);
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", applyQualityRules);
  else applyQualityRules();
})();
