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
      pg041_sec001: ["pg041_n0005", "pg041_n0008", "pg041_n0011", "pg041_n0014", "pg041_n0017", "pg041_n0020", "pg041_n0023", "pg041_n0026", "pg041_n0029", "pg041_n0032", "pg041_n0035", "pg041_n0038", "pg041_n0041", "pg041_n0044", "pg041_n0047"],
      pg079_sec001: ["pg079_n0017", "pg079_n0021", "pg079_n0025", "pg079_n0029", "pg079_n0033", "pg079_n0037", "pg079_n0041", "pg079_n0045", "pg079_n0049"],
      pg082_sec001: ["pg082_n0006", "pg082_n0009", "pg082_n0012", "pg082_n0015", "pg082_n0018", "pg082_n0021", "pg082_n0024", "pg082_n0027", "pg082_n0030"],
      pg121_sec002: Array.from({ length: 18 }, (_, i) => `pg121_n${String(22 + i).padStart(4, "0")}`),
      pg155_sec001: ["pg155_n0008", "pg155_n0014", "pg155_n0020", "pg155_n0026", "pg155_n0032", "pg155_n0038", "pg155_n0044", "pg155_n0050", "pg155_n0056", "pg155_n0062", "pg155_n0068", "pg155_n0074"],
      pg157_sec002: ["pg157_n0020", "pg157_n0025", "pg157_n0030", "pg157_n0035", "pg157_n0040", "pg157_n0045", "pg157_n0050", "pg157_n0055", "pg157_n0060"],
      pg162_sec001: ["pg162_n0006", "pg162_n0009", "pg162_n0012", "pg162_n0015", "pg162_n0018", "pg162_n0021", "pg162_n0024", "pg162_n0027", "pg162_n0030", "pg162_n0033", "pg162_n0036", "pg162_n0039"],
      pg170_sec002: ["pg170_n0012", "pg170_n0015", "pg170_n0018", "pg170_n0021", "pg170_n0024", "pg170_n0027"],
      pg183_sec002: ["pg183_n0028", "pg183_n0031", "pg183_n0034", "pg183_n0037", "pg183_n0040", "pg183_n0043", "pg183_n0046"]
    };
    const pageId = document.querySelector('meta[name="title-id"]')?.content;
    const alignmentPages = new Set(["pg033_sec001", "pg034_sec001", "pg035_sec001", "pg039_sec001", "pg045_sec001", "pg046_sec001", "pg057_sec001", "pg058_sec002", "pg060_sec001", "pg061_sec001", "pg062_sec001", "pg063_sec001", "pg069_sec001", "pg070_sec001", "pg071_sec001", "pg072_sec001", "pg074_sec001", "pg077_sec001", "pg079_sec001", "pg082_sec001", "pg121_sec002", "pg123_sec001", "pg154_sec001", "pg155_sec001", "pg156_sec001", "pg157_sec001", "pg157_sec002", "pg159_sec001", "pg160_sec002", "pg161_sec001", "pg162_sec001", "pg170_sec001", "pg170_sec002", "pg171_sec001", "pg179_sec002", "pg180_sec002", "pg183_sec002"]);
    if (alignmentPages.has(pageId)) document.documentElement.classList.add("validation-alignment-page");
    const renderConvertedMathTables = () => {
      document.querySelectorAll("math mtable").forEach(mathTable => {
        if (mathTable.dataset.htmlTableRendered === "true") return;
        const table = document.createElement("table");
        table.className = "validation-html-math-table";
        [...mathTable.querySelectorAll(":scope > mtr")].forEach(mathRow => {
          const row = document.createElement("tr");
          [...mathRow.querySelectorAll(":scope > mtd")].forEach(mathCell => {
            const cell = document.createElement("td");
            cell.textContent = mathCell.textContent.replace(/\u00a0/g, " ").trim();
            if ((mathCell.getAttribute("style") || "").includes("border-bottom")) cell.classList.add("validation-math-rule");
            row.appendChild(cell);
          });
          table.appendChild(row);
        });
        mathTable.dataset.htmlTableRendered = "true";
        mathTable.closest("math")?.replaceWith(table);
      });
    };
    renderConvertedMathTables();
    setTimeout(renderConvertedMathTables, 700);
    setTimeout(renderConvertedMathTables, 1700);
    const knownStackedCalculations = {
      pg035_sec001: { pg035_n0007: ["3125", "\u00d7 12", "6250", "+ 31250", "37500"] },
      pg039_sec001: { pg039_n0008: ["5624", "\u00d7 24", "22496", "+ 112480", "134976"] },
      pg170_sec001: { pg170_n0005: ["sh 5500", "\u00d7 20", "0000", "+ 110000", "sh 110000"] }
    };
    const renderKnownStackedCalculations = () => {
      Object.entries(knownStackedCalculations[pageId] || {}).forEach(([id, rows]) => {
        const source = document.querySelector(`[data-id="${id}"]`);
        if (!source || source.querySelector(".validation-known-calculation")) return;
        const table = document.createElement("table");
        table.className = "validation-html-math-table validation-known-calculation";
        rows.forEach((value, index) => {
          const row = table.insertRow();
          const cell = row.insertCell();
          cell.textContent = value;
          if (index === 1 || index === 3) cell.classList.add("validation-math-rule");
        });
        source.replaceChildren(table);
      });
    };
    renderKnownStackedCalculations();
    setTimeout(renderKnownStackedCalculations, 700);
    setTimeout(renderKnownStackedCalculations, 1700);
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
        const expression = source.textContent.replace(/\[\[blank:[^\]]+\]\]/g, "").replace(/\s*=.*$/, "").trim();
        const match = expression.match(/^(.+?)\s*(\+|\-|\u00d7|\u00f7|\u2212|x)\s*(.+?)$/i);
        const fractionPairs = [...source.querySelectorAll(".inline-flex.flex-col")].map(fraction =>
          [...fraction.children].map(part => part.textContent.trim()).filter(Boolean)
        ).filter(parts => parts.length === 2);
        if (!match && fractionPairs.length !== 2) return;
        const itemOffsets = { pg038_sec001: 7 };
        const item = (itemOffsets[pageId] || 1) + index;
        source.dataset.verticalized = "true";
        source.classList.add("validation-source-text");
        const visual = document.createElement("span");
        visual.className = "validation-vertical-calculation";
        visual.setAttribute("aria-hidden", "true");
        if (fractionPairs.length === 2) {
          const fractionMarkup = parts => `<span class="validation-fraction"><span>${parts[0]}</span><span>${parts[1]}</span></span>`;
          const operator = expression.match(/\+|\-|\u00d7|\u00f7|\u2212|x/i)?.[0] || "\u00d7";
          visual.innerHTML = `<span>${fractionMarkup(fractionPairs[0])}</span><span>${operator} ${fractionMarkup(fractionPairs[1])}</span><span class="validation-rule"></span>`;
        } else {
          visual.innerHTML = `<span>${match[1]}</span><span>${match[2]} ${match[3]}</span><span class="validation-rule"></span>`;
        }
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
    const removeDuplicateAnswerFields = () => {
      const fields = [...document.querySelectorAll("[data-activity-item]")];
      const counts = fields.reduce((map, field) => map.set(field.dataset.activityItem, (map.get(field.dataset.activityItem) || 0) + 1), new Map());
      fields.forEach(field => {
        if (counts.get(field.dataset.activityItem) > 1 && field.classList.contains("validation-vertical-answer")) field.remove();
      });
    };
    makeVerticalCalculations();
    setTimeout(() => { makeVerticalCalculations(); removeDuplicateAnswerFields(); }, 600);
    setTimeout(() => { makeVerticalCalculations(); removeDuplicateAnswerFields(); }, 1600);

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
