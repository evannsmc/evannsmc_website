/**
 * slide-refs.js
 *
 * FEATURE: Per-Slide Citation References
 *
 * PURPOSE:
 * This script automatically displays full bibliographic references at the bottom
 * of each slide where citations appear. This allows the audience to immediately
 * see what paper/source is being referenced without waiting for the final
 * references slide.
 *
 * HOW IT WORKS:
 * 1. Waits for RevealJS to fully load the presentation
 * 2. Collects all references from the References slide into a lookup table
 * 3. Scans each content slide for citations
 * 4. For each slide with citations, appends the corresponding full references
 *    to the bottom of that specific slide
 *
 * TECHNICAL DETAILS:
 * - Runs after RevealJS 'ready' event to ensure DOM is fully constructed
 * - Uses cloneNode() to duplicate references without removing them from the
 *   References slide (they still appear at the end)
 * - Handles RevealJS's nested section structure (sections contain slides)
 * - Styled via custom.scss with .slide-references class
 *
 * USAGE:
 * Just use standard Quarto citations in your slides:
 *   [See @citation-key for details]  →  "See [1] for details"
 *   [@citation-key]                  →  "[1]"
 *
 * The full reference will automatically appear at the slide bottom.
 *
 * CUSTOMIZATION:
 * - To change positioning/styling: edit custom.scss .slide-references
 * - To change which slides get references: modify the querySelector on line 53
 * - To change reference format: edit the CSL file in your project
 */

