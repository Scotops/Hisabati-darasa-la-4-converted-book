/* Small, runtime-independent safeguards for converted mathematics activities. */
(() => {
  const pageAnswers = { ...(window.correctAnswers || {}) };
  const answerAlternatives = { ...(window.answerAlternatives || {}) };
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
      pg155_sec001: ["pg155_n0008", "pg155_n0014", "pg155_n0020", "pg155_n0026", "pg155_n0032", "pg155_n0038", "pg155_n0044", "pg155_n0050", "pg155_n0056", "pg155_n0062", "pg155_n0068", "pg155_n0074"],
      pg162_sec001: ["pg162_n0006", "pg162_n0009", "pg162_n0012", "pg162_n0015", "pg162_n0018", "pg162_n0021", "pg162_n0024", "pg162_n0027", "pg162_n0030", "pg162_n0033", "pg162_n0036", "pg162_n0039"],
      pg170_sec002: ["pg170_n0012", "pg170_n0015", "pg170_n0018", "pg170_n0021", "pg170_n0024", "pg170_n0027", "pg170_n0030", "pg170_n0033", "pg170_n0036", "pg170_n0039", "pg170_n0042", "pg170_n0045", "pg170_n0048", "pg170_n0051", "pg170_n0054", "pg170_n0057", "pg170_n0060", "pg170_n0063", "pg170_n0066", "pg170_n0069"],
      pg183_sec002: ["pg183_n0028", "pg183_n0031", "pg183_n0034", "pg183_n0037", "pg183_n0040", "pg183_n0043", "pg183_n0046"]
    };
    const pageId = document.querySelector('meta[name="title-id"]')?.content;

    /*
     * The reader's page-audio collector does not consistently include text
     * IDs attached directly to images.  Put every meaningful diagram in the
     * perimeter chapter into a narration-safe text node immediately after
     * the image.  The visible image keeps its alt text for screen readers,
     * while the hidden node supplies the ordered book narration and audio.
     */
    const narratedShapeIds = new Set([
      "pg087_im003_crop_v1_crop1", "pg087_im004_crop1",
      "pg087_im005_crop_v1_crop1", "pg087_im006_crop1",
      "pg089_im003_crop1", "pg090_im005", "pg092_diagram001",
      "pg093_im005_crop_v1_crop1", "pg095_im004_crop_v1_crop1",
      "pg096_im005_seg001_v1_crop_v1_crop1",
      "pg096_im005_seg002_v1_crop_v1_crop1",
      "pg096_im005_seg003_v1_crop_v1_crop1",
      "pg097_im006_crop_v1", "pg097_im001", "pg097_im002",
      "pg098_im001"
    ]);
    const shapeAltOverrides = {
      pg097_im006_crop_v1: "Umbo d ni pembetatu yenye pande za sentimeta 9, sentimeta 7 na sentimeta 18.",
      pg097_im001: "Umbo A ni mraba.",
      pg097_im002: "Umbo B ni mstatili ulioundwa kwa kuunganisha miraba A miwili."
    };
    document.querySelectorAll("img[data-id]").forEach(image => {
      const textId = image.dataset.id;
      if (!narratedShapeIds.has(textId)) return;
      const fallback = shapeAltOverrides[textId] || image.getAttribute("alt") || "";
      image.setAttribute("alt", fallback);
      const narration = document.createElement("span");
      narration.className = "adt-audio-description diagram-narration";
      narration.dataset.id = textId;
      narration.textContent = fallback;
      image.removeAttribute("data-id");
      image.insertAdjacentElement("afterend", narration);
    });

    /*
     * A number of converted place-value calculations use preserved spaces to
     * keep unit columns together (for example "tani   kg" / "12   740").
     * The page font is proportional, so those columns can drift when the
     * reader changes font size or read-aloud wraps the current word.  Mark
     * every such mathematical row for a fixed-width rendering.  Keeping the
     * data-id on the original node preserves the exact narration and i18n
     * lookup while the CSS makes the visible columns deterministic.
     */
    const stabilizeSpacedCalculations = () => {
      document.querySelectorAll("#content .whitespace-pre").forEach(node => {
        const value = node.textContent.replace(/\u00a0/g, " ").trimEnd();
        /* texts.json normalizes repeated spaces before this safeguard runs,
           so accept a single surviving separator as well.  Restricting the
           rule to whitespace-pre mathematical rows keeps ordinary prose out. */
        const hasColumnGap = /\S\s+\S/.test(value);
        const isMathematical = /\d/.test(value) ||
          /(?:^|\s)(?:km|hm|dam|m|dm|sm|mm|tani|t|kg|hg|dag|g|dg|sg|mg|L|mL|sh|st)(?:\s|$)/i.test(value);
        if (hasColumnGap && isMathematical) {
          node.classList.add("validation-spaced-calculation");
          /* Inline the essential alignment properties as a cache-safe
             fallback for offline readers that retain an older stylesheet. */
          node.style.setProperty("font-family", '"Courier New", Courier, ui-monospace, monospace', "important");
          node.style.setProperty("font-variant-numeric", "tabular-nums lining-nums");
          node.style.setProperty("letter-spacing", "0", "important");
          node.style.setProperty("word-spacing", "0", "important");
        }
      });
    };
    const renderPlaceValueColumns = () => {
      const unitPattern = /^(?:km|hm|dam|m|dm|sm|mm|tani|t|kg|hg|dag|g|dg|sg|mg|l|ml|saa|dakika|sh|st)$/i;
      const parents = new Set([...document.querySelectorAll("#content .whitespace-pre")].map(node => node.parentElement));
      parents.forEach(parent => {
        if (!parent) return;
        const rows = [...parent.children].filter(node => node.classList?.contains("whitespace-pre"));
        const header = rows.find(node => {
          const parts = (node.dataset.placeValueSource || node.textContent).trim().split(/\s+/).filter(Boolean);
          return parts.length >= 2 && parts.length <= 4 && parts.every(part => unitPattern.test(part));
        });
        if (!header) return;
        const columnCount = (header.dataset.placeValueSource || header.textContent).trim().split(/\s+/).filter(Boolean).length;
        const preparedRows = rows.map(node => {
          if (!node.dataset.placeValueSource) node.dataset.placeValueSource = node.textContent.replace(/\u00a0/g, " ").trim();
          const source = node.dataset.placeValueSource;
          if (!source) return null;
          let parts = source.split(/\s+/).filter(Boolean);
          if (parts.length === columnCount + 1 && /^[+\-\u2212\u00d7x]$/i.test(parts[0])) {
            parts = [`${parts[0]} ${parts[1]}`, ...parts.slice(2)];
          }
          if (parts.length > columnCount) return null;
          parts = [...Array(columnCount - parts.length).fill(""), ...parts];
          return { node, source, parts };
        }).filter(Boolean);
        const columnWidths = Array.from({ length: columnCount }, (_, index) =>
          Math.max(3, ...preparedRows.map(row => row.parts[index].length))
        );
        const columnTemplate = columnWidths.map(width => `${width + 1}ch`).join(" ");
        preparedRows.forEach(({ node, source, parts }) => {
          if (node.dataset.placeColumns === String(columnCount) && node.querySelectorAll(":scope > .validation-place-cell").length === columnCount) return;
          node.dataset.placeColumns = String(columnCount);
          node.classList.add("validation-place-value-row");
          node.setAttribute("aria-label", source);
          node.style.setProperty("font-family", '"Courier New", Courier, ui-monospace, monospace', "important");
          node.style.setProperty("font-variant-numeric", "tabular-nums lining-nums");
          node.style.setProperty("display", "grid", "important");
          node.style.setProperty("grid-template-columns", columnTemplate, "important");
          node.style.setProperty("justify-content", "center", "important");
          node.style.setProperty("column-gap", "1.5ch", "important");
          node.style.setProperty("padding-left", "0", "important");
          node.style.setProperty("padding-right", "0", "important");
          node.style.setProperty("margin-left", "0", "important");
          node.style.setProperty("margin-right", "0", "important");
          node.replaceChildren(...parts.map(part => {
            const cell = document.createElement("span");
            cell.className = "validation-place-cell";
            cell.setAttribute("aria-hidden", "true");
            cell.textContent = part;
            return cell;
          }));
        });
      });
    };
    stabilizeSpacedCalculations();
    renderPlaceValueColumns();
    setTimeout(stabilizeSpacedCalculations, 700);
    setTimeout(stabilizeSpacedCalculations, 1700);
    setTimeout(renderPlaceValueColumns, 700);
    setTimeout(renderPlaceValueColumns, 1700);
    const alignmentContent = document.getElementById("content");
    if (alignmentContent) {
      let spacingRepairTimer;
      new MutationObserver(() => {
        clearTimeout(spacingRepairTimer);
        spacingRepairTimer = setTimeout(() => {
          stabilizeSpacedCalculations();
          renderPlaceValueColumns();
        }, 80);
      }).observe(alignmentContent, { childList: true, subtree: true, characterData: true });
    }
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
      pg034_sec001: { pg034_n0006: ["624", "\u00d7 35", "3120", "+ 18720", "21840"] },
      pg035_sec001: { pg035_n0007: ["3125", "\u00d7 12", "6250", "+ 31250", "37500"] },
      pg039_sec001: { pg039_n0008: ["5624", "\u00d7 24", "22496", "+ 112480", "134976"] },
      pg140_sec001: { pg140_n0012: ["0.5", "+ 0.2", "0.7"] },
      pg140_sec002: { pg140_n0026: ["1.7", "+ 2.6", "4.3"] },
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
    if (knownStackedCalculations[pageId]) {
      let stackedRepairTimer;
      const stackedContent = document.getElementById("content");
      if (stackedContent) new MutationObserver(() => {
        clearTimeout(stackedRepairTimer);
        stackedRepairTimer = setTimeout(() => {
          renderConvertedMathTables();
          renderKnownStackedCalculations();
        }, 80);
      }).observe(stackedContent, { childList: true, subtree: true, characterData: true });
    }
    const reviewedTextIds = {
      pg106_sec001: ["pg106_n0006", "pg106_n0018", "pg106_n0019", "pg106_n0020", "pg106_n0021"],
      pg121_sec002: Array.from({ length: 18 }, (_, i) => `pg121_n${String(22 + i).padStart(4, "0")}`),
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
        visual.dataset.verticalItem = `item-${item}`;
        if (pageId === "pg183_sec002" && source.dataset.display) {
          const lines = source.dataset.display.split(/\r?\n/).map(line => line.trimEnd());
          const upper = document.createElement("span");
          upper.style.whiteSpace = "pre";
          upper.textContent = lines.slice(0, -1).join("\n");
          const lower = document.createElement("span");
          lower.style.whiteSpace = "pre";
          lower.textContent = lines.at(-1) || "";
          visual.replaceChildren(upper, lower);
          const rule = document.createElement("span");
          rule.className = "validation-rule";
          visual.append(rule);
        } else if (fractionPairs.length === 2) {
          const fractionMarkup = parts => `<span class="validation-fraction"><span>${parts[0]}</span><span>${parts[1]}</span></span>`;
          const operator = expression.match(/\+|\-|\u00d7|\u00f7|\u2212|x/i)?.[0] || "\u00d7";
          visual.innerHTML = `<span>${fractionMarkup(fractionPairs[0])}</span><span>${operator} ${fractionMarkup(fractionPairs[1])}</span><span class="validation-rule"></span>`;
        } else if (pageId === "pg162_sec001") {
          const upper = match[1].trim().match(/^saa\s+dakika\s+(\d+)\s+(\d+)$/i);
          const lower = match[3].trim().match(/^(\d+)\s+(\d+)$/);
          if (upper && lower) {
            const row = (lead, hour, minute, extraClass = "") =>
              `<span class="validation-unit-row ${extraClass}"><span>${lead}</span><span>${hour}</span><span>${minute}</span></span>`;
            visual.classList.add("validation-unit-calculation", "validation-time-calculation");
            visual.style.setProperty("--validation-unit-count", 2);
            visual.style.setProperty("width", "11rem");
            visual.style.setProperty("min-width", "11rem");
            visual.innerHTML = `${row("", "saa", "dakika", "validation-unit-heading")}${row("", upper[1], upper[2])}${row(match[2], lower[1], lower[2])}<span class="validation-rule"></span>`;
          } else {
            visual.innerHTML = `<span>${match[1]}</span><span>${match[2]} ${match[3]}</span><span class="validation-rule"></span>`;
          }
        } else if (pageId === "pg082_sec001") {
          const leftTokens = match[1].trim().split(/\s+/);
          const firstNumber = leftTokens.findIndex(token => /^\d/.test(token));
          const units = firstNumber > 0 ? leftTokens.slice(0, firstNumber) : [];
          const upper = firstNumber > 0 ? leftTokens.slice(firstNumber) : [];
          const lower = match[3].trim().split(/\s+/);
          if (units.length && upper.length === units.length && lower.length === units.length) {
            const row = (lead, values, extraClass = "") =>
              `<span class="validation-unit-row ${extraClass}"><span>${lead}</span>${values.map(value => `<span>${value}</span>`).join("")}</span>`;
            visual.classList.add("validation-unit-calculation");
            visual.style.setProperty("--validation-unit-count", units.length);
            visual.style.setProperty("width", `${2 + units.length * 4.5}rem`);
            visual.style.setProperty("min-width", `${2 + units.length * 4.5}rem`);
            visual.innerHTML = `${row("", units, "validation-unit-heading")}${row("", upper)}${row(match[2], lower)}<span class="validation-rule"></span>`;
          } else {
            visual.innerHTML = `<span>${match[1]}</span><span>${match[2]} ${match[3]}</span><span class="validation-rule"></span>`;
          }
        } else if (pageId === "pg079_sec001") {
          const parseCapacity = value => value.trim().match(/^(\d+)\s*L\s*(\d+)\s*mL$/i);
          const upper = parseCapacity(match[1]);
          const lower = parseCapacity(match[3]);
          if (upper && lower) {
            visual.classList.add("validation-capacity-calculation");
            visual.innerHTML = `
              <span class="validation-capacity-row validation-capacity-heading"><span></span><span>L</span><span>mL</span></span>
              <span class="validation-capacity-row"><span></span><span>${upper[1]}</span><span>${upper[2]}</span></span>
              <span class="validation-capacity-row"><span>${match[2]}</span><span>${lower[1]}</span><span>${lower[2]}</span></span>
              <span class="validation-rule"></span>`;
          } else {
            visual.innerHTML = `<span>${match[1]}</span><span>${match[2]} ${match[3]}</span><span class="validation-rule"></span>`;
          }
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
    const organizeVerticalAnswerFields = () => {
      document.querySelectorAll(".validation-vertical-calculation[data-vertical-item]").forEach(visual => {
        const item = visual.dataset.verticalItem;
        const fields = [...document.querySelectorAll(`[data-activity-item="${item}"]`)].filter(field => field !== visual);
        if (!fields.length) return;
        const canonical = fields.find(field => !field.classList.contains("validation-vertical-answer")) || fields[0];
        fields.forEach(field => { if (field !== canonical) field.remove(); });
        canonical.classList.add("validation-vertical-answer");
        canonical.removeAttribute("style");
        let stack = visual.closest(".validation-vertical-stack");
        if (!stack) {
          stack = document.createElement("span");
          stack.className = "validation-vertical-stack";
          visual.insertAdjacentElement("beforebegin", stack);
          stack.appendChild(visual);
        }
        if (canonical.parentElement !== stack || canonical.previousElementSibling !== visual) stack.appendChild(canonical);
        stack.parentElement?.querySelectorAll("span.border-b-2").forEach(line => {
          if (!line.textContent.trim() && !line.querySelector("input, textarea")) {
            const wrapper = line.parentElement;
            line.remove();
            if (wrapper && !wrapper.textContent.trim() && !wrapper.querySelector("input, textarea")) wrapper.remove();
          }
        });
      });
    };
    const removeAllDuplicateAnswerFields = () => {
      const groups = new Map();
      document.querySelectorAll("input[data-activity-item], textarea[data-activity-item]").forEach(field => {
        const item = field.dataset.activityItem;
        groups.set(item, [...(groups.get(item) || []), field]);
      });
      groups.forEach(fields => {
        if (fields.length < 2) return;
        const canonical = fields.find(field => field.id?.startsWith("fitb-input-")) ||
          fields.find(field => field.classList.contains("validation-vertical-answer")) || fields[0];
        fields.forEach(field => { if (field !== canonical) field.remove(); });
      });
    };
    makeVerticalCalculations();
    setTimeout(() => { makeVerticalCalculations(); organizeVerticalAnswerFields(); }, 600);
    setTimeout(() => { makeVerticalCalculations(); organizeVerticalAnswerFields(); }, 1600);
    setTimeout(() => { makeVerticalCalculations(); organizeVerticalAnswerFields(); removeAllDuplicateAnswerFields(); }, 2600);
    setTimeout(() => { makeVerticalCalculations(); organizeVerticalAnswerFields(); removeAllDuplicateAnswerFields(); }, 4200);
    setTimeout(removeAllDuplicateAnswerFields, 2100);
    setTimeout(removeAllDuplicateAnswerFields, 3000);
    if (verticalPages[pageId]?.length) {
      let repairTimer;
      const content = document.getElementById("content");
      if (content) new MutationObserver(() => {
        clearTimeout(repairTimer);
        repairTimer = setTimeout(() => {
          makeVerticalCalculations();
          organizeVerticalAnswerFields();
          removeAllDuplicateAnswerFields();
        }, 180);
      }).observe(content, { childList: true, subtree: true, characterData: true });
    }

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
        const alternatives = [
          ...String(expected).split("||"),
          ...(answerAlternatives[field.dataset.activityItem] || []).map(String)
        ];
        const entered = field.value;
        const valid = alternatives.some(answer => normalize(answer) === normalize(entered));
        /* The bundled activity engine accepts one canonical answer. When a
           reviewed equivalent is entered, submit the canonical form to that
           engine and immediately restore exactly what the student typed. */
        if (valid && normalize(entered) !== normalize(expected)) {
          field.value = String(expected).split("||")[0];
          setTimeout(() => { field.value = entered; }, 0);
        }
        field.dataset.answerState = valid ? "correct" : "incorrect";
        field.setAttribute("aria-invalid", valid ? "false" : "true");
      });
    }, true);
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", applyQualityRules);
  else applyQualityRules();
})();
