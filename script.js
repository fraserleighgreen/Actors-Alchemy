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

const GOOGLE_BOOKING_URL = "https://calendar.google.com/calendar/appointments/schedules/AcZssZ0g_dRHZeRdO8E4UtYs_XI8L-Zts16q8S1w9GamopuZHjlWN6RJDGGHnVs0_v8Wgrbu8GyJbKvz?gv=true";
const bookingSection = document.querySelector("#booking");
const bookingCalendarEmbed = document.querySelector(".google-calendar-embed");
const bookingAnchorLinks = Array.from(document.querySelectorAll('a[href="#booking"], a[href$="index.html#booking"]'));

const BOOKING_CONFIG = {
  timezone: "Europe/London",
  ownerEmail: "fraser@actorsalchemy.co.uk",
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

if (requestButton) {
  requestButton.addEventListener("click", openBookingModal);
}

function warmBookingCalendar() {
  if (!bookingCalendarEmbed) return;

  if (!bookingCalendarEmbed.getAttribute("src")) {
    bookingCalendarEmbed.setAttribute("src", GOOGLE_BOOKING_URL);
  }
}

function scrollToBookingSection(event) {
  if (!bookingSection) return;

  const link = event.currentTarget;
  const href = link instanceof HTMLAnchorElement ? link.getAttribute("href") || "" : "";
  const isSamePageBookingLink = href === "#booking";

  warmBookingCalendar();

  if (!isSamePageBookingLink) return;

  event.preventDefault();
  bookingSection.scrollIntoView({ block: "start", behavior: "auto" });
  window.history.pushState(null, "", "#booking");
}

bookingAnchorLinks.forEach((link) => {
  link.addEventListener("pointerenter", warmBookingCalendar);
  link.addEventListener("focus", warmBookingCalendar);
  link.addEventListener("touchstart", warmBookingCalendar, { passive: true });
  link.addEventListener("click", scrollToBookingSection);
});

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
    : BOOKING_CONFIG.ownerEmail
      ? "Email request opened. Send it to Fraser to confirm your booking request."
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

initScrollSettle();
initLazyVideos();
initAlchemyCursor();

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

function initScrollSettle() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const settleItems = Array.from(document.querySelectorAll("main > .section > .container"));
  if (!settleItems.length) return;

  let lastScrollY = window.scrollY;
  let driftX = 0;
  let driftY = 0;
  let targetDriftX = 0;
  let targetDriftY = 0;
  let ticking = false;

  const render = () => {
    driftX += (targetDriftX - driftX) * 0.11;
    driftY += (targetDriftY - driftY) * 0.11;
    if (
      Math.abs(driftX) < 0.01
      && Math.abs(driftY) < 0.01
      && Math.abs(targetDriftX) < 0.01
      && Math.abs(targetDriftY) < 0.01
    ) {
      driftX = 0;
      driftY = 0;
      targetDriftX = 0;
      targetDriftY = 0;
      ticking = false;
    } else {
      window.requestAnimationFrame(render);
    }

    settleItems.forEach((item, index) => {
      const direction = index % 2 === 0 ? 1 : -1;
      item.style.setProperty("--scroll-settle-x", `${(driftX * direction).toFixed(3)}px`);
      item.style.setProperty("--scroll-settle-y", `${driftY.toFixed(3)}px`);
    });
  };

  const requestRender = () => {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(render);
  };

  window.addEventListener("scroll", () => {
    const delta = window.scrollY - lastScrollY;
    lastScrollY = window.scrollY;
    targetDriftX = Math.max(-14, Math.min(14, delta * 0.16));
    targetDriftY = Math.max(-5, Math.min(5, delta * -0.06));
    requestRender();

    window.clearTimeout(initScrollSettle.settleTimer);
    initScrollSettle.settleTimer = window.setTimeout(() => {
      targetDriftX = 0;
      targetDriftY = 0;
      requestRender();
    }, 120);
  }, { passive: true });
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

function initAlchemyCursor() {
  const supportsFinePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  const isCompactLayout = window.matchMedia("(max-width: 760px)").matches;
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (!supportsFinePointer || isCompactLayout || prefersReducedMotion) return;

  const cursor = document.createElement("div");
  cursor.className = "alchemy-cursor";
  cursor.setAttribute("aria-hidden", "true");
  cursor.innerHTML = '<span class="alchemy-cursor__ring"></span><span class="alchemy-cursor__mark"></span>';
  document.body.appendChild(cursor);
  document.documentElement.classList.add("has-alchemy-cursor");

  const interactiveSelector = [
    "a",
    "button",
    "input",
    "textarea",
    "select",
    "summary",
    "[role='button']",
    ".fraser-flip-card",
    ".coaching-topic",
    ".stage-strip",
  ].join(",");

  const moveCursor = (event) => {
    cursor.style.transform = `translate3d(${event.clientX}px, ${event.clientY}px, 0)`;
    cursor.classList.add("is-visible");
  };

  const updateCursorState = (event) => {
    const target = event.target instanceof Element ? event.target : null;
    const overCalendar = Boolean(target?.closest(".google-calendar-embed"));
    const isInteractive = Boolean(target?.closest(interactiveSelector));

    cursor.classList.toggle("is-muted", overCalendar);
    cursor.classList.toggle("is-interactive", isInteractive && !overCalendar);
  };

  window.addEventListener("pointermove", (event) => {
    moveCursor(event);
    updateCursorState(event);
  }, { passive: true });

  window.addEventListener("pointerdown", () => {
    cursor.classList.add("is-pressed");
  }, { passive: true });

  window.addEventListener("pointerup", () => {
    cursor.classList.remove("is-pressed");
  }, { passive: true });

  document.addEventListener("pointerleave", () => {
    cursor.classList.remove("is-visible", "is-interactive", "is-pressed");
  });

  document.addEventListener("pointerover", updateCursorState, { passive: true });
}
