/* Saede — progressive enhancement only.
   The site is fully readable and navigable with this file blocked. */
(function () {
  "use strict";

  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* --- THE OPENING ------------------------------------------------------
     Film, fade to white, then the name. Rules, in order of importance:
       1. It is never a gate. The page is fully rendered behind it, and if
          anything at all goes wrong the layer is removed immediately.
       2. Once per browsing session. Coming back to the homepage from
          another page does not replay it.
       3. Never for anyone who has asked for reduced motion.
       4. Never if the browser refuses to autoplay the video.
       5. Skippable at any moment, by button or by pressing Escape.
     The markup ships with `hidden` set, so with JS off it never runs.    */
  (function () {
    var el = document.querySelector("[data-opening]");
    if (!el) return;

    var video = el.querySelector("[data-opening-video]");
    var skip = el.querySelector("[data-opening-skip]");
    var timers = [];
    var finished = false;

    var seen = false;
    try { seen = sessionStorage.getItem("saede-opening") === "1"; } catch (e) {}

    if (seen || reducedMotion) { el.remove(); return; }

    var end = function () {
      if (finished) return;
      finished = true;
      timers.forEach(clearTimeout);
      try { sessionStorage.setItem("saede-opening", "1"); } catch (e) {}
      el.setAttribute("data-phase", "out");
      document.documentElement.classList.remove("is-opening");
      window.setTimeout(function () { el.remove(); }, 1200);
    };

    var showName = function () {
      if (finished) return;
      if (el.getAttribute("data-phase") === "name") return;
      el.setAttribute("data-phase", "name");
      // hold on the name, then lift the whole layer away
      timers.push(window.setTimeout(end, 2600));
    };

    // Reveal the layer first, then let the browser lay it out and paint
    // before asking the video to play. Calling play() in the same tick as
    // un-hiding gets rejected by browsers that refuse to start media they
    // consider not-yet-visible, which is what "video-only background media
    // was paused to save power" means.
    el.hidden = false;
    document.documentElement.classList.add("is-opening");

    if (video) {
      video.addEventListener("ended", showName);
      video.addEventListener("error", function () { softFallback(); });
      // the video fades itself to white at the end; meet it just before
      video.addEventListener("loadedmetadata", function () {
        if (!isFinite(video.duration)) return;
        timers.push(window.setTimeout(showName, Math.max(600, (video.duration - 0.15) * 1000)));
      });
    }

    // A blocked autoplay should still feel composed: hold a beat on white,
    // then bring the name up, rather than snapping to it instantly.
    var softFallback = function () {
      if (finished) return;
      timers.push(window.setTimeout(showName, 700));
    };

    // Give the layer a moment to lay out and paint, then start the film.
    // A timeout rather than requestAnimationFrame on purpose: rAF does not
    // fire while the document is hidden, so a page opened in a background
    // tab would never reach this at all.
    timers.push(window.setTimeout(function () {
      if (finished || !video) { softFallback(); return; }
      var play = video.play();
      if (play && typeof play.catch === "function") {
        play.catch(softFallback);
      }
    }, 60));

    // If the film has not actually started moving shortly after we asked,
    // stop waiting on it and bring the name up. Better a short white beat
    // than a frozen frame nobody can explain.
    timers.push(window.setTimeout(function () {
      if (!finished && (!video || video.paused || video.currentTime === 0)) showName();
    }, 1800));

    // Hard backstop: whatever happens, the opening is gone within 12 seconds.
    timers.push(window.setTimeout(end, 12000));

    skip && skip.addEventListener("click", end);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !finished) end();
    });
  })();

  /* --- the front-page film ---------------------------------------------
     The photograph underneath is the real hero. The film is an enhancement
     laid over it, and it only ever fades in once the browser says it can
     play through. It is skipped entirely on narrow screens, under reduced
     motion, and when the visitor has data saver on — the file is several
     megabytes and nobody should pay for it on a phone plan.              */
  (function () {
    var video = document.querySelector("[data-hero-video]");
    if (!video) return;

    var saveData = navigator.connection && navigator.connection.saveData;
    var narrow = window.matchMedia("(max-width: 780px)").matches;
    if (reducedMotion || saveData || narrow) { video.remove(); return; }

    video.addEventListener("canplaythrough", function () {
      video.classList.add("is-playing");
    }, { once: true });
    video.addEventListener("error", function () { video.remove(); });

    // load only after the page itself has settled, so the film never
    // competes with the stylesheet, the fonts or the still image
    var start = function () {
      video.src = video.getAttribute("data-src");
      var play = video.play();
      if (play && typeof play.catch === "function") {
        play.catch(function () { video.remove(); });
      }
    };
    if (document.readyState === "complete") { window.setTimeout(start, 200); }
    else { window.addEventListener("load", function () { window.setTimeout(start, 200); }); }
  })();

  /* --- launch-list signup ----------------------------------------------
     No endpoint is connected yet (site.json signup.endpoint is null), so
     data-live is "false" and the form validates, confirms, and stores
     nothing. It must never imply otherwise. When an endpoint is set the
     form posts normally and this handler steps out of the way.           */
  (function () {
    var forms = document.querySelectorAll("[data-signup]");
    Array.prototype.forEach.call(forms, function (form) {
      var input = form.querySelector("[data-signup-input]");
      var status = form.parentNode.querySelector("[data-signup-status]");
      if (!input || !status) return;

      form.addEventListener("submit", function (e) {
        var value = input.value.trim();
        var ok = /^[^@\s]+@[^@\s.]+\.[^@\s]{2,}$/.test(value);

        if (!ok) {
          e.preventDefault();
          status.setAttribute("data-state", "error");
          status.textContent = form.getAttribute("data-error") ||
            "That email address does not look right. Could you check it?";
          input.focus();
          return;
        }

        // valid, but nothing to post to yet
        if (form.getAttribute("data-live") !== "true") {
          e.preventDefault();
          status.setAttribute("data-state", "ok");
          // may contain a <strong> and an address, so set it as markup
          status.innerHTML = form.getAttribute("data-success") || "Thank you.";
          form.reset();
          return;
        }

        // Post the fields ourselves so the visitor stays on the page instead
        // of being sent to the provider's own success screen. data-ajax holds
        // the URL to post to, whichever provider is configured.
        var target = form.getAttribute("data-ajax");
        if (target) {
          e.preventDefault();
          var button = form.querySelector("button");
          if (button) { button.disabled = true; }
          status.removeAttribute("data-state");
          status.textContent = "One moment…";

          fetch(target, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams(new FormData(form)).toString()
          }).then(function (r) {
            if (!r.ok) { throw new Error(r.status); }
            status.setAttribute("data-state", "ok");
            status.innerHTML = form.getAttribute("data-success") || "Thank you.";
            form.reset();
          }).catch(function () {
            status.setAttribute("data-state", "error");
            status.textContent = "Something went wrong at our end. Please email hello@saede.eu and we will add you by hand.";
          }).then(function () {
            if (button) { button.disabled = false; }
          });
        }
      });
    });
  })();

  /* --- sticky header hairline ------------------------------------------ */
  var header = document.querySelector("[data-header]");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-stuck", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* --- mobile menu ------------------------------------------------------ */
  var toggle = document.querySelector("[data-nav-toggle]");
  var mobile = document.getElementById("mobile-nav");
  if (toggle && mobile) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      mobile.classList.toggle("is-open", !open);
    });
  }

  /* --- Concerns dropdown ------------------------------------------------ */
  var drops = document.querySelectorAll("[data-drop]");
  Array.prototype.forEach.call(drops, function (drop) {
    var button = drop.querySelector("button");
    if (!button) return;

    var setOpen = function (open) {
      drop.setAttribute("data-open", String(open));
      button.setAttribute("aria-expanded", String(open));
    };

    button.addEventListener("click", function (e) {
      e.stopPropagation();
      setOpen(drop.getAttribute("data-open") !== "true");
    });
    drop.addEventListener("mouseenter", function () { setOpen(true); });
    drop.addEventListener("mouseleave", function () { setOpen(false); });
    drop.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { setOpen(false); button.focus(); }
    });
    document.addEventListener("click", function (e) {
      if (!drop.contains(e.target)) setOpen(false);
    });
  });

  /* --- reveal on scroll -------------------------------------------------
     Only enabled when IntersectionObserver exists and the visitor has not
     asked for reduced motion. Without it, .reveal elements are simply
     visible — the class only hides things once .reveal-ready is set.

     Two safeguards, because content that never appears is far worse than
     content that appears without a fade:
       1. a generous bottom rootMargin, so a section starts animating before
          it scrolls into view and is already solid by the time you reach it
       2. a failsafe timer that reveals everything regardless, in case the
          observer never fires (bfcache restores, odd mobile browsers)       */
  var reduced = reducedMotion;
  var revealAll = function () {
    document.querySelectorAll(".reveal").forEach(function (el) {
      el.classList.add("is-in");
    });
  };

  if ("IntersectionObserver" in window && !reduced) {
    document.documentElement.classList.add("reveal-ready");

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px 25% 0px", threshold: 0 });

    document.querySelectorAll(".reveal").forEach(function (el, i) {
      el.style.transitionDelay = Math.min(i % 3, 2) * 60 + "ms";
      io.observe(el);
    });

    // failsafe
    window.setTimeout(revealAll, 2500);
    window.addEventListener("pageshow", function (e) {
      if (e.persisted) revealAll();
    });
  }

})();
