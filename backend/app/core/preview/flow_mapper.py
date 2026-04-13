from app.models import EnrichedContext, UserFlow, FlowNode
import uuid


def build_flows(ctx: EnrichedContext) -> list[UserFlow]:
    flows = []
    eligible = [p for p in ctx.personas if p.power_level in ("champion", "key_player")]

    for persona in eligible[:3]:  # max 3 flows
        nodes = []
        nid = lambda label: str(uuid.uuid4())[:8]

        trigger_id = nid("trigger")
        nodes.append(FlowNode(id=trigger_id, type="TRIGGER", label=persona.entry_trigger, next_ids=[]))

        prev_id = trigger_id

        if ctx.tech_profile.needs_auth:
            login_id = nid("login")
            auth_id = nid("auth")
            dash_id = nid("dash")
            nodes.append(FlowNode(id=login_id, type="SCREEN", label="Login Screen", next_ids=[auth_id]))
            nodes.append(FlowNode(id=auth_id, type="DECISION", label="Authenticated?", next_ids=[dash_id]))
            nodes.append(FlowNode(id=dash_id, type="SCREEN", label="Dashboard", next_ids=[]))
            nodes[-3].next_ids = [auth_id]
            nodes[-2].next_ids = [dash_id]
            nodes[0].next_ids = [login_id]
            prev_id = dash_id

        must_features = [f for f in ctx.features if f.moscow == "must" and persona.id in f.related_persona_ids]
        if not must_features:
            must_features = [f for f in ctx.features if f.moscow == "must"][:1]

        for feature in must_features[:2]:
            screen_id = nid("screen")
            action_id = nid("action")
            system_id = nid("system")

            if ctx.tech_profile.needs_payments and feature.moscow == "must":
                payment_id = nid("payment")
                outcome_id = nid("outcome")
                nodes.append(FlowNode(id=screen_id, type="SCREEN", label=feature.name, next_ids=[action_id]))
                nodes.append(FlowNode(id=action_id, type="ACTION", label=f"Submit {feature.name}", next_ids=[system_id]))

                if "DOHERTY" in feature.ux_flags:
                    loading_id = nid("loading")
                    nodes.append(FlowNode(id=system_id, type="SYSTEM", label="Process (with loading state)", next_ids=[payment_id]))
                    nodes.append(FlowNode(id=loading_id, type="SYSTEM", label="Loading State", next_ids=[payment_id]))
                else:
                    nodes.append(FlowNode(id=system_id, type="SYSTEM", label="Backend Processing", next_ids=[payment_id]))

                nodes.append(FlowNode(id=payment_id, type="DECISION", label="Payment Required?", next_ids=[outcome_id]))
                nodes.append(FlowNode(id=outcome_id, type="OUTCOME", label=persona.success_signal, next_ids=[]))
            else:
                outcome_id = nid("outcome")
                nodes.append(FlowNode(id=screen_id, type="SCREEN", label=feature.name, next_ids=[action_id]))
                nodes.append(FlowNode(id=action_id, type="ACTION", label=f"Complete {feature.name}", next_ids=[system_id]))

                if "DOHERTY" in feature.ux_flags:
                    nodes.append(FlowNode(id=system_id, type="SYSTEM", label="Processing (loading state shown)", next_ids=[outcome_id]))
                else:
                    nodes.append(FlowNode(id=system_id, type="SYSTEM", label="Backend Operation", next_ids=[outcome_id]))

                nodes.append(FlowNode(id=outcome_id, type="OUTCOME", label=persona.success_signal, next_ids=[]))

            # Connect prev to screen
            for n in nodes:
                if n.id == prev_id:
                    n.next_ids = [screen_id]
                    break
            prev_id = outcome_id

        flows.append(UserFlow(
            persona_id=persona.id,
            persona_name=persona.name,
            nodes=nodes,
        ))

    return flows
