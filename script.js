const menuToggle = document.querySelector(".menu-toggle");
const siteNav = document.querySelector(".site-nav");
const navLinks = Array.from(document.querySelectorAll(".site-nav a"));
const sectionNavLinks = navLinks.filter((link) => link.getAttribute("href")?.startsWith("#"));
const requestButton = document.querySelector(".request-button");
const heroPanel = document.querySelector(".hero-panel");
const bookingModal = document.querySelector("#booking-modal");
const calendarGrid = document.querySelector("[data-calendar-grid]");
const calendarTitle = document.querySelector("[data-calendar-title]");
const selectedDateLabel = document.querySelector("[data-selected-date]");
const slotGrid = document.querySelector("[data-slot-grid]");
const bookingForm = document.querySelector(".booking-request-form");
const bookingStatus = document.querySelector("[data-booking-status]");
const coachingTopicButtons = Array.from(document.querySelectorAll(".coaching-topic"));
const coachingTopicModal = document.querySelector("#coaching-topic-modal");
const coachingTopicTitle = document.querySelector("#coaching-topic-title");
const coachingTopicDescription = document.querySelector("[data-topic-description]");
const fraserFlipCards = Array.from(document.querySelectorAll(".fraser-flip-card"));
let activeTopicButton = null;

const BOOKING_CONFIG = {
  timezone: "Europe/London",
  ownerEmail: "",
  availabilityEndpoint: "",
  requestEndpoint: "",
};

const bookingState = {
  visibleMonth: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
  selectedDate: null,
  selectedTime: "",
  availability: new Map(),
};

menuToggle?.addEventListener("click", () => {
  const isOpen = siteNav?.classList.toggle("is-open");
  menuToggle.setAttribute("aria-expanded", String(Boolean(isOpen)));
});

navLinks.forEach((link) => {
  link.addEventListener("click", () => {
    siteNav?.classList.remove("is-open");
    menuToggle?.setAttribute("aria-expanded", "false");
  });
});

document.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", (event) => {
    const href = link.getAttribute("href");
    const isModifiedClick = event.metaKey || event.ctrlKey || event.shiftKey || event.altKey;
    const isPageLink = href && !href.startsWith("#") && !href.startsWith("mailto:") && !href.startsWith("http");

    if (!isPageLink || isModifiedClick || link.target === "_blank") return;

    event.preventDefault();
    document.body.classList.add("is-page-leaving");
    window.setTimeout(() => {
      window.location.href = link.href;
    }, 170);
  });
});

if (requestButton) {
  requestButton.addEventListener("click", openBookingModal);
}

coachingTopicButtons.forEach((button) => {
  button.setAttribute("aria-expanded", "false");
  button.addEventListener("click", () => openCoachingTopic(button));
});

fraserFlipCards.forEach((fraserFlipCard) => {
  fraserFlipCard.addEventListener("click", () => {
    const isFlipped = fraserFlipCard.classList.toggle("is-flipped");
    fraserFlipCard.setAttribute("aria-pressed", String(isFlipped));
  });
});

