
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useEffect, useRef, useState } from "react";

import {
  Animated,
  Image,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import MenuDropdown from "../components/MenuDropdown";

const DEFAULT_CV_RESULT = {
  score: null,
  insight: "Upload a video to receive form insights.",
  exercise: "",
};

const TIPS = [
  { icon: "barbell-outline",     category: "Form",       text: "Keep your core braced during every compound lift — it protects your spine and transfers force efficiently." },
  { icon: "body-outline",        category: "Form",       text: "For squats, push your knees out in line with your toes to avoid valgus collapse." },
  { icon: "barbell-outline",     category: "Form",       text: "On the bench press, retract your shoulder blades before unracking the bar to protect your shoulders." },
  { icon: "body-outline",        category: "Form",       text: "Deadlift tip: the bar should stay in contact with your legs the entire way up." },
  { icon: "barbell-outline",     category: "Form",       text: "Drive through your heels on squats and leg presses, not the balls of your feet." },
  { icon: "body-outline",        category: "Form",       text: "Keep a neutral spine — avoid rounding your lower back on any pulling movement." },
  { icon: "barbell-outline",     category: "Form",       text: "On overhead press, squeeze your glutes to prevent hyperextending your lumbar spine." },
  { icon: "body-outline",        category: "Form",       text: "For pull-ups, initiate the movement by depressing your shoulder blades, not by pulling with your arms." },
  { icon: "barbell-outline",     category: "Form",       text: "Control the eccentric (lowering) phase — 2–3 seconds down builds more muscle than dropping the weight." },
  { icon: "body-outline",        category: "Form",       text: "During rows, lead with your elbows and squeeze your lats at the top, not your biceps." },
  { icon: "barbell-outline",     category: "Form",       text: "On lunges, keep your front shin vertical — a forward-leaning shin puts extra stress on the knee." },
  { icon: "body-outline",        category: "Form",       text: "Breathe in on the eccentric, brace, then exhale forcefully on the concentric (exertion) phase." },
  { icon: "barbell-outline",     category: "Form",       text: "Film yourself from the side to check squat depth and back angle — what you feel isn't always what's happening." },
  { icon: "body-outline",        category: "Form",       text: "For hip hinges, push your hips back — not down — to load the hamstrings correctly." },
  { icon: "barbell-outline",     category: "Form",       text: "Keep your wrists straight and stacked over the bar during pressing movements to avoid joint strain." },
  { icon: "flash-outline",       category: "Training",   text: "Progressive overload is the #1 driver of muscle growth — aim to add a small amount of weight or reps each week." },
  { icon: "flash-outline",       category: "Training",   text: "Compound lifts first, isolation exercises last — your energy is highest at the start of a session." },
  { icon: "flash-outline",       category: "Training",   text: "Rest 2–3 minutes between heavy compound sets and 60–90 seconds between isolation exercises." },
  { icon: "flash-outline",       category: "Training",   text: "Train each muscle group 2× per week for optimal hypertrophy stimulus and recovery." },
  { icon: "flash-outline",       category: "Training",   text: "Warm up with 2–3 progressively heavier sets before your working sets to prime your nervous system." },
  { icon: "flash-outline",       category: "Training",   text: "Deload every 4–6 weeks — reduce volume by ~40% to let joints and connective tissue recover." },
  { icon: "flash-outline",       category: "Training",   text: "Stop 1–2 reps short of failure on most sets to manage fatigue and keep form tight." },
  { icon: "flash-outline",       category: "Training",   text: "Track your workouts — you can't improve what you don't measure." },
  { icon: "flash-outline",       category: "Training",   text: "Mind–muscle connection matters: slow down and focus on feeling the target muscle working." },
  { icon: "flash-outline",       category: "Training",   text: "Supersets with opposing muscle groups (e.g. chest + back) save time without compromising strength." },
  { icon: "heart-outline",       category: "Recovery",   text: "Sleep 7–9 hours — growth hormone peaks during deep sleep and is essential for muscle repair." },
  { icon: "heart-outline",       category: "Recovery",   text: "Active recovery (light walking, swimming, yoga) on rest days reduces soreness faster than complete rest." },
  { icon: "heart-outline",       category: "Recovery",   text: "Foam roll tight areas for 60–90 seconds before training to improve range of motion." },
  { icon: "heart-outline",       category: "Recovery",   text: "DOMS (delayed onset muscle soreness) peaks 24–72 hours after training — it's normal, not a sign of injury." },
  { icon: "heart-outline",       category: "Recovery",   text: "Cold showers post-workout reduce inflammation, but save ice baths for competitions — they blunt hypertrophy signals." },
  { icon: "heart-outline",       category: "Recovery",   text: "Stretch your hip flexors daily if you sit for long periods — tight hips wreck squat depth and lower back health." },
  { icon: "heart-outline",       category: "Recovery",   text: "Massage or percussion therapy on sore muscles increases blood flow and speeds recovery." },
  { icon: "heart-outline",       category: "Recovery",   text: "At least one full rest day per week is non-negotiable — your muscles grow during rest, not during training." },
  { icon: "nutrition-outline",   category: "Nutrition",  text: "Eat 0.7–1g of protein per pound of bodyweight daily to maximize muscle protein synthesis." },
  { icon: "nutrition-outline",   category: "Nutrition",  text: "A pre-workout meal with carbs + protein 1–2 hours before training fuels performance and reduces catabolism." },
  { icon: "nutrition-outline",   category: "Nutrition",  text: "Post-workout protein within 2 hours helps muscle repair — the 'anabolic window' is real but forgiving." },
  { icon: "nutrition-outline",   category: "Nutrition",  text: "Staying hydrated improves strength, endurance, and focus — aim for at least 2–3L of water on training days." },
  { icon: "nutrition-outline",   category: "Nutrition",  text: "Creatine monohydrate is the most research-backed supplement for strength and muscle gains — 3–5g daily." },
  { icon: "nutrition-outline",   category: "Nutrition",  text: "Carbs are not the enemy — they're your muscles' preferred fuel source for high-intensity training." },
  { icon: "nutrition-outline",   category: "Nutrition",  text: "Caffeine (3–6mg/kg) 30–60 min before training is proven to boost strength output and endurance." },
  { icon: "nutrition-outline",   category: "Nutrition",  text: "Prioritize whole foods over supplements — no powder replaces consistent, protein-rich meals." },
  { icon: "walk-outline",        category: "Cardio",     text: "Zone 2 cardio (conversational pace) 2–3× per week improves heart health without eating into recovery." },
  { icon: "walk-outline",        category: "Cardio",     text: "HIIT is efficient but taxing — limit it to 2 sessions per week if you're also lifting heavy." },
  { icon: "walk-outline",        category: "Cardio",     text: "10,000 steps a day is a solid baseline for non-exercise activity that supports fat loss and health." },
  { icon: "walk-outline",        category: "Cardio",     text: "Steady-state cardio after lifting uses stored fat more readily — keep it under 30 min to protect muscle." },
  { icon: "bulb-outline",        category: "Mindset",    text: "Consistency beats intensity — showing up 80% is infinitely better than the perfect program you can't sustain." },
  { icon: "bulb-outline",        category: "Mindset",    text: "Set process goals ('train 4× this week') not just outcome goals ('lose 10lbs') — you control the process." },
  { icon: "bulb-outline",        category: "Mindset",    text: "Plateaus are normal — they're a signal to audit your sleep, nutrition, and program, not to quit." },
  { icon: "bulb-outline",        category: "Mindset",    text: "Compare yourself to who you were last month, not to others online — their journey isn't yours." },
  { icon: "bulb-outline",        category: "Mindset",    text: "The best workout program is the one you'll actually stick to — find what you enjoy and build from there." },
];

const CATEGORY_COLORS = {
  Form:      { bg: "rgba(99,102,241,0.25)",  border: "rgba(99,102,241,0.45)",  text: "#A5B4FC" },
  Training:  { bg: "rgba(251,191,36,0.18)",  border: "rgba(251,191,36,0.38)",  text: "#FCD34D" },
  Recovery:  { bg: "rgba(52,211,153,0.18)",  border: "rgba(52,211,153,0.38)",  text: "#6EE7B7" },
  Nutrition: { bg: "rgba(251,113,133,0.18)", border: "rgba(251,113,133,0.38)", text: "#FCA5A5" },
  Cardio:    { bg: "rgba(56,189,248,0.18)",  border: "rgba(56,189,248,0.38)",  text: "#7DD3FC" },
  Mindset:   { bg: "rgba(167,139,250,0.18)", border: "rgba(167,139,250,0.38)", text: "#C4B5FD" },
};

const getGreeting = () => {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
};

const getScoreColor = (score) => {
  if (score === null) return "rgba(255,255,255,0.25)";
  const n = Number(score);
  if (n >= 80) return "#34D399";
  if (n >= 60) return "#FBBF24";
  return "#F87171";
};

export default function DashboardScreen({ navigation, route }) {
  const [prompt, setPrompt] = useState("");
  const [cvResult, setCvResult] = useState(DEFAULT_CV_RESULT);
  const [tipIndex, setTipIndex] = useState(0);
  const [username, setUsername] = useState("");
  const [todayEvent, setTodayEvent] = useState(undefined); // undefined = loading, null = no plan
  const fadeAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    let isMounted = true;
    const loadData = async () => {
      try {
        const [rawCV, storedUsername, rawPlan] = await Promise.all([
          AsyncStorage.getItem("lastCVResult"),
          AsyncStorage.getItem("username"),
          AsyncStorage.getItem("cachedPlanEvents"),
        ]);
        if (!isMounted) return;
        if (rawCV) setCvResult((prev) => ({ ...prev, ...JSON.parse(rawCV) }));
        if (storedUsername) setUsername(storedUsername);
        if (rawPlan) {
          const today = new Date().toISOString().split("T")[0];
          const events = JSON.parse(rawPlan);
          const event = events.find((e) => e.date === today) || null;
          setTodayEvent(event);
        } else {
          setTodayEvent(null);
        }
      } catch {
        setTodayEvent(null);
      }
    };
    loadData();
    return () => { isMounted = false; };
  }, []);

  useEffect(() => {
    const incoming = route?.params?.cvResult;
    if (!incoming) return;
    const normalized = {
      score: incoming.score ?? null,
      insight: incoming.insight ?? incoming.feedback ?? "Analysis complete.",
      exercise: incoming.exercise ?? "",
    };
    setCvResult((prev) => ({ ...prev, ...normalized }));
    AsyncStorage.setItem("lastCVResult", JSON.stringify(normalized)).catch(() => {});
  }, [route?.params?.cvResult]);

  // Auto-rotate tips every 8 seconds
  useEffect(() => {
    const interval = setInterval(() => changeTip((tipIndex + 1) % TIPS.length), 8000);
    return () => clearInterval(interval);
  }, [tipIndex]);

  const changeTip = (nextIndex) => {
    Animated.timing(fadeAnim, {
      toValue: 0,
      duration: 220,
      useNativeDriver: true,
    }).start(() => {
      setTipIndex(nextIndex);
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 280,
        useNativeDriver: true,
      }).start();
    });
  };

  const onSend = () => {
    const t = prompt.trim();
    if (!t) return;
    setPrompt("");
    navigation.navigate("ChatBot", { q: t });
  };

  const tip = TIPS[tipIndex];
  const colors = CATEGORY_COLORS[tip.category];

  return (
    <LinearGradient
      colors={["#7c3aed", "#6366f1", "#4c1d95"]}
      style={styles.gradient}
    >
      <SafeAreaView style={styles.safe}>
        <KeyboardAvoidingView
          style={styles.safe}
          behavior={Platform.OS === "ios" ? "padding" : undefined}
          keyboardVerticalOffset={Platform.OS === "ios" ? 8 : 0}
        >
          <View style={styles.cardShell}>
            <ScrollView
              style={{ flex: 1 }}
              showsVerticalScrollIndicator={false}
              contentContainerStyle={styles.scrollContent}
              keyboardShouldPersistTaps="handled"
              nestedScrollEnabled={true}
            >
              <View style={styles.topRow}>
                <MenuDropdown />
              </View>

              {/* ── Greeting ── */}
              <View style={styles.greetingRow}>
                <Text style={styles.greeting}>
                  {getGreeting()}{username ? `, ${username}` : ""} 👋
                </Text>
                <Text style={styles.greetingSub}>Fitness Dashboard</Text>
              </View>

              {/* ── Today: Rest vs Train ── */}
              <Pressable
                style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
                onPress={() => navigation.navigate("Snapshot")}
                android_ripple={{ color: "rgba(167,139,250,0.25)", borderless: false }}
              >
                <View style={styles.cardHeaderRow}>
                  <Text style={styles.cardTitle}>Today's Plan</Text>
                  <Ionicons name="chevron-forward-circle" size={24} color="rgba(220,210,255,1)" />
                </View>

                {todayEvent === undefined ? (
                  /* loading */
                  <Text style={styles.cardSub}>Loading…</Text>
                ) : todayEvent === null ? (
                  /* no plan cached */
                  <>
                    <Text style={styles.cardSub}>No plan found</Text>
                    <Text style={styles.planHint}>Generate your plan in Chat first</Text>
                  </>
                ) : todayEvent.type === "rest" ? (
                  /* rest day */
                  <>
                    <View style={styles.trainBadgeRest}>
                      <Ionicons name="bed-outline" size={16} color="#6EE7B7" />
                      <Text style={[styles.trainBadgeText, { color: "#6EE7B7" }]}>Rest Day</Text>
                    </View>
                    <Text style={styles.planHint}>Recovery — light movement or rest today</Text>
                  </>
                ) : (
                  /* workout day */
                  <>
                    <View style={styles.trainBadgeWorkout}>
                      <Ionicons name="barbell-outline" size={16} color="#C4B5FD" />
                      <Text style={[styles.trainBadgeText, { color: "#C4B5FD" }]}>Train Day</Text>
                    </View>
                    {todayEvent.metadata?.targetMuscleGroups?.length > 0 && (
                      <Text style={styles.planMuscles}>
                        {todayEvent.metadata.targetMuscleGroups.join(" · ")}
                      </Text>
                    )}
                    {todayEvent.metadata?.estimatedDurationMinutes && (
                      <Text style={styles.planHint}>
                        ~{todayEvent.metadata.estimatedDurationMinutes} min · {todayEvent.title}
                      </Text>
                    )}
                  </>
                )}

                <View style={styles.viewPlanRow}>
                  <Text style={styles.viewPlanText}>Tap to see full plan</Text>
                  <Ionicons name="arrow-forward" size={12} color="rgba(255,255,255,0.45)" />
                </View>
              </Pressable>

              {/* ── Form Score Card ── */}
              <Pressable
                style={({ pressed }) => [styles.formCard, pressed && styles.cardPressed]}
                onPress={() => navigation.navigate("RecordVideo")}
                android_ripple={{ color: "rgba(167,139,250,0.25)", borderless: false }}
              >
                <View style={styles.formHeader}>
                  <Text style={styles.cardTitle}>Form Score</Text>
                  <View style={styles.formHeaderIcons}>
                    <Ionicons name="videocam-outline" size={18} color="rgba(255,255,255,0.9)" />
                    <Ionicons name="chevron-forward-circle" size={24} color="rgba(220,210,255,1)" />
                  </View>
                </View>

                {cvResult.score === null ? (
                  /* ── Empty state ── */
                  <>
                    <Text style={styles.formBlurb}>
                      Upload a video of yourself performing a specific{"\n"}
                      exercise to know how good your form is!
                    </Text>
                    <View style={styles.mediaFrame}>
                      <Image
                        source={{ uri: "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=1200&q=60" }}
                        style={styles.mediaImg}
                        resizeMode="cover"
                      />
                    </View>
                    <View style={styles.btnRow}>
                      <View style={styles.pillBtn}>
                        <Text style={styles.pillBtnText}>Upload Video</Text>
                      </View>
                    </View>
                  </>
                ) : (
                  /* ── Has score state ── */
                  <View style={styles.scoreLayout}>
                    <View style={styles.scoreRingWrap}>
                      <View style={[styles.scoreRing, { borderColor: getScoreColor(cvResult.score) }]}>
                        <Text style={[styles.scoreNumber, { color: getScoreColor(cvResult.score) }]}>
                          {Number(cvResult.score).toFixed(0)}
                        </Text>
                        <Text style={styles.scoreDenom}>/100</Text>
                      </View>
                    </View>
                    <View style={styles.scoreDetails}>
                      {!!cvResult.exercise && (
                        <Text style={styles.scoreExercise}>{cvResult.exercise}</Text>
                      )}
                      <Text style={styles.scoreInsight}>
                        {cvResult.insight}
                      </Text>
                      <View style={styles.reuploadRow}>
                        <Ionicons name="refresh-outline" size={12} color="rgba(255,255,255,0.5)" />
                        <Text style={styles.reuploadText}>Tap to re-analyze</Text>
                      </View>
                    </View>
                  </View>
                )}
              </Pressable>

              {/* ── Rotating Tips Card ── */}
              <View style={[styles.tipsCard, { backgroundColor: colors.bg, borderColor: colors.border }]}>
                {/* Header row */}
                <View style={styles.tipsHeader}>
                  <View style={[styles.tipsCategoryPill, { backgroundColor: colors.bg, borderColor: colors.border }]}>
                    <Ionicons name={tip.icon} size={12} color={colors.text} />
                    <Text style={[styles.tipsCategoryText, { color: colors.text }]}>{tip.category}</Text>
                  </View>
                  <Text style={styles.tipsCounter}>{tipIndex + 1} / {TIPS.length}</Text>
                </View>

                {/* Tip text (fades) */}
                <Animated.Text style={[styles.tipText, { opacity: fadeAnim }]}>
                  {tip.text}
                </Animated.Text>

                {/* Dot indicators + nav */}
                <View style={styles.tipsFooter}>
                  <Pressable style={styles.tipsNavBtn} onPress={() => changeTip((tipIndex - 1 + TIPS.length) % TIPS.length)}>
                    <Ionicons name="chevron-back" size={16} color="rgba(255,255,255,0.7)" />
                  </Pressable>

                  <View style={styles.tipsDots}>
                    {Array.from({ length: 5 }).map((_, i) => {
                      const dotIndex = (tipIndex - 2 + i + TIPS.length) % TIPS.length;
                      const isActive = dotIndex === tipIndex;
                      return (
                        <Pressable key={i} onPress={() => changeTip(dotIndex)}>
                          <View style={[styles.tipsDot, isActive && styles.tipsDotActive, isActive && { backgroundColor: colors.text }]} />
                        </Pressable>
                      );
                    })}
                  </View>

                  <Pressable style={styles.tipsNavBtn} onPress={() => changeTip((tipIndex + 1) % TIPS.length)}>
                    <Ionicons name="chevron-forward" size={16} color="rgba(255,255,255,0.7)" />
                  </Pressable>
                </View>
              </View>

            </ScrollView>

            <View style={styles.promptBarWrap}>
              <View style={styles.promptBar}>
                <TextInput
                  testID="chat-input"
                  value={prompt}
                  onChangeText={setPrompt}
                  placeholder="Enter Your Prompt Here..."
                  placeholderTextColor="rgba(0,0,0,0.45)"
                  style={styles.promptInput}
                  returnKeyType="send"
                  onSubmitEditing={onSend}
                />
                <Pressable testID="send-button" style={styles.sendBtn} onPress={onSend}>
                  <Ionicons name="arrow-up" size={18} color="#4A4A4A" />
                </Pressable>
              </View>
            </View>
          </View>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: { flex: 1 },
  safe: { flex: 1 },

  cardShell: {
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
    position: "relative",
  },

  scrollContent: {
    flexGrow: 1,
    paddingBottom: 90,
  },

  topRow: {
    paddingTop: 6,
    flexDirection: "row",
    justifyContent: "flex-end",
  },

  // ── Greeting ──
  greetingRow: {
    marginTop: 8,
    marginBottom: 16,
    paddingHorizontal: 2,
  },
  greeting: {
    color: "#fff",
    fontSize: 22,
    fontWeight: "900",
    letterSpacing: -0.3,
  },
  greetingSub: {
    color: "rgba(255,255,255,0.55)",
    fontSize: 13,
    fontWeight: "600",
    marginTop: 2,
  },

  // ── Cards ──
  card: {
    borderRadius: 16,
    padding: 14,
    backgroundColor: "rgba(255,255,255,0.12)",
    borderWidth: 1.5,
    borderColor: "rgba(167,139,250,0.45)",
    marginBottom: 12,
    overflow: "hidden",
  },
  formCard: {
    borderRadius: 18,
    padding: 16,
    backgroundColor: "rgba(255,255,255,0.17)",
    borderWidth: 1.5,
    borderColor: "rgba(167,139,250,0.6)",
    marginBottom: 12,
    overflow: "hidden",
  },
  cardHeaderRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    marginBottom: 4,
  },
  cardPressed: {
    opacity: 0.75,
  },
  cardTitle: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "900",
    textAlign: "center",
  },
  cardSub: {
    color: "rgba(255,255,255,0.65)",
    fontSize: 11,
    fontWeight: "700",
    textAlign: "center",
    marginTop: 4,
  },

  trainBadgeRest: {
    flexDirection: "row",
    alignItems: "center",
    alignSelf: "center",
    gap: 6,
    paddingVertical: 5,
    paddingHorizontal: 14,
    borderRadius: 999,
    backgroundColor: "rgba(52,211,153,0.15)",
    borderWidth: 1,
    borderColor: "rgba(52,211,153,0.35)",
    marginTop: 8,
    marginBottom: 6,
  },
  trainBadgeWorkout: {
    flexDirection: "row",
    alignItems: "center",
    alignSelf: "center",
    gap: 6,
    paddingVertical: 5,
    paddingHorizontal: 14,
    borderRadius: 999,
    backgroundColor: "rgba(167,139,250,0.15)",
    borderWidth: 1,
    borderColor: "rgba(167,139,250,0.35)",
    marginTop: 8,
    marginBottom: 6,
  },
  trainBadgeText: {
    fontSize: 13,
    fontWeight: "800",
  },
  planMuscles: {
    color: "rgba(255,255,255,0.85)",
    fontSize: 12,
    fontWeight: "700",
    textAlign: "center",
    marginBottom: 2,
  },
  planHint: {
    color: "rgba(255,255,255,0.5)",
    fontSize: 11,
    fontWeight: "600",
    textAlign: "center",
    marginBottom: 2,
  },
  viewPlanRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 4,
    marginTop: 10,
  },
  viewPlanText: {
    color: "rgba(255,255,255,0.45)",
    fontSize: 11,
    fontWeight: "700",
  },

  formHeader: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    gap: 8,
    marginBottom: 6,
  },
  formHeaderIcons: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  formBlurb: {
    color: "rgba(255,255,255,0.75)",
    fontSize: 11,
    fontWeight: "700",
    textAlign: "center",
    marginBottom: 10,
  },
  mediaFrame: {
    borderRadius: 14,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.14)",
    backgroundColor: "rgba(0,0,0,0.18)",
  },
  mediaImg: { width: "100%", height: 150 },

  btnRow: {
    flexDirection: "row",
    justifyContent: "center",
    gap: 10,
    marginTop: 10,
  },
  pillBtn: {
    flex: 1,
    height: 30,
    borderRadius: 999,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(0,0,0,0.28)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.14)",
  },
  pillBtnText: {
    color: "rgba(255,255,255,0.92)",
    fontSize: 11,
    fontWeight: "800",
  },

  metaText: {
    color: "rgba(255,255,255,0.92)",
    fontSize: 11,
    fontWeight: "700",
    marginTop: 4,
  },
  metaLabel: { color: "rgba(255,255,255,0.7)", fontWeight: "900" },

  // ── Score ring ──
  scoreLayout: {
    flexDirection: "row",
    alignItems: "center",
    gap: 16,
    marginTop: 10,
  },
  scoreRingWrap: {
    alignItems: "center",
    justifyContent: "center",
  },
  scoreRing: {
    width: 86,
    height: 86,
    borderRadius: 43,
    borderWidth: 4,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(0,0,0,0.15)",
  },
  scoreNumber: {
    fontSize: 26,
    fontWeight: "900",
    lineHeight: 30,
  },
  scoreDenom: {
    color: "rgba(255,255,255,0.5)",
    fontSize: 10,
    fontWeight: "700",
  },
  scoreDetails: {
    flex: 1,
    gap: 4,
  },
  scoreExercise: {
    color: "#fff",
    fontSize: 14,
    fontWeight: "900",
    marginBottom: 2,
  },
  scoreInsight: {
    color: "rgba(255,255,255,0.7)",
    fontSize: 11,
    fontWeight: "600",
    lineHeight: 16,
  },
  reuploadRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    marginTop: 6,
  },
  reuploadText: {
    color: "rgba(255,255,255,0.4)",
    fontSize: 10,
    fontWeight: "700",
  },

  // ── Rotating tips card (compact) ──
  tipsCard: {
    borderRadius: 16,
    borderWidth: 1,
    padding: 12,
    marginBottom: 10,
  },
  tipsHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 12,
  },
  tipsCategoryPill: {
    flexDirection: "row",
    alignItems: "center",
    gap: 5,
    paddingVertical: 4,
    paddingHorizontal: 10,
    borderRadius: 999,
    borderWidth: 1,
  },
  tipsCategoryText: {
    fontSize: 11,
    fontWeight: "800",
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  tipsCounter: {
    color: "rgba(255,255,255,0.35)",
    fontSize: 11,
    fontWeight: "700",
  },
  tipText: {
    color: "rgba(255,255,255,0.92)",
    fontSize: 12,
    fontWeight: "600",
    lineHeight: 18,
    marginBottom: 12,
  },
  tipsFooter: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  tipsNavBtn: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: "rgba(255,255,255,0.10)",
    alignItems: "center",
    justifyContent: "center",
  },
  tipsDots: {
    flexDirection: "row",
    alignItems: "center",
    gap: 5,
  },
  tipsDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: "rgba(255,255,255,0.2)",
  },
  tipsDotActive: {
    width: 18,
    borderRadius: 3,
  },

  promptBarWrap: {
    position: "absolute",
    left: 0,
    right: 0,
    bottom: 18,
    paddingHorizontal: 18,
  },

  promptBar: {
    backgroundColor: "rgba(255,255,255,0.92)",
    borderRadius: 28,
    paddingLeft: 16,
    paddingRight: 10,
    height: 56,
    flexDirection: "row",
    alignItems: "center",
  },

  promptInput: {
    flex: 1,
    fontSize: 14,
    fontWeight: "600",
    color: "#222",
    paddingRight: 10,
  },

  sendBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: "rgba(255,255,255,0.95)",
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: "rgba(0,0,0,0.12)",
  },
});
