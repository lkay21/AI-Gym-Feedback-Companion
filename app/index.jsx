import React, { useMemo, useState } from "react";

import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import {
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import { Calendar } from "react-native-calendars";
import { router } from "expo-router";

/**
 * Workouts keyed by ISO date (YYYY-MM-DD).
 * Replace this with your real backend data later.
 */
const WORKOUTS_BY_DATE = {
  "2025-12-09": [
    {
      id: "w1",
      title: "Bicep Curls",
      tag: "All day today",
      duration: "30 minutes",
      reps: "3",
      sets: "8",
      exercise: "5",
    },
    {
      id: "w2",
      title: "Triceps Extensions",
      tag: "All day today",
      duration: "30 minutes",
      reps: "3",
      sets: "8",
      exercise: "5",
    },
    {
      id: "w3",
      title: "Lat Pull-downs",
      tag: "All day today",
      duration: "30 minutes",
      reps: "3",
      sets: "8",
      exercise: "5",
    },
  ],
  "2025-12-14": [
    {
      id: "w4",
      title: "Incline Bench",
      tag: "Scheduled",
      duration: "40 minutes",
      reps: "60",
      sets: "12",
      exercise: "4",
    },
  ],
};

function WorkoutCard({ item }) {
  return (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.cardTitle}>{item.title}</Text>
        <Text style={styles.cardTag}>{item.tag}</Text>
      </View>

      <View style={styles.cardRow}>
        <View style={styles.metric}>
          <Text style={styles.metricLabel}>Duration:</Text>
          <Text style={styles.metricValue}>{item.duration}</Text>
        </View>
        <View style={styles.metric}>
          <Text style={styles.metricLabel}>Reps:</Text>
          <Text style={styles.metricValue}>{item.reps}</Text>
        </View>
        <View style={styles.metric}>
          <Text style={styles.metricLabel}>Sets:</Text>
          <Text style={styles.metricValue}>{item.sets}</Text>
        </View>
        <View style={styles.metric}>
          <Text style={styles.metricLabel}>Exercise:</Text>
          <Text style={styles.metricValue}>{item.exercise}</Text>
        </View>
      </View>
    </View>
  );
}

export default function Index() {
  const [selectedDate, setSelectedDate] = useState("2025-12-09");
  const [prompt, setPrompt] = useState("");

  const workoutsForDay = WORKOUTS_BY_DATE[selectedDate] ?? [];

  // Mark the selected date + add dots for any date that has workouts
  const markedDates = useMemo(() => {
    const marks = {};

    // Add dots for all dates that have workouts
    for (const dateKey of Object.keys(WORKOUTS_BY_DATE)) {
      marks[dateKey] = {
        marked: true,
        dotColor: "#f5a623",
      };
    }

    // Override the selected date styling
    marks[selectedDate] = {
      ...(marks[selectedDate] ?? {}),
      selected: true,
      selectedColor: "rgba(36, 12, 75, 0.85)",
      selectedTextColor: "#ffffff",
    };

    return marks;
  }, [selectedDate]);

  const onSend = () => {
    const trimmed = prompt.trim();
    if (!trimmed) return;

    // Later: send to chat endpoint
    // For now: clear the input
    setPrompt("");
  };

  return (
    <SafeAreaView style={styles.safe}>
      <LinearGradient
        colors={["#8E5AAE", "#4C76D6"]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.bg}
      >
        <KeyboardAvoidingView
          style={styles.flex}
          behavior={Platform.OS === "ios" ? "padding" : undefined}
        >
          {/* Header with navigation button */}
          <View style={styles.header}>
            <Text style={styles.title}>Workout Plan</Text>

            <Pressable
              onPress={() => router.push("/chatbot")}
              style={styles.chatNavBtn}
              accessibilityRole="button"
              accessibilityLabel="Go to Chatbot"
            >
              <Ionicons
                name="chatbubble-ellipses-outline"
                size={18}
                color="#fff"
              />
              <Text style={styles.chatNavText}>Chatbot</Text>
            </Pressable>
          </View>

          <FlatList
            data={workoutsForDay}
            keyExtractor={(item) => item.id}
            contentContainerStyle={styles.listContent}
            ListHeaderComponent={
              <View>
                <Text style={styles.sectionLabel}>Calendar</Text>

                <View style={styles.calendarWrap}>
                  <Calendar
                    current={"2025-12-01"}
                    markedDates={markedDates}
                    onDayPress={(day) => setSelectedDate(day.dateString)}
                    onMonthChange={(m) => {
                      // optional: fetch month data
                    }}
                    theme={{
                      backgroundColor: "transparent",
                      calendarBackground: "transparent",
                      textSectionTitleColor: "rgba(255,255,255,0.7)",
                      dayTextColor: "rgba(255,255,255,0.9)",
                      monthTextColor: "rgba(255,255,255,0.95)",
                      selectedDayTextColor: "#ffffff",
                      arrowColor: "rgba(255,255,255,0.9)",
                      textDisabledColor: "rgba(255,255,255,0.25)",
                      todayTextColor: "rgba(255,255,255,0.9)",
                    }}
                    style={styles.calendar}
                  />
                </View>

                <View style={{ height: 18 }} />

                <Text style={styles.sectionLabelSmall}>
                  {workoutsForDay.length === 0
                    ? "No workouts scheduled."
                    : "Workouts"}
                </Text>

                <View style={{ height: 10 }} />
              </View>
            }
            renderItem={({ item }) => <WorkoutCard item={item} />}
            ItemSeparatorComponent={() => <View style={{ height: 14 }} />}
          />

          {/* Bottom chatbot prompt bar */}
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
                <Ionicons name="arrow-up" size={20} color="#4A4A4A" />
              </Pressable>
            </View>
          </View>
        </KeyboardAvoidingView>
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  safe: { flex: 1, backgroundColor: "#000" },
  bg: { flex: 1 },

  header: {
    paddingHorizontal: 18,
    paddingTop: 10,
    paddingBottom: 8,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  title: {
    color: "#fff",
    fontSize: 28,
    fontWeight: "800",
  },

  chatNavBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 999,
    backgroundColor: "rgba(255,255,255,0.16)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.18)",
  },
  chatNavText: {
    color: "#fff",
    fontSize: 13,
    fontWeight: "800",
  },

  listContent: {
    paddingHorizontal: 18,
    paddingBottom: 120,
  },

  sectionLabel: {
    color: "rgba(255,255,255,0.35)",
    fontSize: 18,
    fontWeight: "700",
    marginTop: 10,
    marginBottom: 8,
  },
  sectionLabelSmall: {
    color: "rgba(255,255,255,0.5)",
    fontSize: 14,
    fontWeight: "700",
  },

  calendarWrap: {
    borderRadius: 16,
    padding: 10,
    backgroundColor: "rgba(255,255,255,0.08)",
  },
  calendar: { borderRadius: 16 },

  card: {
    borderRadius: 14,
    padding: 14,
    backgroundColor: "rgba(36, 12, 75, 0.35)",
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "baseline",
    marginBottom: 10,
  },
  cardTitle: { color: "#fff", fontSize: 16, fontWeight: "800" },
  cardTag: { color: "rgba(255,255,255,0.45)", fontSize: 12, fontWeight: "600" },

  cardRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 10,
  },
  metric: { flex: 1 },
  metricLabel: {
    color: "rgba(255,255,255,0.45)",
    fontSize: 11,
    fontWeight: "700",
    marginBottom: 4,
  },
  metricValue: { color: "#fff", fontSize: 12, fontWeight: "800" },

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
    shadowOpacity: 0.15,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 6 },
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
