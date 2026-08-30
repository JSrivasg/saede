/**
 * Cloudflare Pages Function — the launch list.
 *
 * Receives the signup form and stores the address in a KV namespace.
 * Deployed automatically by Cloudflare Pages from the functions/ directory
 * at the repository root, so there is nothing to configure in the build.
 *
 * ONE SETUP STEP, in the Cloudflare dashboard:
 *   1. Workers & Pages -> KV -> Create a namespace, call it SAEDE_SIGNUPS
 *   2. Your Pages project -> Settings -> Functions -> KV namespace bindings
 *      Variable name: SIGNUPS      Namespace: SAEDE_SIGNUPS
 *   3. Redeploy
 *
 * Until that binding exists this returns an honest error and the form on the
 * page tells the visitor to email instead. It never pretends to have stored
 * an address it did not store.
 *
 * To read the list: Workers & Pages -> KV -> SAEDE_SIGNUPS, or
 *   npx wrangler kv key list --binding=SIGNUPS
 */

const EMAIL = /^[^@\s]+@[^@\s.]+\.[^@\s]{2,}$/;

export async function onRequestPost({ request, env }) {
  const json = (body, status) =>
    new Response(JSON.stringify(body), {
      status,
      headers: { "content-type": "application/json; charset=utf-8" },
    });

  let email = "";
  let honey = "";
  try {
    const form = await request.formData();
    email = String(form.get("email") || "").trim().toLowerCase();
    honey = String(form.get("bot-field") || "");
  } catch (e) {
    return json({ ok: false, error: "bad_request" }, 400);
  }

  // The honeypot is hidden from people and irresistible to bots. Accept it
  // silently so the bot believes it succeeded and does not try again.
  if (honey) return json({ ok: true }, 200);

  if (!EMAIL.test(email) || email.length > 254) {
    return json({ ok: false, error: "invalid_email" }, 400);
  }

  if (!env.SIGNUPS) {
    // No KV bound yet. Say so plainly rather than dropping the address.
    return json({ ok: false, error: "not_configured" }, 503);
  }

  try {
    // Keyed by address so signing up twice does not create two entries.
    await env.SIGNUPS.put(
      `signup:${email}`,
      JSON.stringify({
        email,
        at: new Date().toISOString(),
        country: request.headers.get("cf-ipcountry") || null,
      })
    );
  } catch (e) {
    return json({ ok: false, error: "store_failed" }, 500);
  }

  return json({ ok: true }, 200);
}

// A GET to this path is not an error worth a stack trace; just say no.
export async function onRequestGet() {
  return new Response("Method not allowed", { status: 405 });
}