if (heroPanel && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  let settleTimer;

  heroPanel.addEventListener("pointerenter", () => {
    clearTimeout(settleTimer);
    heroPanel.classList.remove("is-settling");
    heroPanel.classList.add("is-interacting");
  });

  heroPanel.addEventListener("pointermove", (event) => {
    const rect = heroPanel.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - 0.5;
    const y = (event.clientY - rect.top) / rect.height - 0.5;
    const lift = 1 - Math.min(Math.hypot(x, y) * 1.7, 1);
    const shadowLift = 1 + lift * 0.55;

    heroPanel.style.setProperty("--tilt-x", `${x * 5.5}deg`);
    heroPanel.style.setProperty("--tilt-y", `${y * -4.5}deg`);
    heroPanel.style.setProperty("--float-x", `${x * 5}px`);
    heroPanel.style.setProperty("--float-y", `${y * 4 - lift * 3}px`);
    heroPanel.style.setProperty("--glow-x", `${(x + 0.5) * 100}%`);
    heroPanel.style.setProperty("--glow-y", `${(y + 0.5) * 100}%`);
    heroPanel.style.setProperty("--shadow-y", `${22 * shadowLift}px`);
    heroPanel.style.setProperty("--shadow-blur", `${60 * shadowLift}px`);
    heroPanel.style.setProperty("--shadow-spread", `${-34 - lift * 8}px`);
    heroPanel.style.setProperty("--shadow-alpha", `${0.36 + lift * 0.16}`);
  });

  heroPanel.addEventListener("pointerleave", () => {
    heroPanel.classList.remove("is-interacting");
    heroPanel.style.setProperty("--tilt-x", "0deg");
    heroPanel.style.setProperty("--tilt-y", "0deg");
    heroPanel.style.setProperty("--float-x", "0px");
    heroPanel.style.setProperty("--float-y", "0px");
    heroPanel.style.setProperty("--glow-x", "65%");
    heroPanel.style.setProperty("--glow-y", "18%");
    heroPanel.style.setProperty("--shadow-y", "22px");
    heroPanel.style.setProperty("--shadow-blur", "60px");
    heroPanel.style.setProperty("--shadow-spread", "-34px");
    heroPanel.style.setProperty("--shadow-alpha", "0.36");
    heroPanel.classList.add("is-settling");
    settleTimer = setTimeout(() => heroPanel.classList.remove("is-settling"), 650);
  });
}

function formatDateKey(date) {
  return [
    date.getFullYear(),
    String(date.getMonth() + 1).padStart(2, "0"),
    String(date.getDate()).padStart(2, "0"),
  ].join("-");
}

function formatLongDate(date) {
  return new Intl.DateTimeFormat("en-GB", {
    weekday: "long",
    day: "numeric",
    month: "long",
  }).format(date);
}

async function fetchAvailabilityForMonth(monthDate) {
  const start = new Date(monthDate.getFullYear(), monthDate.getMonth(), 1);
  const end = new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 0);

  if (BOOKING_CONFIG.availabilityEndpoint) {
    const params = new URLSearchParams({
      start: formatDateKey(start),
      end: formatDateKey(end),
      timezone: BOOKING_CONFIG.timezone,
    });
    const response = await fetch(`${BOOKING_CONFIG.availabilityEndpoint}?${params}`);
    const data = await response.json();
    return new Map(Object.entries(data.availableSlots || {}));
  }

  return generateMockAvailability(start, end);
}

function generateMockAvailability(start, end) {
  const slots = new Map();
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  for (let day = new Date(start); day <= end; day.setDate(day.getDate() + 1)) {
    const dayCopy = new Date(day);
    const weekday = dayCopy.getDay();
    const isPast = dayCopy < today;
    const isWeekend = weekday === 0 || weekday === 6;

    if (isPast || isWeekend) continue;

    const options = weekday === 2 || weekday === 4
      ? ["10:00", "13:30", "18:00"]
      : ["11:00", "16:00"];

    slots.set(formatDateKey(dayCopy), options);
  }

  return slots;
}

