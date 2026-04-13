from app.models import EnrichedContext, ScreenSpec, WireframeZone, CTASpec


def derive_screens(ctx: EnrichedContext) -> list[ScreenSpec]:
    screens = []

    def make_id(name: str) -> str:
        return name.lower().replace(" ", "-")

    # Always: Landing / Home
    screens.append(ScreenSpec(
        id="landing",
        name="Landing Page",
        accessible_by=["all"],
        purpose="Introduce the app and drive sign-up or entry",
        zones=[
            WireframeZone(type="NAV", description="Logo + navigation links", y=0, height=60),
            WireframeZone(type="HERO", description="Headline + sub-headline + primary CTA", y=60, height=200),
            WireframeZone(type="FEATURES", description="3-column feature highlights", y=260, height=160),
            WireframeZone(type="FOOTER", description="Links + copyright", y=420, height=80),
        ],
        primary_cta=CTASpec(label="Get Started", action="navigate_to_signup", loading_label="Loading..."),
        responsive={"mobile": "Single column, hamburger nav", "tablet": "Two column", "desktop": "Full layout"},
    ))

    # Auth screens if needed
    if ctx.tech_profile.needs_auth:
        screens.append(ScreenSpec(
            id="login",
            name="Login",
            accessible_by=["all"],
            purpose="Authenticate returning users",
            zones=[
                WireframeZone(type="NAV", description="Logo only", y=0, height=60),
                WireframeZone(type="FORM", description="Email + password fields + submit", y=80, height=200),
                WireframeZone(type="LINKS", description="Forgot password + Sign up link", y=280, height=40),
            ],
            primary_cta=CTASpec(
                label="Sign In",
                action="authenticate",
                loading_label="Signing in...",
                success_state="Redirecting...",
                error_message="Invalid credentials",
            ),
            responsive={"mobile": "Full screen form", "tablet": "Centered card", "desktop": "Centered card 400px wide"},
        ))

        screens.append(ScreenSpec(
            id="signup",
            name="Sign Up",
            accessible_by=["all"],
            purpose="Register new users",
            zones=[
                WireframeZone(type="NAV", description="Logo only", y=0, height=60),
                WireframeZone(type="FORM", description="Name + email + password + confirm", y=80, height=240),
                WireframeZone(type="CTA", description="Create account button", y=320, height=50),
            ],
            primary_cta=CTASpec(
                label="Create Account",
                action="register",
                loading_label="Creating account...",
                success_state="Welcome!",
                error_message="Account creation failed",
            ),
            responsive={"mobile": "Full screen form", "tablet": "Centered card", "desktop": "Centered card 440px wide"},
        ))

    # Dashboard
    champion_personas = [p for p in ctx.personas if p.power_level in ("champion", "key_player")]
    accessible_by = [p.role for p in champion_personas] if champion_personas else ["all users"]

    screens.append(ScreenSpec(
        id="dashboard",
        name="Dashboard",
        accessible_by=accessible_by,
        purpose="Primary hub showing key metrics and quick actions",
        zones=[
            WireframeZone(type="NAV", description="Top navigation + user avatar", y=0, height=60),
            WireframeZone(type="STATS", description="3\u20134 key metric cards", y=60, height=120),
            WireframeZone(type="LIST", description="Recent activity or primary data list", y=180, height=300),
            WireframeZone(type="CTA", description="Primary action button (FAB on mobile)", y=480, height=60),
        ],
        primary_cta=CTASpec(
            label="New " + (ctx.features[0].name if ctx.features else "Item"),
            action="create_item",
        ),
        ux_flags=["EMPTY_STATE"],
        empty_state_message="Nothing here yet",
        empty_state_cta="Create your first " + (ctx.features[0].name.lower() if ctx.features else "item"),
        responsive={"mobile": "Single column, bottom nav, FAB", "tablet": "Two column grid", "desktop": "Sidebar + main content"},
    ))

    # One screen per must-have feature
    must_have = [f for f in ctx.features if f.moscow == "must"]
    for feature in must_have[:8]:  # cap at 8
        flags = feature.ux_flags
        zones = [WireframeZone(type="NAV", description="Back button + screen title", y=0, height=60)]

        if "EMPTY_STATE" in flags or True:
            zones.append(WireframeZone(type="LIST", description=f"{feature.name} items list", y=60, height=320))

        if "ZEIGARNIK" in flags:
            zones.append(WireframeZone(type="PROGRESS", description="Step indicator / progress bar", y=380, height=40))

        zones.append(WireframeZone(type="CTA", description="Primary action for this feature", y=420, height=60))

        screens.append(ScreenSpec(
            id=make_id(feature.name),
            name=feature.name,
            accessible_by=[p for p in feature.related_persona_ids] or accessible_by,
            purpose=feature.description,
            zones=zones,
            primary_cta=CTASpec(
                label=feature.name,
                action=f"submit_{feature.id}",
                loading_label="Processing...",
                success_state="Done!",
                error_message=f"Could not complete {feature.name.lower()}. Try again.",
            ),
            ux_flags=flags,
            empty_state_message=f"No {feature.name.lower()} yet" if "EMPTY_STATE" in flags else None,
            empty_state_cta=f"Add your first {feature.name.lower()}" if "EMPTY_STATE" in flags else None,
            responsive={
                "mobile": "Single column, 320px",
                "tablet": "Two-column layout, 768px",
                "desktop": "Full width, 1280px",
            },
        ))

    # Payment screens if needed
    if ctx.tech_profile.needs_payments:
        screens.append(ScreenSpec(
            id="checkout",
            name="Checkout",
            accessible_by=accessible_by,
            purpose="Complete payment transaction",
            zones=[
                WireframeZone(type="NAV", description="Back + progress (step 2 of 2)", y=0, height=60),
                WireframeZone(type="SUMMARY", description="Order summary card", y=60, height=120),
                WireframeZone(type="PAYMENT", description="Stripe payment element", y=180, height=200),
                WireframeZone(type="CTA", description="Pay now button", y=380, height=60),
            ],
            primary_cta=CTASpec(
                label="Pay Now",
                action="submit_payment",
                loading_label="Processing payment...",
                success_state="Payment successful!",
                error_message="Payment failed. Please try again.",
            ),
            ux_flags=["ZEIGARNIK", "DOHERTY"],
            responsive={"mobile": "Single column", "tablet": "Centered 600px", "desktop": "Centered 600px"},
        ))

    # Settings / Profile
    screens.append(ScreenSpec(
        id="settings",
        name="Settings",
        accessible_by=accessible_by,
        purpose="User profile and app preferences",
        zones=[
            WireframeZone(type="NAV", description="Back + title", y=0, height=60),
            WireframeZone(type="PROFILE", description="Avatar + name + email", y=60, height=120),
            WireframeZone(type="SECTIONS", description="Settings groups (account, notifications, etc.)", y=180, height=300),
            WireframeZone(type="DANGER", description="Log out / Delete account (red zone)", y=480, height=80),
        ],
        responsive={"mobile": "List view", "tablet": "Two-column", "desktop": "Sidebar navigation"},
    ))

    return screens
