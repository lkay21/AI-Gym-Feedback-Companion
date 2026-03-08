import { Ionicons } from "@expo/vector-icons";
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
import WorkoutSnapshot from "../components/WorkoutSnapshot";
import { chatAPI } from "../services/api";
import MenuDropdown from "../components/MenuDropdown";

export default function SnapshotScreen({ navigation }) {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedDate, setSelectedDate] = useState(() => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  });
  const [prompt, setPrompt] = useState("");

  const fetchPlan = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const result = await chatAPI.generatePlan();

      if (!result.success) {
        if (result.data?.requiresOnboarding) {
          throw new Error("Please complete your health profile first in the chat.");
        }
        throw new Error(result.error || "Failed to fetch plan");
      }

      const structuredPlan = result.data?.structuredPlan;
      if (!structuredPlan) {
        throw new Error("No structured plan returned");
      }

      setPlan(structuredPlan);
    } catch (err) {
      setError(err.message || "Failed to load plan");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPlan();
  }, [fetchPlan]);

  const workoutsByDate = useMemo(() => {
    if (!plan || !plan.weeks) return {};
    const map = {};
    plan.weeks.forEach((week) => {
      if (week.days) {
        week.days.forEach((day) => {
          if (day.date) {
            map[day.date] = day;
          }
        });
      }
    });
    return map;
  }, [plan]);

  const selectedWorkout = workoutsByDate[selectedDate] || null;
  const muscleGroups = selectedWorkout?.targetMuscleGroups || [];
  const estimatedDuration = selectedWorkout?.estimatedDurationMinutes || 0;
  const totalCalories = selectedWorkout?.totalExpectedCaloriesBurnt || 0;

  const markedDates = useMemo(() => {
    const marks = {};
    Object.keys(workoutsByDate).forEach((date) => {
      const workout = workoutsByDate[date];
      const isRest = workout.workoutType?.toLowerCase().includes('rest') || !workout.exercises?.length;
      marks[date] = {
        marked: true,
        dotColor: isRest ? "#94a3b8" : "#F5A623",
      };
    });
    if (selectedDate && marks[selectedDate]) {
      marks[selectedDate] = {
        ...marks[selectedDate],
        selected: true,
        selectedColor: "rgba(36, 12, 75, 0.85)",
        selectedTextColor: "#fff",
      };
    } else if (selectedDate) {
      marks[selectedDate] = {
        selected: true,
        selectedColor: "rgba(36, 12, 75, 0.85)",
        selectedTextColor: "#fff",
      };
    }
    return marks;
  }, [workoutsByDate, selectedDate]);

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
            {/* Top bar */}
            <View style={styles.topBar}>
              <Text style={styles.topLeftLabel}>Today's Snapshot</Text>
              <MenuDropdown />
            </View>

            <ScrollView
              showsVerticalScrollIndicator={false}
              contentContainerStyle={styles.scrollContent}
            >
              <Text style={styles.title}>Workout Snapshot</Text>

              {loading ? (
                <View style={styles.loadingContainer}>
                  <ActivityIndicator size="large" color="#facc15" />
                  <Text style={styles.loadingText}>Loading your workout plan...</Text>
                </View>
              ) : error ? (
                <View style={styles.errorContainer}>
                  <Text style={styles.errorText}>{error}</Text>
                  <Pressable style={styles.retryBtn} onPress={fetchPlan}>
                    <Text style={styles.retryBtnText}>Retry</Text>
                  </Pressable>
                </View>
              ) : (
              <>
              {/* Calendar */}
              <View style={styles.calendarWrap}>
                <Calendar
                  current={selectedDate}
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

              {/* Targeted muscle groups */}
              {muscleGroups.length > 0 && (
                <>
                  <Text style={styles.sectionTitle}>Targeted Muscle Groups</Text>
                  <View style={styles.muscleTagsWrap}>
                    {muscleGroups.map((muscle, idx) => (
                      <View key={idx} style={styles.muscleTag}>
                        <Text style={styles.muscleTagText}>{muscle}</Text>
                      </View>
                    ))}
                  </View>
                </>
              )}

              {/* Session card */}
              <View style={styles.sessionCard}>
                <Text style={styles.sessionTitle}>
                  {selectedWorkout?.workoutType || "Workout"}
                </Text>
                <Text style={styles.sessionSub}>
                  {selectedWorkout?.exercises?.length > 0
                    ? "Make sure to warm up and stretch your muscles\nbefore proceeding with today's session."
                    : "Rest and recovery day"}
                </Text>

                {estimatedDuration > 0 && (
                  <View style={styles.chipRow}>
                    <View style={styles.chip}>
                      <Ionicons name="time-outline" size={14} color="#2E2E2E" />
                      <Text style={styles.chipText}>{estimatedDuration} mins</Text>
                    </View>
                    {totalCalories > 0 && (
                      <View style={styles.chip}>
                        <Ionicons name="flame-outline" size={14} color="#2E2E2E" />
                        <Text style={styles.chipText}>{totalCalories} cal</Text>
                      </View>
                    )}
                  </View>
                )}

                <Text style={styles.exerciseHeader}>Exercises</Text>

                <WorkoutSnapshot workout={selectedWorkout} />
              </View>
              </>
              )}
            </ScrollView>

            {/* Bottom prompt */}
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
  safe: { flex: 1},
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

  scrollContent: {
    paddingBottom: 120, // room for prompt
  },

  loadingContainer: {
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 40,
  },
  loadingText: {
    marginTop: 12,
    color: "rgba(255,255,255,0.8)",
    fontSize: 14,
    fontWeight: "700",
  },
  errorContainer: {
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 30,
    paddingHorizontal: 20,
  },
  errorText: {
    color: "#fecaca",
    fontSize: 14,
    fontWeight: "700",
    textAlign: "center",
    marginBottom: 16,
  },
  retryBtn: {
    paddingVertical: 10,
    paddingHorizontal: 24,
    borderRadius: 20,
    backgroundColor: "#facc15",
  },
  retryBtnText: {
    color: "#111827",
    fontSize: 14,
    fontWeight: "700",
  },

  title: {
    color: "rgba(255,255,255,0.95)",
    fontSize: 22,
    fontWeight: "900",
    textAlign: "center",
    marginTop: 6,
    marginBottom: 14,
  },

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
    marginBottom: 10,
    color: "rgba(255,255,255,0.88)",
    fontSize: 12,
    fontWeight: "900",
    textAlign: "center",
  },

  muscleTagsWrap: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "center",
    gap: 8,
    marginBottom: 16,
    paddingHorizontal: 10,
  },
  muscleTag: {
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 12,
    backgroundColor: "rgba(250, 204, 21, 0.85)",
    borderWidth: 1,
    borderColor: "rgba(0,0,0,0.10)",
  },
  muscleTagText: {
    fontSize: 12,
    fontWeight: "900",
    color: "#1f2937",
  },

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
  },
  chipText: { fontSize: 11, fontWeight: "900", color: "#222" },

  exerciseHeader: {
    marginTop: 8,
    marginBottom: 10,
    color: "rgba(255,255,255,0.92)",
    fontSize: 13,
    fontWeight: "900",
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
  promptInput: { flex: 1, fontSize: 14, fontWeight: "600", color: "#222", paddingRight: 10 },
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
