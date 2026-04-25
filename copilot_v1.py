import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Trading Copilot", layout="centered")

st.title("📱 Trading Copilot V4")

# ━━━━━━━━━━━━━━━━━━━━
# STEP 1 — TSL
# ━━━━━━━━━━━━━━━━━━━━
tsl_flip = st.checkbox("🔁 TSL Flip (Required)")

# ━━━━━━━━━━━━━━━━━━━━
# STEP 2 — MODE
# ━━━━━━━━━━━━━━━━━━━━
mode = st.radio("Mode", ["Range", "Breakout"], horizontal=True)

# ━━━━━━━━━━━━━━━━━━━━
# STEP 3 — RANGE SETUPS (MULTI SELECT FIXED)
# ━━━━━━━━━━━━━━━━━━━━
range_setups = []
touch_count = 0

if mode == "Range":
    st.subheader("Range Setup")

    cons = st.checkbox("📊 Consolidation")
    bb = st.checkbox("📉 Bollinger Buy")
    retr = st.checkbox("🔄 Retracement")

    touch_count = st.slider("Touches", 0, 10, 3)

    if cons:
        range_setups.append("Consolidation")
    if bb:
        range_setups.append("Bollinger Buy")
    if retr:
        range_setups.append("Retracement")

# ━━━━━━━━━━━━━━━━━━━━
# STEP 4 — BREAKOUT SETUPS
# ━━━━━━━━━━━━━━━━━━━━
breakout_setups = []

if mode == "Breakout":
    st.subheader("Breakout Setup")

    tl = st.checkbox("📈 Trendline Break")
    sq = st.checkbox("💥 Squeeze")

    if tl:
        breakout_setups.append("Trendline Break")
    if sq:
        breakout_setups.append("Bollinger Squeeze")

    htf_position = st.radio(
        "HTF Position",
        ["above_078", "below_0216", "neutral"],
        horizontal=True
    )

# ━━━━━━━━━━━━━━━━━━━━
# TRADE INPUTS
# ━━━━━━━━━━━━━━━━━━━━
st.subheader("Trade Levels")

entry = st.number_input("Entry", value=0.0)
stop = st.number_input("Stop Loss", value=0.0)
target = st.number_input("Final Target", value=0.0)

nearest_target = st.number_input(
    "Nearest Structure Target (Opp Zone / Fib 0.6)",
    value=0.0
)

view = st.text_area("Your View (optional)")

# ━━━━━━━━━━━━━━━━━━━━
# EVALUATION FUNCTION
# ━━━━━━━━━━━━━━━━━━━━
def evaluate():

    score = 0
    reasons = []

    # TSL
    if not tsl_flip:
        return "REJECTED", ["❌ No TSL flip"], 0, 0

    reasons.append("✔ TSL Flip")

    # RANGE MODE
    if mode == "Range":

        if len(range_setups) == 0:
            return "REJECTED", ["❌ No range setup selected"], 0, score

        if "Consolidation" in range_setups:
            if touch_count >= 5:
                score += 3
                reasons.append("🔥 Strong consolidation (5+ touches)")
            elif touch_count >= 3:
                score += 2
                reasons.append("✔ Valid consolidation")
            else:
                reasons.append("⚠ Weak consolidation")

        if "Bollinger Buy" in range_setups:
            score += 2
            reasons.append("✔ Bollinger signal")

        if "Retracement" in range_setups:
            score += 1
            reasons.append("✔ Retracement")

    # BREAKOUT MODE
    if mode == "Breakout":

        if len(breakout_setups) == 0:
            return "REJECTED", ["❌ No breakout setup selected"], 0, score

        if "Trendline Break" in breakout_setups:
            score += 2
            reasons.append("✔ Trendline break")

        if "Bollinger Squeeze" in breakout_setups:
            score += 2
            reasons.append("✔ Squeeze")

        if htf_position in ["above_078", "below_0216"]:
            score += 1
            reasons.append("✔ HTF aligned")
        else:
            reasons.append("⚠ HTF weak")

    # RISK REWARD
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = reward / risk if risk != 0 else 0

    if rr >= 2:
        score += 2
        reasons.append("✔ Good RR")
    elif rr >= 1.5:
        score += 1
        reasons.append("⚠ Moderate RR")
    else:
        reasons.append("✖ Poor RR")

    # STRUCTURE DISTANCE (CRITICAL FILTER)
    structure_dist = abs(nearest_target - entry)

    if structure_dist < risk * 1.2:
        score -= 3
        reasons.append("❌ No room to move")
    elif structure_dist < risk * 1.8:
        score -= 1
        reasons.append("⚠ Tight structure")
    else:
        score += 1
        reasons.append("✔ Good space")

    # LATE ENTRY (optional text)
    if "late" in view.lower():
        score -= 1
        reasons.append("✖ Late entry")

    # FINAL DECISION
    if score >= 7:
        decision = "🔥 STRONG"
    elif score >= 4:
        decision = "⚠ MODERATE"
    else:
        decision = "❌ WEAK"

    return decision, reasons, rr, score

# ━━━━━━━━━━━━━━━━━━━━
# EXECUTION BUTTON
# ━━━━━━━━━━━━━━━━━━━━
if st.button("🚀 Evaluate Trade", use_container_width=True):

    decision, reasons, rr, score = evaluate()

    st.markdown(f"## {decision}")
    st.write(f"Score: {score} | RR: {round(rr,2)}")

    st.write("### Reasons:")
    for r in reasons:
        st.write(r)

    # DISCIPLINE
    follow = st.radio("Will you follow?", ["Yes", "No"], horizontal=True)

    if follow == "No":
        st.warning("⚠ Overriding system")

    # SAVE LOG
    log = {
        "Time": datetime.now(),
        "Mode": mode,
        "Decision": decision,
        "Score": score,
        "RR": rr,
        "Followed": follow
    }

    df = pd.DataFrame([log])

    try:
        old = pd.read_csv("log.csv")
        df = pd.concat([old, df])
    except:
        pass

    df.to_csv("log.csv", index=False)

    st.success("Trade saved!")

# ━━━━━━━━━━━━━━━━━━━━
# STATS
# ━━━━━━━━━━━━━━━━━━━━
st.subheader("📈 Stats")

try:
    log = pd.read_csv("log.csv")
    st.write("Total Trades:", len(log))
    st.write("Follow Rate:", round((log["Followed"] == "Yes").mean(), 2))
except:
    st.write("No data yet")