async function renderCalendar() {
  if (!calendarGrid || !calendarTitle) return;

  bookingState.availability = await fetchAvailabilityForMonth(bookingState.visibleMonth);
  const selectedInVisibleMonth = bookingState.selectedDate
    && bookingState.selectedDate.getMonth() === bookingState.visibleMonth.getMonth()
    && bookingState.selectedDate.getFullYear() === bookingState.visibleMonth.getFullYear();

  if (!selectedInVisibleMonth) {
    const firstAvailable = Array.from(bookingState.availability.keys())[0];
    bookingState.selectedDate = firstAvailable ? new Date(`${firstAvailable}T12:00:00`) : null;
    bookingState.selectedTime = "";
  }

  calendarGrid.innerHTML = "";
  calendarTitle.textContent = new Intl.DateTimeFormat("en-GB", {
    month: "long",
    year: "numeric",
  }).format(bookingState.visibleMonth);

  const firstDay = new Date(bookingState.visibleMonth);
  const startOffset = (firstDay.getDay() + 6) % 7;
  const gridStart = new Date(firstDay);
  gridStart.setDate(firstDay.getDate() - startOffset);

  for (let index = 0; index < 42; index += 1) {
    const date = new Date(gridStart);
    date.setDate(gridStart.getDate() + index);
    const dateKey = formatDateKey(date);
    const hasSlots = bookingState.availability.has(dateKey);
    const inMonth = date.getMonth() === bookingState.visibleMonth.getMonth();
    const button = document.createElement("button");

    button.type = "button";
    button.className = "calendar-day";
    button.textContent = String(date.getDate());
    button.setAttribute("aria-label", formatLongDate(date));

    if (!inMonth || !hasSlots) {
      button.classList.add("is-muted");
      button.disabled = true;
    } else {
      button.classList.add("has-slots");
      button.addEventListener("click", () => selectDate(date));
    }

    if (bookingState.selectedDate && dateKey === formatDateKey(bookingState.selectedDate)) {
      button.classList.add("is-selected");
    }

    calendarGrid.appendChild(button);
  }

  if (bookingState.selectedDate) {
    selectedDateLabel.textContent = formatLongDate(bookingState.selectedDate);
    bookingForm.elements.date.value = formatDateKey(bookingState.selectedDate);
  } else {
    selectedDateLabel.textContent = "Choose a date";
    bookingForm.elements.date.value = "";
  }

  bookingForm.elements.time.value = "";
  renderSlots();
}

function selectDate(date, rerender = true) {
  bookingState.selectedDate = new Date(date);
  bookingState.selectedTime = "";
  selectedDateLabel.textContent = formatLongDate(bookingState.selectedDate);
  bookingForm.elements.date.value = formatDateKey(bookingState.selectedDate);
  bookingForm.elements.time.value = "";
  renderSlots();
  if (rerender) renderCalendar();
}

function renderSlots() {
  const dateKey = bookingState.selectedDate ? formatDateKey(bookingState.selectedDate) : "";
  const slots = bookingState.availability.get(dateKey) || [];
  slotGrid.innerHTML = "";

  if (!slots.length) {
    const empty = document.createElement("p");
    empty.className = "slot-empty";
    empty.textContent = "Choose another available date.";
    slotGrid.appendChild(empty);
    return;
  }

  slots.forEach((slot) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "slot-button";
    button.textContent = slot;
    button.addEventListener("click", () => {
      bookingState.selectedTime = slot;
      bookingForm.elements.time.value = slot;
      document.querySelectorAll(".slot-button").forEach((item) => {
        item.classList.toggle("is-selected", item === button);
      });
    });
    slotGrid.appendChild(button);
  });
}

async function openBookingModal() {
  if (!bookingModal) return;
  bookingModal.hidden = false;
  document.body.classList.add("modal-open");
  bookingModal.scrollTop = 0;
  bookingStatus.textContent = "";
  await renderCalendar();
  bookingModal.scrollTop = 0;
  bookingModal.querySelector(".booking-modal__close")?.focus();
}

function closeBookingModal() {
  if (!bookingModal) return;
  bookingModal.hidden = true;
  document.body.classList.remove("modal-open");
  requestButton?.focus();
}

function openCoachingTopic(button) {
  if (!coachingTopicModal || !coachingTopicTitle || !coachingTopicDescription) return;

  activeTopicButton = button;
  coachingTopicButtons.forEach((topicButton) => {
    topicButton.classList.remove("is-active");
    topicButton.setAttribute("aria-expanded", "false");
  });
  button.classList.add("is-active");
  button.setAttribute("aria-expanded", "true");
  coachingTopicTitle.textContent = button.dataset.topicTitle || button.textContent.trim();
  coachingTopicDescription.textContent = button.dataset.topicCopy || "";
  coachingTopicModal.hidden = false;
  coachingTopicModal.scrollTop = 0;
  coachingTopicModal.querySelector(".coaching-topic-modal__close")?.focus();
}

function closeCoachingTopic({ restoreFocus = true } = {}) {
  if (!coachingTopicModal) return;

  coachingTopicModal.hidden = true;
  coachingTopicButtons.forEach((button) => {
    button.classList.remove("is-active");
    button.setAttribute("aria-expanded", "false");
  });

  if (restoreFocus) activeTopicButton?.focus();
}

