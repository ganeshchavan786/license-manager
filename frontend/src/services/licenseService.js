// ================================================================
// licenseService.js
// तुमच्या existing Salary Pay React app मध्ये हे file add करा
// src/services/licenseService.js
// ================================================================

const LICENSE_SERVER = import.meta.env.VITE_API_URL || "https://licenseapi.vrushaliinfotech.com";
const CACHE_KEY = "sp_license_cache";
const MACHINE_ID_KEY = "sp_machine_id";

// ── Machine ID ──────────────────────────────────────────────────
export function getMachineId() {
  let id = localStorage.getItem(MACHINE_ID_KEY);
  if (!id) {
    // Browser fingerprint (basic)
    const raw = [
      navigator.userAgent,
      navigator.language,
      screen.width + "x" + screen.height,
      new Date().getTimezoneOffset(),
      navigator.hardwareConcurrency || "",
    ].join("|");

    // Simple hash
    let hash = 0;
    for (let i = 0; i < raw.length; i++) {
      hash = ((hash << 5) - hash) + raw.charCodeAt(i);
      hash |= 0;
    }
    id = Math.abs(hash).toString(16) + Date.now().toString(16);
    localStorage.setItem(MACHINE_ID_KEY, id);
  }
  return id;
}

// ── Cache Management ────────────────────────────────────────────
function saveCache(data) {
  const cache = {
    ...data,
    cached_at: new Date().toISOString(),
  };
  localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
}

function loadCache() {
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function getCachedDaysOffline(cache) {
  if (!cache?.cached_at) return 999;
  const cachedAt = new Date(cache.cached_at);
  const now = new Date();
  return Math.floor((now - cachedAt) / (1000 * 60 * 60 * 24));
}

// ── Main License Check ──────────────────────────────────────────
export async function checkLicense() {
  const machineId = getMachineId();
  const licenseKey = localStorage.getItem("sp_license_key");

  // License key नसेल तर registration हवे
  if (!licenseKey) {
    return { valid: false, reason: "not_registered", plan: null };
  }

  // Online असेल तर server validate करा
  try {
    const response = await fetch(`${LICENSE_SERVER}/license/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ machine_id: machineId, license_key: licenseKey }),
      signal: AbortSignal.timeout(5000), // 5 second timeout
    });

    if (response.ok) {
      const data = await response.json();
      if (data.valid) {
        saveCache(data);
        return data;
      }
    }
  } catch {
    // Offline आहे — cache वापरा
    console.log("License server offline — using cache");
  }

  // Offline: Cache check करा
  const cache = loadCache();
  if (!cache) {
    return { valid: false, reason: "no_cache", plan: null };
  }

  const daysOffline = getCachedDaysOffline(cache);
  const gracePeriod = cache.grace_period_days || 15;

  if (daysOffline <= gracePeriod) {
    return {
      ...cache,
      valid: true,
      offline: true,
      days_remaining_offline: gracePeriod - daysOffline,
    };
  }

  // Grace period संपली
  return {
    valid: false,
    reason: "grace_expired",
    plan: cache.plan,
    offline: true,
  };
}

// ── Registration ────────────────────────────────────────────────
export async function registerCustomer(formData) {
  const machineId = getMachineId();
  const response = await fetch(`${LICENSE_SERVER}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...formData, machine_id: machineId }),
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || "Registration failed");
  }

  const data = await response.json();
  localStorage.setItem("sp_license_key", data.license_key);
  localStorage.setItem("sp_customer_id", data.customer_id);
  return data;
}

// ── Plan Features Check ─────────────────────────────────────────
export function hasFeature(userFeatures, featureName) {
  if (!userFeatures) return false;
  if (userFeatures.includes("*")) return true;
  return userFeatures.includes(featureName);
}

// ── Create Razorpay Order ───────────────────────────────────────
export async function createPaymentOrder(plan, promoCode = null) {
  const customerId = localStorage.getItem("sp_customer_id");
  const body = { plan, customer_id: customerId };
  if (promoCode) body.promo_code = promoCode;

  const response = await fetch(`${LICENSE_SERVER}/payment/create-order`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Order creation failed");
  }
  return response.json();
}

// ── Verify Payment ──────────────────────────────────────────────
export async function verifyPayment(paymentData, plan) {
  const customerId = localStorage.getItem("sp_customer_id");
  const response = await fetch(`${LICENSE_SERVER}/payment/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...paymentData, customer_id: customerId, plan }),
  });

  if (!response.ok) throw new Error("Payment verification failed");
  const data = await response.json();

  // नवीन license key save करा
  if (data.license_key) {
    localStorage.setItem("sp_license_key", data.license_key);
  }
  return data;
}
