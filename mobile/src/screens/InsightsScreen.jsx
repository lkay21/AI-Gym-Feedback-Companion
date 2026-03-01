import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { useMemo, useState } from "react";
import {
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import Svg, { Circle, Path } from "react-native-svg";
import MenuDropdown from "../components/MenuDropdown";

/**
 * Notes:
 * - No backend; all values are mocked.
 * - Uses react-native-svg (already standard in Expo).
 * - Layout mirrors your “glass card” style from the ChatBot example.
 */

const TABS = ["Day", "Week", "Month", "Year", "All Time"];

export default function InsightsScreen({ navigation }) {
  const [tab, setTab] = useState("Week");
  const [input, setInput] = useState("");

  // Mock bar data (Week view)
  const bars = useMemo(
    () => [
      { label: "Week 1", value: 82 },
      { label: "Week 2", value: 68 },
      { label: "Week 3", value: 54 },
      { label: "Week 4", value: 61 },
      { label: "Week 5", value: 63 },
      { label: "Week 6", value: 58 },
      { label: "Week 7", value: 60 },
      { label: "Week 8", value: 57 },
    ],
    []
  );

  // Mock stat cards
  const steps = 23456;
  const trainingMinutes = 90;

  // Mock “calories burned” blurb
  const caloriesBlurb = "Based on distance and\nweight";

  // Mock goal progress
  const goalProgress = 0.5;

  // Mock workout breakdown (sums to 100)
  const workoutBreakdown = useMemo(
    () => [
      { label: "Strength", value: 45, color: "#F2A900" },
      { label: "Cardio", value: 30, color: "#1FA0FF" },
      { label: "Mobility", value: 15, color: "#18C58F" },
      { label: "HIIT", value: 10, color: "#E6E04A" },
    ],
    []
  );

  const handleSend = () => {
    const t = input.trim();
    if (!t) return;
    setInput("");
    navigation.navigate("ChatBot", { q: t });
  };

  return (
    <LinearGradient
      colors={["#4C76D6", "#8E5AAE"]}
      start={{ x: 0.15, y: 0.1 }}
      end={{ x: 0.85, y: 0.95 }}
      style={styles.gradient}
    >
      <SafeAreaView style={styles.safe}>
        <KeyboardAvoidingView
          style={styles.safe}
          behavior={Platform.OS === "ios" ? "padding" : undefined}
          keyboardVerticalOffset={Platform.OS === "ios" ? 8 : 0}
        >
          <View style={styles.card}>
            {/* Top bar */}
            <View style={styles.topBar}>
              <Text style={styles.topLeftLabel}>Insights</Text>
              <MenuDropdown />
            </View>

            {/* Scrollable content (input pill is NOT inside this anymore) */}
            <ScrollView
              style={{ flex: 1 }}
              showsVerticalScrollIndicator={false}
              contentContainerStyle={styles.scrollContent}
              keyboardShouldPersistTaps="handled"
            >
              <Text style={styles.title}>Your Insights</Text>

              {/* Segmented control */}
              <SegmentedControl options={TABS} value={tab} onChange={setTab} />

              {/* Bar chart */}
              <View style={styles.chartWrap}>
                <BarChart data={bars} goalPercent={0.62} goalLabel="Goal: 44 kg" />
              </View>

              {/* Cards row 1 */}
              <View style={styles.row}>
                <StatCard
                  title="Steps"
                  leftIcon={<FootprintsIcon />}
                  value={`${steps}`}
                  valueSuffix="steps"
                  style={{ flex: 1 }}
                />

                <StatCard
                  title="Training"
                  value={`${trainingMinutes}`}
                  valueSuffix="minutes"
                  style={{ flex: 1 }}
                />
              </View>

              {/* Cards row 2 */}
              <View style={styles.row}>
                <MiniCard
                  title="Calories burned"
                  icon={<FlameIcon />}
                  body={caloriesBlurb}
                  style={{ flex: 1 }}
                />

                <View style={[styles.miniCard, { flex: 1 }]}>
                  <Text style={styles.miniTitle}>Goal Progress:</Text>
                  <View style={{ height: 10 }} />
                  <View style={{ alignItems: "center", justifyContent: "center" }}>
                    <DonutProgress
                      size={62}
                      strokeWidth={10}
                      progress={goalProgress}
                      trackColor="rgba(255,255,255,0.18)"
                      progressColor="rgba(255,255,255,0.92)"
                    />
                    <View style={styles.donutCenter}>
                      <Text style={styles.donutText}>
                        {Math.round(goalProgress * 100)}%
                      </Text>
                    </View>
                  </View>
                </View>
              </View>

              {/* Workout type breakdown */}
              <View style={styles.breakdownCard}>
                <Text style={styles.breakdownTitle}>Workout Type Breakdown</Text>
                <View style={styles.breakdownBody}>
                  <View style={{ width: 170, alignItems: "center" }}>
                    <PieChart
                      size={150}
                      innerRadius={0}
                      data={workoutBreakdown}
                      strokeColor="rgba(255,255,255,0.20)"
                      strokeWidth={1}
                    />
                  </View>

                  <View style={{ flex: 1, paddingLeft: 12 }}>
                    {workoutBreakdown.map((s) => (
                      <LegendRow
                        key={s.label}
                        color={s.color}
                        label={s.label}
                        value={`${s.value}%`}
                      />
                    ))}
                  </View>
                </View>
              </View>
            </ScrollView>

            {/* Bottom input pill (fixed + lifts above keyboard) */}
            <View style={styles.inputWrap}>
              <View style={styles.inputPill}>
                <TextInput
                  value={input}
                  onChangeText={setInput}
                  placeholder="Enter Your Prompt Here..."
                  placeholderTextColor="rgba(0,0,0,0.45)"
                  style={styles.input}
                  returnKeyType="send"
                  onSubmitEditing={handleSend}
                />
                <Pressable onPress={handleSend} style={styles.sendBtn}>
                  <Ionicons name="arrow-up" size={18} color="#fff" />
                </Pressable>
              </View>
            </View>
          </View>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </LinearGradient>
  );
}

/* ----------------------------- UI Pieces ----------------------------- */

function SegmentedControl({ options, value, onChange }) {
  return (
    <View style={styles.segmentWrap}>
      {options.map((opt) => {
        const active = opt === value;
        return (
          <Pressable
            key={opt}
            onPress={() => onChange(opt)}
            style={[styles.segmentItem, active && styles.segmentItemActive]}
          >
            <Text style={[styles.segmentText, active && styles.segmentTextActive]}>
              {opt}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

function BarChart({ data, goalPercent = 0.6, goalLabel = "Goal" }) {
  const max = Math.max(...data.map((d) => d.value), 1);
  const goalY = 1 - clamp(goalPercent, 0, 1);

  return (
    <View style={styles.barChartCard}>
      <View style={styles.barChartArea}>
        {/* Goal line */}
        <View style={[styles.goalLine, { top: `${goalY * 100}%` }]}>
          <View style={styles.goalTag}>
            <Text style={styles.goalTagText}>{goalLabel}</Text>
          </View>
        </View>

        <View style={styles.barsRow}>
          {data.map((d) => {
            const h = (d.value / max) * 100;
            return (
              <View key={d.label} style={styles.barCol}>
                <View style={styles.barTrack}>
                  <View style={[styles.barFill, { height: `${h}%` }]} />
                </View>
                <Text style={styles.barLabel} numberOfLines={1}>
                  {d.label}
                </Text>
              </View>
            );
          })}
        </View>
      </View>
    </View>
  );
}

function StatCard({ title, value, valueSuffix, leftIcon, style }) {
  return (
    <View style={[styles.statCard, style]}>
      <View style={styles.statTopRow}>
        <Text style={styles.statTitle}>{title}</Text>
        {leftIcon ? <View style={{ marginLeft: 8 }}>{leftIcon}</View> : null}
      </View>

      <View style={{ height: 12 }} />
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statSuffix}>{valueSuffix}</Text>
    </View>
  );
}

function MiniCard({ title, icon, body, style }) {
  return (
    <View style={[styles.miniCard, style]}>
      <View style={styles.miniTopRow}>
        <View style={styles.iconPill}>{icon}</View>
      </View>
      <Text style={styles.miniTitle}>{title}</Text>
      <View style={{ height: 6 }} />
      <Text style={styles.miniBody}>{body}</Text>
    </View>
  );
}

function LegendRow({ color, label, value }) {
  return (
    <View style={styles.legendRow}>
      <View style={[styles.legendDot, { backgroundColor: color }]} />
      <Text style={styles.legendLabel}>{label}</Text>
      <View style={{ flex: 1 }} />
      <Text style={styles.legendValue}>{value}</Text>
    </View>
  );
}

/* ----------------------------- Icons ----------------------------- */

function FlameIcon() {
  return <Ionicons name="flame" size={16} color="rgba(255,255,255,0.95)" />;
}
function FootprintsIcon() {
  return <Ionicons name="footsteps" size={16} color="rgba(255,255,255,0.95)" />;
}

/* ----------------------------- SVG Charts ----------------------------- */

function DonutProgress({
  size = 64,
  strokeWidth = 10,
  progress = 0.5,
  trackColor = "rgba(255,255,255,0.20)",
  progressColor = "white",
}) {
  const r = (size - strokeWidth) / 2;
  const c = 2 * Math.PI * r;
  const p = clamp(progress, 0, 1);
  const dash = c * p;
  const gap = c - dash;

  return (
    <Svg width={size} height={size}>
      <Circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        stroke={trackColor}
        strokeWidth={strokeWidth}
        fill="transparent"
      />
      <Circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        stroke={progressColor}
        strokeWidth={strokeWidth}
        fill="transparent"
        strokeLinecap="round"
        strokeDasharray={`${dash} ${gap}`}
        rotation={-90}
        originX={size / 2}
        originY={size / 2}
      />
    </Svg>
  );
}

function PieChart({
  size = 150,
  innerRadius = 0,
  data = [],
  strokeColor = "rgba(255,255,255,0.18)",
  strokeWidth = 1,
}) {
  const total = data.reduce((s, d) => s + d.value, 0) || 1;
  const rOuter = size / 2;
  const rInner = clamp(innerRadius, 0, rOuter - 1);

  let startAngle = -90;
  const center = { x: rOuter, y: rOuter };

  return (
    <Svg width={size} height={size}>
      {data.map((slice) => {
        const sweep = (slice.value / total) * 360;
        const endAngle = startAngle + sweep;

        const path =
          rInner > 0
            ? describeDonutSlice(center.x, center.y, rOuter, rInner, startAngle, endAngle)
            : describePieSlice(center.x, center.y, rOuter, startAngle, endAngle);

        startAngle = endAngle;

        return (
          <Path
            key={`${slice.label}_${slice.value}`}
            d={path}
            fill={slice.color}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
          />
        );
      })}

      {rInner > 0 ? (
        <Circle cx={center.x} cy={center.y} r={rInner} fill="rgba(255,255,255,0.08)" />
      ) : null}
    </Svg>
  );
}

/* ----------------------------- SVG Path Math ----------------------------- */

function polarToCartesian(cx, cy, r, angleDeg) {
  const a = (Math.PI / 180) * angleDeg;
  return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
}

function describePieSlice(cx, cy, r, startAngle, endAngle) {
  const start = polarToCartesian(cx, cy, r, endAngle);
  const end = polarToCartesian(cx, cy, r, startAngle);
  const largeArc = endAngle - startAngle > 180 ? 1 : 0;

  return [
    `M ${cx} ${cy}`,
    `L ${end.x} ${end.y}`,
    `A ${r} ${r} 0 ${largeArc} 1 ${start.x} ${start.y}`,
    "Z",
  ].join(" ");
}

function describeDonutSlice(cx, cy, rOuter, rInner, startAngle, endAngle) {
  const p1 = polarToCartesian(cx, cy, rOuter, startAngle);
  const p2 = polarToCartesian(cx, cy, rOuter, endAngle);
  const p3 = polarToCartesian(cx, cy, rInner, endAngle);
  const p4 = polarToCartesian(cx, cy, rInner, startAngle);

  const largeArc = endAngle - startAngle > 180 ? 1 : 0;

  return [
    `M ${p1.x} ${p1.y}`,
    `A ${rOuter} ${rOuter} 0 ${largeArc} 1 ${p2.x} ${p2.y}`,
    `L ${p3.x} ${p3.y}`,
    `A ${rInner} ${rInner} 0 ${largeArc} 0 ${p4.x} ${p4.y}`,
    "Z",
  ].join(" ");
}

function clamp(n, a, b) {
  return Math.max(a, Math.min(b, n));
}

/* ----------------------------- Styles ----------------------------- */

const styles = StyleSheet.create({
  gradient: { flex: 1 },
  safe: { flex: 1 },

  card: {
    flex: 1,
    marginHorizontal: 16,
    marginTop: 10,
    marginBottom: 14,
    borderRadius: 28,
    paddingTop: 12,
    paddingHorizontal: 14,
    backgroundColor: "rgba(255,255,255,0.14)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.18)",
    overflow: "hidden",
  },

  topBar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 6,
    paddingBottom: 8,
  },
  topLeftLabel: {
    color: "rgba(255,255,255,0.75)",
    fontSize: 14,
    letterSpacing: 0.2,
  },

  // IMPORTANT: give room for the fixed input pill
  scrollContent: {
    paddingHorizontal: 4,
    paddingBottom: 18,
  },

  title: {
    color: "rgba(255,255,255,0.96)",
    fontSize: 24,
    fontWeight: "700",
    alignSelf: "center",
    marginTop: 6,
    marginBottom: 12,
  },

  /* Segmented */
  segmentWrap: {
    flexDirection: "row",
    alignSelf: "center",
    backgroundColor: "rgba(255,255,255,0.70)",
    borderRadius: 999,
    padding: 4,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.45)",
  },
  segmentItem: {
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 999,
  },
  segmentItemActive: {
    backgroundColor: "rgba(0,0,0,0.16)",
  },
  segmentText: {
    fontSize: 12,
    color: "rgba(0,0,0,0.55)",
    fontWeight: "600",
  },
  segmentTextActive: {
    color: "rgba(0,0,0,0.85)",
  },

  /* Chart */
  chartWrap: {
    marginTop: 14,
    marginBottom: 12,
  },
  barChartCard: {
    borderRadius: 18,
    backgroundColor: "rgba(255,255,255,0.10)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.16)",
    padding: 12,
  },
  barChartArea: {
    height: 170,
    position: "relative",
  },
  goalLine: {
    position: "absolute",
    left: 6,
    right: 6,
    height: 1,
    backgroundColor: "rgba(255,255,255,0.55)",
    zIndex: 3,
  },
  goalTag: {
    position: "absolute",
    right: 0,
    top: -12,
    paddingVertical: 4,
    paddingHorizontal: 8,
    borderRadius: 999,
    backgroundColor: "rgba(0,0,0,0.24)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.20)",
  },
  goalTagText: {
    color: "rgba(255,255,255,0.95)",
    fontSize: 11,
    fontWeight: "700",
  },

  barsRow: {
    flexDirection: "row",
    alignItems: "flex-end",
    height: "100%",
    gap: 8,
    paddingTop: 6,
  },
  barCol: {
    flex: 1,
    alignItems: "center",
    justifyContent: "flex-end",
  },
  barTrack: {
    width: "70%",
    height: "86%",
    borderRadius: 10,
    backgroundColor: "rgba(255,255,255,0.10)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.12)",
    overflow: "hidden",
    justifyContent: "flex-end",
  },
  barFill: {
    width: "100%",
    borderRadius: 10,
    backgroundColor: "rgba(90, 0, 170, 0.55)",
  },
  barLabel: {
    marginTop: 6,
    fontSize: 10,
    color: "rgba(255,255,255,0.55)",
    maxWidth: 46,
  },

  /* Rows & cards */
  row: {
    flexDirection: "row",
    gap: 12,
    marginTop: 12,
  },
  statCard: {
    borderRadius: 18,
    padding: 14,
    backgroundColor: "rgba(255,255,255,0.12)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.16)",
    minHeight: 105,
  },
  statTopRow: {
    flexDirection: "row",
    alignItems: "center",
  },
  statTitle: {
    color: "rgba(255,255,255,0.90)",
    fontSize: 14,
    fontWeight: "800",
  },
  statValue: {
    color: "rgba(255,255,255,0.98)",
    fontSize: 22,
    fontWeight: "900",
    letterSpacing: 0.2,
  },
  statSuffix: {
    color: "rgba(255,255,255,0.70)",
    fontSize: 12,
    marginTop: 2,
    fontWeight: "700",
  },

  miniCard: {
    borderRadius: 18,
    padding: 14,
    backgroundColor: "rgba(0,0,0,0.22)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.16)",
    minHeight: 110,
  },
  miniTopRow: {
    flexDirection: "row",
    justifyContent: "flex-start",
  },
  iconPill: {
    width: 34,
    height: 34,
    borderRadius: 999,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(255,255,255,0.10)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.14)",
  },
  miniTitle: {
    marginTop: 10,
    color: "rgba(255,255,255,0.92)",
    fontSize: 13,
    fontWeight: "800",
  },
  miniBody: {
    color: "rgba(255,255,255,0.70)",
    fontSize: 12,
    lineHeight: 16,
    fontWeight: "600",
  },

  donutCenter: {
    position: "absolute",
    width: 62,
    height: 62,
    alignItems: "center",
    justifyContent: "center",
  },
  donutText: {
    color: "rgba(255,255,255,0.95)",
    fontSize: 13,
    fontWeight: "900",
  },

  /* Breakdown */
  breakdownCard: {
    marginTop: 12,
    borderRadius: 18,
    backgroundColor: "rgba(255,255,255,0.10)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.16)",
    padding: 12,
  },
  breakdownTitle: {
    color: "rgba(255,255,255,0.92)",
    fontSize: 13,
    fontWeight: "800",
    textAlign: "center",
    marginBottom: 10,
  },
  breakdownBody: {
    flexDirection: "row",
    alignItems: "center",
  },

  legendRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 6,
  },
  legendDot: {
    width: 10,
    height: 10,
    borderRadius: 99,
    marginRight: 10,
  },
  legendLabel: {
    color: "rgba(255,255,255,0.88)",
    fontSize: 12,
    fontWeight: "700",
  },
  legendValue: {
    color: "rgba(255,255,255,0.70)",
    fontSize: 12,
    fontWeight: "700",
  },

  /* Fixed input pill */
  inputWrap: {
    paddingTop: 10,
    paddingBottom: 14,
    paddingHorizontal: 2,
  },
  inputPill: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "rgba(255,255,255,0.95)",
    borderRadius: 999,
    paddingLeft: 16,
    paddingRight: 10,
    height: 54,
  },
  input: {
    flex: 1,
    fontSize: 14,
    color: "#111",
    paddingRight: 10,
  },
  sendBtn: {
    width: 38,
    height: 38,
    borderRadius: 999,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#6D5ACF",
  },
});