async function submitBookingRequest(event) {
  event.preventDefault();

  if (!bookingForm.elements.date.value || !bookingForm.elements.time.value) {
    bookingStatus.textContent = "Choose a date and time first.";
    return;
  }

  const formData = Object.fromEntries(new FormData(bookingForm).entries());
  const payload = {
    ...formData,
    sessionType: "One-to-One Coaching",
    duration: "60 minutes",
    location: "Online",
    price: "£50",
    timezone: BOOKING_CONFIG.timezone,
  };

  if (BOOKING_CONFIG.requestEndpoint) {
    const response = await fetch(BOOKING_CONFIG.requestEndpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      bookingStatus.textContent = "Something went wrong. Please try again.";
      return;
    }
  } else {
    const requests = JSON.parse(localStorage.getItem("actorsAlchemyBookingRequests") || "[]");
    requests.push({ ...payload, createdAt: new Date().toISOString() });
    localStorage.setItem("actorsAlchemyBookingRequests", JSON.stringify(requests));

    if (BOOKING_CONFIG.ownerEmail) {
      const subject = encodeURIComponent(`Actors Alchemy booking request: ${payload.date} at ${payload.time}`);
      const body = encodeURIComponent([
        "New one-to-one coaching request",
        "",
        `Name: ${payload.name}`,
        `Email: ${payload.email}`,
        `Preferred session: ${payload.date} at ${payload.time}`,
        `Duration: ${payload.duration}`,
        `Location: ${payload.location}`,
        `Session fee: ${payload.price}`,
        "",
        "Preferences or notes:",
        payload.notes || "None provided",
      ].join("\n"));
      window.location.href = `mailto:${BOOKING_CONFIG.ownerEmail}?subject=${subject}&body=${body}`;
    }
  }

  bookingForm.reset();
  bookingState.selectedTime = "";
  bookingStatus.textContent = BOOKING_CONFIG.requestEndpoint
    ? "Request sent. Fraser will confirm by email."
    : "Request saved locally. Add an email or booking endpoint to send it automatically.";
  document.querySelectorAll(".slot-button").forEach((item) => item.classList.remove("is-selected"));
}

document.querySelector("[data-calendar-prev]")?.addEventListener("click", () => {
  bookingState.visibleMonth.setMonth(bookingState.visibleMonth.getMonth() - 1);
  bookingState.selectedDate = null;
  selectedDateLabel.textContent = "Choose a date";
  renderCalendar();
  renderSlots();
});

document.querySelector("[data-calendar-next]")?.addEventListener("click", () => {
  bookingState.visibleMonth.setMonth(bookingState.visibleMonth.getMonth() + 1);
  bookingState.selectedDate = null;
  selectedDateLabel.textContent = "Choose a date";
  renderCalendar();
  renderSlots();
});

document.querySelectorAll("[data-booking-close]").forEach((button) => {
  button.addEventListener("click", closeBookingModal);
});

document.querySelectorAll("[data-topic-close]").forEach((button) => {
  button.addEventListener("click", () => closeCoachingTopic({ restoreFocus: false }));
});

document.addEventListener("click", (event) => {
  if (!coachingTopicModal || coachingTopicModal.hidden) return;
  const target = event.target instanceof Element ? event.target : null;
  if (!target) return;
  if (target.closest(".coaching-topic-modal__panel")) return;
  if (target.closest(".coaching-topic")) return;

  closeCoachingTopic({ restoreFocus: false });
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && bookingModal && !bookingModal.hidden) {
    closeBookingModal();
  }

  if (event.key === "Escape" && coachingTopicModal && !coachingTopicModal.hidden) {
    closeCoachingTopic();
  }
});

bookingForm?.addEventListener("submit", submitBookingRequest);

const sections = sectionNavLinks
  .map((link) => document.querySelector(link.getAttribute("href")))
  .filter(Boolean);

initScrollReveals();
initLazyVideos();

