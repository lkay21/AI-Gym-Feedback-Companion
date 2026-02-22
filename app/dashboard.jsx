
import React, { useMemo, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  Image,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import MenuDropdown from "../components/MenuDropdown";

// ---- dummy data (replace later) ----
const WEEK_RANGE = "12/9/2025 - 12/15/2025";
const WEEKLY_PLAN = [
  { day: "Monday", text: "Biceps, Triceps, Shoulders" },
  { day: "Wednesday", text: "Glutes, Quads" },
  { day: "Friday", text: "Abs, Cardio" },
];

export default function Dashboard() {
  const router = useRouter();
  const [prompt, setPrompt] = useState("");

  const onSend = () => {
    const t = prompt.trim();
    if (!t) return;
    setPrompt("");
  };

  const waveBars = useMemo(
    () => [
      { label: "8A", h: 36 },
      { label: "10A", h: 52 },
      { label: "12A", h: 42 },
      { label: "2P", h: 58 },
      { label: "4PM", h: 78, active: true },
    ],
    []
  );

  return (
    <SafeAreaView style={styles.safe} edges={["top", "left", "right"]}>
      <LinearGradient
        colors={["#8E5AAE", "#4C76D6"]}
        start={{ x: 0.05, y: 0.05 }}
        end={{ x: 0.95, y: 0.95 }}
        style={styles.bg}
      >
        <KeyboardAvoidingView
          style={styles.flex}
          behavior={Platform.OS === "ios" ? "padding" : undefined}
        >
          {/* Top right dropdown */}
          <View style={styles.topRow}>
            <MenuDropdown />
          </View>

          <Text style={styles.title}>Fitness Dashboard</Text>

          {/* Weekly Workout Plan card */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Weekly Workout Plan</Text>
            <Text style={styles.cardSub}>{WEEK_RANGE}</Text>

            <View style={{ height: 10 }} />
            {WEEKLY_PLAN.map((row) => (
              <View key={row.day} style={styles.planRow}>
                <Text style={styles.planDay}>{row.day} - </Text>
                <Text style={styles.planText}>{row.text}</Text>
              </View>
            ))}

            <View style={styles.shoeIcon}>
              <Ionicons name="walk-outline" size={52} color="rgba(195, 220, 255, 0.85)" />
            </View>
          </View>

          {/* Form Score card */}
          <View style={styles.card}>
            <View style={styles.formHeader}>
              <Text style={styles.cardTitle}>Form Score</Text>
              <Ionicons name="videocam-outline" size={18} color="rgba(255,255,255,0.9)" />
            </View>

            <Text style={styles.formBlurb}>
              Upload a video of yourself performing a specific{"\n"}
              exercise to know how good your form is!
            </Text>

            <View style={styles.mediaFrame}>
              <Image
                source={{
                  uri:
                    "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=1200&q=60",
                }}
                style={styles.mediaImg}
                resizeMode="cover"
              />
            </View>

            <View style={styles.btnRow}>
              <Pressable
                style={styles.pillBtn}
                onPress={() => router.push("/record")}
              >
                <Text style={styles.pillBtnText}>Record Video</Text>
              </Pressable>

              {/* You said Select Exercise is reached from Record’s Upload button,
                  so this can also go to Record (same flow) */}
              <Pressable
                style={styles.pillBtn}
                onPress={() => router.push("/record")}
              >
                <Text style={styles.pillBtnText}>Upload Video</Text>
              </Pressable>
            </View>

            <View style={{ height: 10 }} />

            <Text style={styles.metaText}>
              <Text style={styles.metaLabel}>Form Score:</Text> 7.8
            </Text>
            <Text style={styles.metaText}>
              <Text style={styles.metaLabel}>Feedback:</Text> Keep your back straight and your arm{"\n"}
              at a 90 degree angle!
            </Text>
          </View>

          {/* Steps summary */}
          <View style={styles.stepsRow}>
            <View style={styles.stepsIconWrap}>
              <Ionicons name="footsteps-outline" size={26} color="#2E2E2E" />
            </View>

            <View style={{ flex: 1 }}>
              <Text style={styles.stepsText}>Today’s Steps: 7,855</Text>
              <Text style={styles.stepsText}>Weekly Average: 8,933</Text>
            </View>
          </View>

          {/* Chart area */}
          <View style={styles.chartWrap}>
            <View style={styles.bubble}>
              <Text style={styles.bubbleText}>120 cal</Text>
            </View>

            <View style={styles.chartBars}>
              {waveBars.map((b) => (
                <View key={b.label} style={styles.barCol}>
                  <View style={[styles.bar, { height: b.h }, b.active && styles.barActive]} />
                  <Text style={[styles.barLabel, b.active && styles.barLabelActive]}>
                    {b.label}
                  </Text>
                </View>
              ))}
            </View>
          </View>

          {/* Bottom prompt bar */}
          <View style={styles.promptBarWrap}>
            <View style={styles.promptBar}>
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
        </KeyboardAvoidingView>
      </LinearGradient>
    </SafeAreaView>
  );
}

// (keep your existing styles; only topRow changed a bit)
const styles = StyleSheet.create({
  flex: { flex: 1 },
  safe: { flex: 1, backgroundColor: "#000" },
  bg: { flex: 1, paddingHorizontal: 16 },

  topRow: {
    paddingTop: 6,
    flexDirection: "row",
    justifyContent: "flex-end",
  },

  title: {
    color: "#fff",
    fontSize: 28,
    fontWeight: "800",
    textAlign: "center",
    marginTop: 8,
    marginBottom: 12,
  },

  card: {
    borderRadius: 16,
    padding: 14,
    backgroundColor: "rgba(36, 12, 75, 0.35)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.10)",
    marginBottom: 14,
    overflow: "hidden",
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

  planRow: { flexDirection: "row", justifyContent: "center", marginVertical: 4, paddingHorizontal: 6 },
  planDay: { color: "#fff", fontWeight: "900", fontSize: 12 },
  planText: { color: "rgba(255,255,255,0.9)", fontWeight: "700", fontSize: 12 },
  shoeIcon: { position: "absolute", right: 12, bottom: 8, opacity: 0.9 },

  formHeader: { flexDirection: "row", justifyContent: "center", alignItems: "center", gap: 8, marginBottom: 6 },
  formBlurb: { color: "rgba(255,255,255,0.75)", fontSize: 11, fontWeight: "700", textAlign: "center", marginBottom: 10 },
  mediaFrame: { borderRadius: 14, overflow: "hidden", borderWidth: 1, borderColor: "rgba(255,255,255,0.14)", backgroundColor: "rgba(0,0,0,0.18)" },
  mediaImg: { width: "100%", height: 150 },

  btnRow: { flexDirection: "row", justifyContent: "space-between", gap: 10, marginTop: 10 },
  pillBtn: { flex: 1, height: 30, borderRadius: 999, alignItems: "center", justifyContent: "center", backgroundColor: "rgba(0,0,0,0.28)", borderWidth: 1, borderColor: "rgba(255,255,255,0.14)" },
  pillBtnText: { color: "rgba(255,255,255,0.92)", fontSize: 11, fontWeight: "800" },

  metaText: { color: "rgba(255,255,255,0.92)", fontSize: 11, fontWeight: "700", marginTop: 4 },
  metaLabel: { color: "rgba(255,255,255,0.7)", fontWeight: "900" },

  stepsRow: { flexDirection: "row", alignItems: "center", gap: 12, marginTop: 2, marginBottom: 8, paddingHorizontal: 6 },
  stepsIconWrap: { width: 40, height: 40, borderRadius: 12, backgroundColor: "rgba(255,255,255,0.92)", alignItems: "center", justifyContent: "center", borderWidth: 1, borderColor: "rgba(0,0,0,0.10)" },
  stepsText: { color: "rgba(255,255,255,0.92)", fontSize: 14, fontWeight: "900" },

  chartWrap: { flex: 1, borderRadius: 16, paddingTop: 10, paddingHorizontal: 10, marginBottom: 96 },
  bubble: { alignSelf: "flex-end", backgroundColor: "rgba(255,255,255,0.92)", paddingVertical: 6, paddingHorizontal: 10, borderRadius: 999, borderWidth: 1, borderColor: "rgba(0,0,0,0.12)", marginBottom: 8 },
  bubbleText: { color: "#222", fontWeight: "900", fontSize: 12 },

  chartBars: { flex: 1, borderRadius: 16, paddingVertical: 8, paddingHorizontal: 6, justifyContent: "flex-end", flexDirection: "row", gap: 10, backgroundColor: "rgba(255,255,255,0.06)", borderWidth: 1, borderColor: "rgba(255,255,255,0.10)" },
  barCol: { flex: 1, alignItems: "center", justifyContent: "flex-end" },
  bar: { width: "100%", borderRadius: 18, backgroundColor: "rgba(255,255,255,0.65)" },
  barActive: { backgroundColor: "rgba(255,255,255,0.92)" },
  barLabel: { marginTop: 8, color: "rgba(255,255,255,0.55)", fontSize: 11, fontWeight: "800" },
  barLabelActive: { color: "rgba(255,255,255,0.95)" },

  promptBarWrap: { position: "absolute", left: 0, right: 0, bottom: 18, paddingHorizontal: 18 },
  promptBar: { backgroundColor: "rgba(255,255,255,0.92)", borderRadius: 28, paddingLeft: 16, paddingRight: 10, height: 56, flexDirection: "row", alignItems: "center" },
  promptInput: { flex: 1, fontSize: 14, fontWeight: "600", color: "#222", paddingRight: 10 },
  sendBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: "rgba(255,255,255,0.95)", alignItems: "center", justifyContent: "center", borderWidth: 1, borderColor: "rgba(0,0,0,0.12)" },
});