Reveal.on('ready', function() {
  // STEP 1: Collect all references from the References slide
  // -------------------------------------------------------
  // Find the #refs div which contains all bibliography entries.
  // Quarto/Pandoc generates this automatically at the end of the document.
  const refsSection = document.querySelector('#refs');

  // If there's no references section, nothing to do
  if (!refsSection) return;

  // Create a lookup table (object) to store all references by their ID.
  // Key: reference ID (e.g., "ref-smith2020")
  // Value: cloned DOM node of the full reference entry
  const allRefs = {};

  // Each reference has class .csl-entry and an id like "ref-citationkey"
  refsSection.querySelectorAll('.csl-entry').forEach(ref => {
    // Clone the node deeply (true) to copy all child elements and text
    // This allows us to reuse the reference without removing it from
    // the original References slide
    allRefs[ref.id] = ref.cloneNode(true);
  });

  // STEP 2: Process each individual slide
  // -------------------------------------
  // RevealJS structure: Level 1 headers create parent sections,
  // Level 2 headers create slides within those sections.
  // We only want to process the actual content slides (level2),
  // not the parent section containers.
  document.querySelectorAll('.reveal .slides section.level2').forEach(slide => {

    // STEP 3: Find all citations in this slide
    // ---------------------------------------------------------
    // slide.querySelectorAll() already scopes to descendants of this slide,
    // so no closest('section') guard is needed — it caused null===slide → false
    // when Reveal.js detached/reattached DOM nodes, silently dropping citations.
    const citationSpans = slide.querySelectorAll('.citation[data-cites]');

    // If this slide has no citations, skip it
    if (citationSpans.length === 0) return;

    // STEP 4: Extract citation keys and find corresponding references
    // ---------------------------------------------------------------
    // Use a Set to automatically handle duplicates
    // (if someone cites the same paper twice on one slide)
    const citedRefs = new Set();

    citationSpans.forEach(cite => {
      // data-cites can contain multiple space-separated citation keys
      // Example: data-cites="smith2020 jones2021"
      const cites = cite.getAttribute('data-cites').split(' ');

      cites.forEach(citeKey => {
        // Convert citation key to reference ID format
        // Citation key: "smith2020" → Reference ID: "ref-smith2020"
        const refId = 'ref-' + citeKey;

        // If we found this reference in our lookup table, add it
        if (allRefs[refId]) {
          citedRefs.add(refId);
        }
      });
    });

    // STEP 5: Create and append the references div to this slide
    // ----------------------------------------------------------
    if (citedRefs.size > 0) {
      // Create a container div for this slide's references
      const slideRefs = document.createElement('div');

      // This class is styled in custom.scss to position at bottom of slide
      slideRefs.className = 'slide-references';

      // Append each cited reference to the container
      citedRefs.forEach(refId => {
        // Clone again because we might reuse the same reference on multiple slides
        slideRefs.appendChild(allRefs[refId].cloneNode(true));
      });

      // PLACEMENT STRATEGY: Place citations below footnotes if they exist
      // Footnotes are rendered in Quarto as <aside> elements with .aside-footnotes
      // Also check for .footnotes class for other cases
      const footnotesAside = slide.querySelector('aside');

      if (footnotesAside) {
        // Insert citations after the footnotes aside element
        footnotesAside.parentNode.insertBefore(slideRefs, footnotesAside.nextSibling);
      } else {
        // No footnotes: add the references container to the end of the slide
        slide.appendChild(slideRefs);
      }

      // Reveal.js sets dimensions on .slides, not on individual section elements,
      // so section.level2 has auto height. bottom:0 then anchors to the section's
      // content height — not to the configured 900px — placing the bar off-screen.
      // Quarto's theme also sets min-height:0!important on all sections in center
      // mode, which defeats a plain inline minHeight assignment. setProperty with
      // 'important' creates an inline !important which beats any stylesheet rule.
      // Reveal.js sets dimensions on .slides, not on individual section elements,
      // so section.level2 has auto height. bottom:0 then anchors to the section's
      // content height — not to the configured 900px — placing the bar off-screen.
      // Quarto's theme also sets min-height:0!important on all sections in center
      // mode, which defeats a plain inline minHeight assignment. setProperty with
      // 'important' creates an inline !important which beats any stylesheet rule.
      var cfgHeight = (Reveal.getConfig && Reveal.getConfig().height) || 900;
      slide.style.setProperty('min-height', cfgHeight + 'px', 'important');
      slide.style.setProperty('height', cfgHeight + 'px', 'important');

      // Measurement + per-entry shrink happens in sizeSlideRefs() — deferred so
      // it runs after the slide is actually visible. Reveal.js hides non-active
      // sections (display:none in most transition modes), which makes
      // offsetHeight/scrollWidth return 0 — so a one-shot measurement at 'ready'
      // only works for the initial slide. We hook 'slidechanged' further below.
    }
  });

  // Pandoc sometimes appends a stray <div class="references"> at the document
  // end outside all slide <section>s, bleeding into the last visible slide.
  // Remove any .references div that is NOT inside a slide section.
  document.querySelectorAll('div.references.csl-bib-body').forEach(function(el) {
    if (!el.closest('section')) {
      el.remove();
    }
  });

  // NOTE: Quarto injects its own tippyHover on every a[role="doc-biblioref"]
  // in the compiled HTML. Adding a second Tippy here causes the double popup.
  // Quarto's built-in tooltip already shows the full reference text on hover.

  // Measure each slide's reference bar height so custom.scss can reserve
  // the exact padding-bottom needed (via --ref-bar-h). Runs on slidechanged
  // because Reveal hides non-active sections with display:none, which makes
  // offsetHeight return 0 — so a one-shot measurement at 'ready' only works
  // for the initial slide. Also covers the footnote aside height.
  function sizeSlideRefs(slide) {
    if (!slide) return;
    var slideRefs = slide.querySelector('.slide-references');
    if (!slideRefs) return;
    if (slide.dataset.refsSized === '1') return;

    slide.style.setProperty('--ref-bar-h', slideRefs.offsetHeight + 'px');
    var aside = slide.querySelector('aside');
    if (aside) slide.style.setProperty('--aside-h', aside.offsetHeight + 'px');

    // Only mark sized if we successfully measured — otherwise retry next visit
    if (slideRefs.offsetHeight > 0) slide.dataset.refsSized = '1';
  }

  Reveal.on('slidechanged', function(e) {
    sizeSlideRefs(e.currentSlide);
  });
  sizeSlideRefs(Reveal.getCurrentSlide && Reveal.getCurrentSlide());
});