if (sections.length) {
  const observer = new IntersectionObserver((entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

    if (!visible) return;

    sectionNavLinks.forEach((link) => {
      link.classList.toggle("is-active", link.getAttribute("href") === `#${visible.target.id}`);
    });
  }, {
    rootMargin: "-28% 0px -58% 0px",
    threshold: [0.1, 0.35, 0.65],
  });

  sections.forEach((section) => observer.observe(section));
}

function initScrollReveals() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const revealGroups = [
    [".hero-section-number", "reveal-from-left"],
    [".hero-eyebrow", "reveal-soft"],
    [".hero-title", "reveal-soft"],
    [".hero-copy .button-row", ""],
    [".hero-panel", "reveal-from-right reveal-soft"],
    [".alchemy-flow", "reveal-soft"],
    [".section-intro .section-number, .testimonial-section-grid .section-number, .booking-section-grid .section-number", "reveal-from-left"],
    [".section-head, .section-intro .container > div > p:not(.eyebrow), .script-margin-note", "reveal-soft"],
    [".coaching-grid > div:first-child > *, .coaching-list li", "reveal-soft"],
    [".testimonial-card", "reveal-soft"],
    [".about-grid > *, .booking-grid > *, .booking-card, .final-cta > *, .contact-grid > *, .fraser-hero > *, .stage-reel-heading > *, .stage-strip-card, .credits-panel, .fraser-cta-card", "reveal-soft"],
  ];

  const revealItems = [];
  const seen = new Set();

  revealGroups.forEach(([selector, extraClasses]) => {
    document.querySelectorAll(selector).forEach((element) => {
      if (seen.has(element)) return;
      seen.add(element);
      element.classList.add("reveal-on-scroll");
      extraClasses.split(" ").filter(Boolean).forEach((className) => element.classList.add(className));
      revealItems.push(element);
    });
  });

  if (!revealItems.length) return;

  document.body.classList.add("reveal-ready");

  revealItems.forEach((element, index) => {
    element.style.setProperty("--reveal-delay", `${Math.min(index % 6, 5) * 70}ms`);
  });

  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-visible");
      revealObserver.unobserve(entry.target);
    });
  }, {
    rootMargin: "0px 0px -12% 0px",
    threshold: 0.16,
  });

  revealItems.forEach((element) => revealObserver.observe(element));

  const driftItems = Array.from(document.querySelectorAll(".scroll-drift"));
  if (!driftItems.length) return;

  let ticking = false;
  const updateDrift = () => {
    driftItems.forEach((element) => {
      const rect = element.getBoundingClientRect();
      const progress = (rect.top + rect.height / 2 - window.innerHeight / 2) / window.innerHeight;
      const drift = Math.max(-1, Math.min(1, progress)) * -10;
      element.style.setProperty("--scroll-drift", `${drift.toFixed(2)}px`);
    });
    ticking = false;
  };

  const requestDrift = () => {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(updateDrift);
  };

  updateDrift();
  window.addEventListener("scroll", requestDrift, { passive: true });
  window.addEventListener("resize", requestDrift);
}

function initLazyVideos() {
  const lazyVideos = Array.from(document.querySelectorAll("video[data-lazy-video]"));
  if (!lazyVideos.length) return;

  const loadVideo = (video) => {
    if (video.dataset.loaded === "true") return;

    video.querySelectorAll("source[data-src]").forEach((source) => {
      source.src = source.dataset.src;
      source.removeAttribute("data-src");
    });

    video.dataset.loaded = "true";
    video.load();
  };

  const playVideo = (video) => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    loadVideo(video);
    video.play().catch(() => {});
  };

  if (!("IntersectionObserver" in window)) {
    lazyVideos.forEach(playVideo);
    return;
  }

  const videoObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      const video = entry.target;

      if (entry.isIntersecting) {
        playVideo(video);
        return;
      }

      if (video.dataset.loaded === "true") {
        video.pause();
      }
    });
  }, {
    rootMargin: "240px 0px",
    threshold: 0.08,
  });

  lazyVideos.forEach((video) => videoObserver.observe(video));
}
