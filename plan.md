## Drishti Printing - Feature Plan and Status

### Overview
- Technology: Django (MVT), Tailwind CSS, Konva-based design tool, Pixabay API
- Scope: Printing service site with dynamic homepage, products with pricing, design tool, orders, user profiles, and blog

### Status at a Glance
- Hero slider (admin-managed): Pending → now implementing
- Best 4 bestsellers on home: Implemented (context + template)
- Dedicated product pages with price calculator: Partially implemented (UI present, logic partial)
- Subcategories on parent product pages: Implemented (category view + template)
- “No design? No problem” section: Implemented
- Designable products section on home: Implemented
- Product actions: Upload design / Design now: Partially implemented (design now exists; upload flow not wired to cart/order)
- Front/back selection in design flow: Partially implemented in design_tool (supports front/back via API), missing UI trigger
- User accounts and profile: Implemented (profile shows recent orders; designs listing missing)
- Orders/cart/checkout: Implemented basic models and views; integration with uploads/designs partial
- Blog pages for SEO: Implemented (model, admin, list view/template)

### Gaps to Complete
1) Admin-managed Hero Slider on homepage
2) Pricing calculator logic for non-designable products; compute price from options
3) Product pages: show both actions clearly (Upload design, Design now) and wire uploads to cart
4) Front/back selection modal before entering editor when applicable
5) Profile: add “My Designs” section listing `UserDesign` items
6) Quote flow for non-standard specs; persist quote requests

### Implementation Checklist
- [ ] Admin-managed Hero Slider (model, admin, context, template loop)
- [ ] Pricing calculator service + UI bindings on `templates/products/detail.html`
- [ ] Product actions: Upload design → save file(s) to cart item `design_files`
- [ ] Front/back selection modal on designable products → pass mode to editor
- [ ] Profile: add user designs list to `users/profile.html`
- [ ] Quote request endpoint and template wiring
- [x] Bestsellers and designable products on home
- [x] Subcategories listing on category page
- [x] Blog list and admin posting

### Next Actions
1) Finish Hero Slider admin feature and migrate data
2) Implement pricing calculation endpoint and JavaScript integration
3) Implement upload-to-cart on product detail page
4) Add front/back selection modal and route to `design_tool:editor`
5) Extend profile to show saved designs

