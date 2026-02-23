import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { useMemo, useState } from "react";
import {
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
import { Calendar } from "react-native-calendars";
import { SafeAreaView } from "react-native-safe-area-context";
import MenuDropdown from "../components/MenuDropdown";
import { useRouter } from "expo-router";

const DAY_PILLS = [
  { k: "sat", label: "Sat", num: "7" },
  { k: "sun", label: "Sun", num: "8" },
  { k: "mon", label: "Mon", num: "9" },
  { k: "tue", label: "Tue", num: "10" },
  { k: "wed", label: "Wed", num: "11" },
];

const EXERCISES = [
  {
    id: "e1",
    title: "Exercise 1",
    duration: "02.30 Minutes",
    image:
      "https://images.unsplash.com/photo-1599058918144-1ffabb6ab9a0?auto=format&fit=crop&w=200&q=80",
  },
  {
    id: "e2",
    title: "Exercise 2",
    duration: "02.00 Minutes",
    image:
      "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=200&q=80",
  },
  {
    id: "e3",
    title: "Exercise 3",
    duration: "03.20 Minutes",
    image:
      "https://images.unsplash.com/photo-1517963628607-235ccdd5476c?auto=format&fit=crop&w=200&q=80",
  },
];

export default function SnapshotScreen() {
  const [selectedPill, setSelectedPill] = useState("mon");
  const [selectedDate, setSelectedDate] = useState("2025-12-09");
  const [prompt, setPrompt] = useState("");
  const router = useRouter();

  const markedDates = useMemo(
    () => ({
      [selectedDate]: {
        selected: true,
        selectedColor: "rgba(36, 12, 75, 0.85)",
        selectedTextColor: "#fff",
      },
      "2025-12-07": { marked: true, dotColor: "#F5A623" },
      "2025-12-09": { marked: true, dotColor: "#F5A623" },
      "2025-12-14": { marked: true, dotColor: "#F5A623" },
    }),
    [selectedDate]
  );

  const onSend = () => {
    const t = prompt.trim();
    if (!t) return;
    setPrompt("");
    router.push({ pathname: "/chatbot", params: { q: t } });
  };

  return (
      <LinearGradient
        colors={["#4C76D6", "#8E5AAE"]}
        start={{ x: 0.15, y: 0.1 }}
        end={{ x: 0.85, y: 0.95 }}
        style={styles.bg}
      >
       <SafeAreaView style={styles.safe} edges={["top", "left", "right"]}>
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

              {/* Day pills */}
              <View style={styles.pillsRow}>
                {DAY_PILLS.map((p) => {
                  const active = p.k === selectedPill;
                  return (
                    <Pressable
                      key={p.k}
                      onPress={() => setSelectedPill(p.k)}
                      style={[styles.pill, active && styles.pillActive]}
                    >
                      <Text style={[styles.pillDay, active && styles.pillDayActive]}>
                        {p.label}
                      </Text>
                      <Text style={[styles.pillNum, active && styles.pillNumActive]}>
                        {p.num}
                      </Text>
                    </Pressable>
                  );
                })}
              </View>

              {/* Calendar */}
              <View style={styles.calendarWrap}>
                <Calendar
                  current={"2025-12-01"}
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
              <Text style={styles.sectionTitle}>Targeted Muscle Groups</Text>
              <View style={styles.muscleFrame}>
                <Image
                  source={{
                    uri:
                      "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Muscle_anterior_labeled.png/640px-Muscle_anterior_labeled.png",
                  }}
                  style={styles.muscleImg}
                  resizeMode="contain"
                />
              </View>

              {/* Session card */}
              <View style={styles.sessionCard}>
                <Text style={styles.sessionTitle}>Starting Today’s Session</Text>
                <Text style={styles.sessionSub}>
                  Make sure to warm up and stretch your muscles{"\n"}
                  before proceeding with today’s session.
                </Text>

                <View style={styles.chipRow}>
                  <View style={styles.chip}>
                    <Ionicons name="time-outline" size={14} color="#2E2E2E" />
                    <Text style={styles.chipText}>10.00 mins</Text>
                  </View>
                  <View style={styles.chip}>
                    <Ionicons name="walk-outline" size={14} color="#2E2E2E" />
                    <Text style={styles.chipText}>Running</Text>
                  </View>
                </View>

                <Text style={styles.exerciseHeader}>Exercises</Text>

                {EXERCISES.map((e) => (
                  <View key={e.id} style={styles.exerciseRow}>
                    <Image source={{ uri: e.image }} style={styles.exerciseThumb} />
                    <View style={{ flex: 1, marginLeft: 10 }}>
                      <Text style={styles.exerciseTitle}>{e.title}</Text>
                      <Text style={styles.exerciseDuration}>{e.duration}</Text>
                    </View>
                    <Pressable style={styles.playBtn} onPress={() => {}}>
                      <Ionicons name="play" size={16} color="#2E2E2E" />
                    </Pressable>
                  </View>
                ))}
              </View>
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

  title: {
    color: "rgba(255,255,255,0.95)",
    fontSize: 22,
    fontWeight: "900",
    textAlign: "center",
    marginTop: 6,
    marginBottom: 14,
  },

  pillsRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingHorizontal: 6,
    marginBottom: 10,
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
    marginBottom: 10,
    color: "rgba(255,255,255,0.88)",
    fontSize: 12,
    fontWeight: "900",
    textAlign: "center",
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
    marginTop: 4,
    marginBottom: 8,
    color: "rgba(255,255,255,0.92)",
    fontSize: 12,
    fontWeight: "900",
  },

  exerciseRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 12,
  },
  exerciseThumb: {
    width: 46,
    height: 46,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.14)",
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
  playBtn: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: "rgba(255,255,255,0.92)",
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: "rgba(0,0,0,0.10)",
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
