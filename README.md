# leakwatch-jp

English | [日本語](README.ja.md)

A CLI that checks whether your email address appears in past breaches via a **public API (Have I Been Pwned by default)**,
rates the severity, suggests response steps, and tracks your progress — **entirely on your own PC**.

## What it does
- Checks your registered email addresses against HIBP (`leakwatch check`)
- Rates severity (low / medium / high / critical) from the breached fields (passwords, cards, phone numbers, etc.)
- Checks whether a password appears in breach data (`leakwatch password`). Uses HIBP Pwned Passwords, sending only the first 5 characters of the SHA-1 hash (k-anonymity). Passwords are never sent, displayed, or stored
- Shows response steps for major Japanese services (`leakwatch guide`)
- Records and displays your response status (unaddressed / done) (`leakwatch status` / `done`)
- Inspects "you've been breached" emails you received: fake domains, urgency-inducing wording, AI instruction text (`leakwatch mail`)
- Optionally, supplementary assessment by a local OpenAI-compatible LLM (`--llm`)

## What it does not do
- **It does not crawl or scrape the dark web or Tor itself, and it does not download breach data.**
- It does not change passwords, cancel cards, or log in to services. **You perform the final steps yourself.**
- It does not handle bank or card-company credentials.

### Why we do not crawl the dark web ourselves
- Keeping breach data on hand creates a new leak risk in itself and can raise legal problems.
- Connecting to criminal forums carries the risk of malware and tracking.
- It is more accurate and safer to leave it to specialist services that handle the data responsibly, such as HIBP.

## Data handling
- Records are stored only in `~/.leakwatch/state.json` (permission 600). The only thing sent externally is your email address to the API used for the check.
- API keys are read from an environment variable or the macOS Keychain. They are never displayed or recorded.
- Encrypted storage is not supported (future work). Enable disk encryption (e.g. FileVault).
- The LLM is used only when `LEAKWATCH_LLM_URL` is set. A local server is recommended.

## Usage
```
pip install -e .
leakwatch add you@example.com
leakwatch check --source mock      # smoke test without a key (pwned@example.com is a mocked breached address)
leakwatch check                    # HIBP (requires HIBP_API_KEY)
leakwatch status
leakwatch done you@example.com:Adobe
leakwatch guide google
leakwatch password                 # input is not displayed on screen
leakwatch mail suspicious.eml --llm
leakwatch sources
```

Get your own HIBP API key from https://haveibeenpwned.com/API/Key and set it either way:
- Environment variable `HIBP_API_KEY`
- Keychain: `security add-generic-password -s leakwatch-jp -a HIBP_API_KEY -w` (you will be prompted for the value)

Local LLM (example): `LEAKWATCH_LLM_URL=http://127.0.0.1:18080/v1 LEAKWATCH_LLM_MODEL=glm-5.3-flash`

## Adding sources
Implement `BreachSource` in `leakwatch/sources/` and register it in `REGISTRY`. SpyCloud and Flare are stubs only (not implemented).

## Response-step data
`leakwatch/data/playbooks.json`. Links and phone numbers are never written on guesswork. Anything unverified is marked `verified: false` and shown as "unconfirmed".

## License
AGPL-3.0. For companies that cannot use AGPL terms, a separate commercial license is planned by negotiation.
