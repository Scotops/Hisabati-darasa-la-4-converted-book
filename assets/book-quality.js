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

    /* Restore the vertically stacked calculations specified by the book review. */
    const verticalPages = {
      pg032_sec001: ["pg032_n0007", "pg032_n0010", "pg032_n0013", "pg032_n0016", "pg032_n0019", "pg032_n0022", "pg032_n0025", "pg032_n0028", "pg032_n0031", "pg032_n0034", "pg032_n0037", "pg032_n0040", "pg032_n0043", "pg032_n0046", "pg032_n0049"],
      pg038_sec001: ["pg038_n0024", "pg038_n0028", "pg038_n0032", "pg038_n0036", "pg038_n0040", "pg038_n0044", "pg038_n0048", "pg038_n0052"],
      pg041_sec001: ["pg041_n0005", "pg041_n0008", "pg041_n0011", "pg041_n0014", "pg041_n0017", "pg041_n0020", "pg041_n0023", "pg041_n0026", "pg041_n0029", "pg041_n0032", "pg041_n0035", "pg041_n0038", "pg041_n0041", "pg041_n0044", "pg041_n0047"]
    };
    const pageId = document.querySelector('meta[name="title-id"]')?.content;
    const reviewedTextIds = {
      pg053_sec003: Array.from({ length: 11 }, (_, i) => `pg053_n${String(30 + i * 2).padStart(4, "0")}`),
      pg106_sec001: ["pg106_n0006", "pg106_n0018", "pg106_n0019", "pg106_n0020", "pg106_n0021"],
      pg127_sec001: ["pg127_n0011", "pg127_n0013", "pg127_n0014", "pg127_n0015", "pg127_n0016", "pg127_n0021", "pg127_n0026"],
      pg133_sec001: ["pg133_n0003", "pg133_n0004", "pg133_n0012", "pg133_n0014", "pg133_n0016", "pg133_n0018", "pg133_n0020", "pg133_n0022", "pg133_n0024", "pg133_n0026", "pg133_n0028"],
      pg137_sec001: ["pg137_n0037", "pg137_n0076"],
      pg138_sec001: ["pg138_n0032"],
      pg152_sec001: ["pg152_n0043", "pg152_n0044"],
      pg177_sec001: ["pg177_n0017", "pg177_n0019", "pg177_n0021", "pg177_n0023"],
      pg180_sec001: ["pg180_n0004", "pg180_n0006", "pg180_n0008", "pg180_n0010", "pg180_n0012"],
      pg183_sec002: ["pg183_n0049", "pg183_n0052"]
    };
    const reviewedInlineText = Object.fromEntries((reviewedTextIds[pageId] || []).map(id => [id, document.querySelector(`[data-id="${id}"]`)?.innerHTML]));
    const enforceReviewedText = () => {
      const ids = reviewedTextIds[pageId];
      if (!ids?.length) return;
      ids.forEach(id => {
        const node = document.querySelector(`[data-id="${id}"]`);
        if (node && reviewedInlineText[id] != null) node.innerHTML = reviewedInlineText[id];
      });
    };
    setTimeout(enforceReviewedText, 700);
    setTimeout(enforceReviewedText, 1700);
    const makeVerticalCalculations = () => {
      (verticalPages[pageId] || []).forEach((id, index) => {
        const source = document.querySelector(`[data-id="${id}"]`);
        if (!source || source.dataset.verticalized === "true") return;
        const expression = source.textContent.replace(/\s*=.*$/, "").trim();
        const match = expression.match(/^(\d+)\s*([^\d\s])\s*(\d+)$/i);
        if (!match) return;
        const item = pageId === "pg038_sec001" ? index + 7 : index + 1;
        source.dataset.verticalized = "true";
        source.classList.add("validation-source-text");
        const visual = document.createElement("span");
        visual.className = "validation-vertical-calculation";
        visual.setAttribute("aria-hidden", "true");
        visual.innerHTML = `<span>${match[1]}</span><span>${match[2]} ${match[3]}</span><span class="validation-rule"></span>`;
        source.insertAdjacentElement("afterend", visual);
        if (!document.querySelector(`[data-activity-item="item-${item}"]`)) {
          const input = document.createElement("input");
          input.type = "text";
          input.dataset.activityItem = `item-${item}`;
          input.className = "validation-vertical-answer";
          input.setAttribute("aria-label", `Jibu la swali la ${item}`);
          visual.insertAdjacentElement("afterend", input);
        }
      });
    };
    makeVerticalCalculations();
    setTimeout(makeVerticalCalculations, 600);
    setTimeout(makeVerticalCalculations, 1600);

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
