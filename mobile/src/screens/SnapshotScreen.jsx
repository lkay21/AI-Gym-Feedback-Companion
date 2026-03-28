import { Ionicons } from "@expo/vector-icons";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { LinearGradient } from "expo-linear-gradient";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  Image,
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
import { Calendar } from "react-native-calendars";
import MenuDropdown from "../components/MenuDropdown";
import { chatAPI } from "../services/api";
import { mapPlanToCalendarEvents } from "../utils/planMapping";

const WEEKDAY_SHORT = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function pillFromDateString(dateStr) {
  const d = new Date(`${dateStr}T12:00:00`);
  return {
    k: dateStr,
    label: WEEKDAY_SHORT[d.getDay()],
    num: String(d.getDate()),
  };
}

function pickInitialDate(events) {
  const today = new Date().toISOString().split("T")[0];
  const workoutDates = events
    .filter((e) => e.type === "workout")
    .map((e) => e.date)
    .sort();
  if (workoutDates.includes(today)) return today;
  return workoutDates[0] || events[0]?.date || today;
}

export default function SnapshotScreen({ navigation }) {
  const [userId, setUserId] = useState(null);
  const [planName, setPlanName] = useState("");
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedDate, setSelectedDate] = useState(null);
  const [prompt, setPrompt] = useState("");

  useEffect(() => {
    AsyncStorage.getItem("userId").then(setUserId);
  }, []);

  const fetchPlan = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const result = await chatAPI.generatePlan();
      if (!result.success) {
        if (result.data?.requiresOnboarding) {
          throw new Error(
            "Complete your health profile and generate a plan in Chat first."
          );
        }
        throw new Error(result.error || "Failed to load fitness plan");
      }
      const structuredPlan = result.data?.structuredPlan;
      if (!structuredPlan) {
        throw new Error("No structured plan returned from server");
      }
      setPlanName(structuredPlan.planName || "Your Fitness Plan");
      const ev = mapPlanToCalendarEvents(structuredPlan);
      setEvents(ev);
      setSelectedDate(pickInitialDate(ev));
    } catch (e) {
      setError(e.message || "Failed to load plan");
      setEvents([]);
      setSelectedDate(new Date().toISOString().split("T")[0]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPlan();
  }, [fetchPlan]);

  const eventsByDate = useMemo(() => {
    const map = {};
    events.forEach((ev) => {
      if (!map[ev.date]) map[ev.date] = [];
      map[ev.date].push(ev);
    });
    return map;
  }, [events]);

  const workoutDates = useMemo(
    () =>
      events
        .filter((e) => e.type === "workout")
        .map((e) => e.date)
        .sort(),
    [events]
  );

  const dayPills = useMemo(() => {
    const unique = [...new Set(workoutDates)].slice(0, 5);
    return unique.map(pillFromDateString);
  }, [workoutDates]);

  const selectedEvent = useMemo(() => {
    if (!selectedDate) return null;
    return (eventsByDate[selectedDate] || [])[0] || null;
  }, [selectedDate, eventsByDate]);

  const exercisesForDay = selectedEvent?.metadata?.exercises || [];
  const muscleGroups = selectedEvent?.metadata?.targetMuscleGroups || [];
  const workoutLabel =
    selectedEvent?.metadata?.workoutType || selectedEvent?.title || "Workout";
  const durationMinutes =
    selectedEvent?.metadata?.estimatedDurationMinutes ?? null;

  const markedDates = useMemo(() => {
    const marks = {};
    [...new Set(workoutDates)].forEach((date) => {
      marks[date] = { marked: true, dotColor: "#F5A623" };
    });
    if (selectedDate) {
      marks[selectedDate] = {
        ...(marks[selectedDate] || {}),
        selected: true,
        selectedColor: "rgba(36, 12, 75, 0.85)",
        selectedTextColor: "#fff",
      };
    }
    return marks;
  }, [workoutDates, selectedDate]);

  const calendarCurrent = selectedDate || new Date().toISOString().split("T")[0];

  const onSend = () => {
    const t = prompt.trim();
    if (!t) return;
    setPrompt("");
    navigation.navigate("ChatBot", { q: t });
  };

  return (
    <LinearGradient
      colors={["#4C76D6", "#8E5AAE"]}
      start={{ x: 0.15, y: 0.1 }}
      end={{ x: 0.85, y: 0.95 }}
      style={styles.bg}
    >
      <SafeAreaView style={styles.safe}>
        <KeyboardAvoidingView
          style={{ flex: 1 }}
          behavior={Platform.OS === "ios" ? "padding" : undefined}
        >
          <View style={styles.card}>
            <View style={styles.topBar}>
              <Text style={styles.topLeftLabel}>Today's Snapshot</Text>
              <MenuDropdown />
            </View>

            {userId ? (
              <Text style={styles.userHint} numberOfLines={1}>
                User: {userId}
              </Text>
            ) : null}

            <ScrollView
              showsVerticalScrollIndicator={false}
              contentContainerStyle={styles.scrollContent}
            >
              <Text style={styles.title}>Workout Snapshot</Text>
              {planName ? (
                <Text style={styles.planName}>{planName}</Text>
              ) : null}

              {loading ? (
                <View style={styles.centered}>
                  <ActivityIndicator size="large" color="#fff" />
                  <Text style={styles.loadingText}>Loading your plan…</Text>
                </View>
              ) : error ? (
                <View style={styles.centered}>
                  <Text style={styles.errorText}>{error}</Text>
                  <Pressable style={styles.retryBtn} onPress={fetchPlan}>
                    <Text style={styles.retryBtnText}>Retry</Text>
                  </Pressable>
                </View>
              ) : (
                <>
                  <View style={styles.pillsRow}>
                    {dayPills.length === 0 ? (
                      <Text style={styles.emptyPlanText}>
                        No scheduled workouts in your plan yet.
                      </Text>
                    ) : (
                      dayPills.map((p) => {
                        const active = p.k === selectedDate;
                        return (
                          <Pressable
                            key={p.k}
                            onPress={() => setSelectedDate(p.k)}
                            style={[styles.pill, active && styles.pillActive]}
                          >
                            <Text
                              style={[
                                styles.pillDay,
                                active && styles.pillDayActive,
                              ]}
                            >
                              {p.label}
                            </Text>
                            <Text
                              style={[
                                styles.pillNum,
                                active && styles.pillNumActive,
                              ]}
                            >
                              {p.num}
                            </Text>
                          </Pressable>
                        );
                      })
                    )}
                  </View>

                  <View style={styles.calendarWrap}>
                    <Calendar
                      current={calendarCurrent}
                      markedDates={markedDates}
                      onDayPress={(day) => setSelectedDate(day.dateString)}
                      theme={{
                        backgroundColor: "transparent",
                        calendarBackground: "transparent",
                        textSectionTitleColor: "rgba(255,255,255,0.55)",
                        dayTextColor: "rgba(255,255,255,0.85)",
                        monthTextColor: "rgba(255,255,255,0.92)",
                        selectedDayTextColor: "#ffffff",
                        arrowColor: "rgba(255,255,255,0.85)",
                        textDisabledColor: "rgba(255,255,255,0.20)",
                        todayTextColor: "rgba(255,255,255,0.92)",
                      }}
                      style={styles.calendar}
                    />
                  </View>

                  <Text style={styles.sectionTitle}>Targeted Muscle Groups</Text>
                  <Text style={styles.muscleList}>
                    {muscleGroups.length > 0
                      ? muscleGroups.join(", ")
                      : exercisesForDay.length === 0
                        ? "Rest or no exercises — tap a workout day."
                        : "See exercises below"}
                  </Text>
                  <View style={styles.muscleFrame}>
                    <Image
                      source={{
                        uri: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Muscle_anterior_labeled.png/640px-Muscle_anterior_labeled.png",
                      }}
                      style={styles.muscleImg}
                      resizeMode="contain"
                    />
                  </View>

                  <View style={styles.sessionCard}>
                    <Text style={styles.sessionTitle}>
                      {selectedDate
                        ? `Session — ${selectedDate}`
                        : "Today's Session"}
                    </Text>
                    <Text style={styles.sessionSub}>
                      {selectedEvent?.type === "rest" || exercisesForDay.length === 0
                        ? "Recovery day — light movement or rest."
                        : "Exercises below match your saved plan in AWS (by date)."}
                    </Text>

                    <View style={styles.chipRow}>
                      <View style={styles.chip}>
                        <Ionicons name="time-outline" size={14} color="#2E2E2E" />
                        <Text style={styles.chipText}>
                          {durationMinutes != null
                            ? `${durationMinutes} min`
                            : "—"}
                        </Text>
                      </View>
                      <View style={styles.chip}>
                        <Ionicons name="barbell-outline" size={14} color="#2E2E2E" />
                        <Text style={styles.chipText} numberOfLines={1}>
                          {workoutLabel}
                        </Text>
                      </View>
                    </View>

                    <Text style={styles.exerciseHeader}>Exercises</Text>
                    {exercisesForDay.length === 0 ? (
                      <Text style={styles.noExercises}>No exercises this day.</Text>
                    ) : (
                      exercisesForDay.map((ex, idx) => (
                        <View
                          key={`${ex.name}-${idx}`}
                          style={styles.exerciseRow}
                        >
                          <View style={styles.exerciseThumbPlaceholder}>
                            <Ionicons name="barbell-outline" size={22} color="#4C76D6" />
                          </View>
                          <View style={{ flex: 1, marginLeft: 10 }}>
                            <Text style={styles.exerciseTitle}>
                              {ex.name || ex.title || "Exercise"}
                            </Text>
                            <Text style={styles.exerciseDuration}>
                              {ex.duration ||
                                (ex.durationMinutes != null
                                  ? `${ex.durationMinutes} min`
                                  : "—")}{" "}
                              · {ex.sets ?? "—"} × {ex.reps ?? "—"} reps
                              {ex.weight ? ` · ${ex.weight}` : ""}
                            </Text>
                          </View>
                        </View>
                      ))
                    )}
                  </View>
                </>
              )}
            </ScrollView>

            <View style={styles.promptWrap}>
              <View style={styles.promptPill}>
                <TextInput
                  value={prompt}
                  onChangeText={setPrompt}
                  placeholder="Enter Your Prompt Here..."
                  placeholderTextColor="rgba(0,0,0,0.45)"
                  style={styles.promptInput}
                  returnKeyType="send"
                  onSubmitEditing={onSend}
                />
                <Pressable style={styles.sendBtn} onPress={onSend}>
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
  safe: { flex: 1 },
  bg: { flex: 1 },

  card: {
    flex: 1,
    marginHorizontal: 16,
    marginTop: 10,
    marginBottom: 14,
    borderRadius: 28,
    paddingTop: 10,
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
    color: "rgba(255,255,255,0.60)",
    fontSize: 12,
    fontWeight: "800",
  },
  userHint: {
    fontSize: 10,
    color: "rgba(255,255,255,0.45)",
    paddingHorizontal: 8,
    marginBottom: 4,
  },

  scrollContent: {
    paddingBottom: 120,
  },

  title: {
    color: "rgba(255,255,255,0.95)",
    fontSize: 22,
    fontWeight: "900",
    textAlign: "center",
    marginTop: 6,
    marginBottom: 6,
  },
  planName: {
    color: "rgba(255,255,255,0.75)",
    fontSize: 12,
    fontWeight: "700",
    textAlign: "center",
    marginBottom: 12,
  },

  centered: {
    paddingVertical: 24,
    alignItems: "center",
  },
  loadingText: {
    marginTop: 10,
    color: "rgba(255,255,255,0.85)",
    fontSize: 13,
  },
  errorText: {
    color: "#fecaca",
    textAlign: "center",
    marginBottom: 12,
    paddingHorizontal: 12,
  },
  retryBtn: {
    backgroundColor: "rgba(255,255,255,0.92)",
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 16,
  },
  retryBtnText: {
    fontWeight: "800",
    color: "#222",
  },
  emptyPlanText: {
    color: "rgba(255,255,255,0.8)",
    fontSize: 12,
    textAlign: "center",
    flex: 1,
  },

  pillsRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingHorizontal: 6,
    marginBottom: 10,
    flexWrap: "wrap",
    gap: 8,
  },
  pill: {
    width: 54,
    borderRadius: 14,
    paddingVertical: 10,
    alignItems: "center",
    backgroundColor: "rgba(255,255,255,0.85)",
    borderWidth: 1,
    borderColor: "rgba(0,0,0,0.10)",
  },
  pillActive: {
    backgroundColor: "rgba(36, 12, 75, 0.85)",
    borderColor: "rgba(255,255,255,0.18)",
  },
  pillDay: { fontSize: 10, fontWeight: "900", color: "rgba(20,20,20,0.75)" },
  pillNum: { marginTop: 4, fontSize: 14, fontWeight: "900", color: "#111" },
  pillDayActive: { color: "rgba(255,255,255,0.80)" },
  pillNumActive: { color: "rgba(255,255,255,0.95)" },

  calendarWrap: {
    marginTop: 2,
    marginBottom: 14,
    paddingHorizontal: 6,
  },
  calendar: {
    borderRadius: 16,
    padding: 8,
    backgroundColor: "rgba(255,255,255,0.06)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.10)",
  },

  sectionTitle: {
    marginTop: 6,
    marginBottom: 6,
    color: "rgba(255,255,255,0.88)",
    fontSize: 12,
    fontWeight: "900",
    textAlign: "center",
  },
  muscleList: {
    color: "rgba(255,255,255,0.7)",
    fontSize: 11,
    fontWeight: "600",
    textAlign: "center",
    marginBottom: 10,
    paddingHorizontal: 8,
  },

  muscleFrame: {
    alignSelf: "center",
    width: "86%",
    height: 155,
    borderRadius: 14,
    backgroundColor: "rgba(255,255,255,0.92)",
    borderWidth: 1,
    borderColor: "rgba(0,0,0,0.10)",
    overflow: "hidden",
    marginBottom: 16,
  },
  muscleImg: { width: "100%", height: "100%" },

  sessionCard: {
    borderRadius: 18,
    padding: 14,
    backgroundColor: "rgba(36, 12, 75, 0.55)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.12)",
  },
  sessionTitle: {
    color: "rgba(255,255,255,0.95)",
    fontSize: 16,
    fontWeight: "900",
    textAlign: "center",
  },
  sessionSub: {
    marginTop: 8,
    color: "rgba(255,255,255,0.70)",
    fontSize: 11,
    fontWeight: "700",
    textAlign: "center",
    lineHeight: 15,
  },

  chipRow: {
    flexDirection: "row",
    justifyContent: "center",
    gap: 10,
    marginTop: 12,
    marginBottom: 10,
    flexWrap: "wrap",
  },
  chip: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 10,
    backgroundColor: "rgba(255,255,255,0.92)",
    borderWidth: 1,
    borderColor: "rgba(0,0,0,0.10)",
    maxWidth: "48%",
  },
  chipText: { fontSize: 11, fontWeight: "900", color: "#222", flexShrink: 1 },

  exerciseHeader: {
    marginTop: 4,
    marginBottom: 8,
    color: "rgba(255,255,255,0.92)",
    fontSize: 12,
    fontWeight: "900",
  },
  noExercises: {
    color: "rgba(255,255,255,0.65)",
    fontSize: 12,
    marginBottom: 8,
  },

  exerciseRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 12,
  },
  exerciseThumbPlaceholder: {
    width: 46,
    height: 46,
    borderRadius: 14,
    backgroundColor: "rgba(255,255,255,0.92)",
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: "rgba(0,0,0,0.08)",
  },
  exerciseTitle: {
    color: "rgba(255,255,255,0.95)",
    fontSize: 12,
    fontWeight: "900",
  },
  exerciseDuration: {
    marginTop: 3,
    color: "rgba(255,255,255,0.65)",
    fontSize: 11,
    fontWeight: "700",
  },

  promptWrap: {
    position: "absolute",
    left: 0,
    right: 0,
    bottom: 18,
    paddingHorizontal: 16,
  },
  promptPill: {
    height: 54,
    borderRadius: 999,
    paddingLeft: 16,
    paddingRight: 10,
    backgroundColor: "rgba(255,255,255,0.92)",
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
