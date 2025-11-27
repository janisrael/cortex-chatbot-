# Landing Page Plan

## Objectives
- Present Cortex AI as a premium AI assistant builder for sales and marketing teams.
- Drive conversions to the register/login flow.
- Provide compelling social-sharing metadata (og: tags) for better previews.

## Audience
- Sales/marketing leaders, founders, agencies seeking automated chat support.

## Structure
1. **Hero Section**
   - Glassy/Vista-inspired background, 3D gradients, soft glow.
   - Headline: "Deploy a Sales-Ready AI Agent in Minutes"
   - Subtext: highlight PayPal-integrated subscriptions, knowledge base, widget preview.
   - CTA buttons: `Start Free Trial` (register) and `Watch Demo` (link to /demo).
   - Social proof badges/logos optional.

2. **Key Metrics / Stats Bar**
   - 3 cards (Active Bots, Avg. Response Time, Leads Captured) with animated counters.

3. **Product Highlights**
   - Split layout mirroring login-right panel (glassmorphism card).
   - Features: Knowledge Base, Widget Integration, LLM Orchestration, Real-time Analytics.

4. **Interactive Showcase**
   - Mock chat window or video placeholder showing AI in action.
   - Secondary CTA.

5. **Testimonials / Logos**
   - Quote cards or brand icons.

6. **Pricing Teaser**
   - Emphasize free plan + pay-as-you-grow.
   - CTA linking to register.

7. **FAQ Preview**
   - 3 accordion items tied to product usage.

8. **Final CTA Banner**
   - Background gradient, compelling message to register/login.

## Technical Notes
- Create new template `templates/landing.html`.
- Expose page at `/home` (public, no auth) — keep `/landing` as optional alias if needed.
- Include social meta tags in `<head>` for better sharing.
- Reuse `static/v2/css/dashboard.css` and add dedicated CSS chunk for landing specifics.
- Ensure responsive design (mobile stacked sections).
- Hook hero CTA buttons to `/register` and `/login`.

