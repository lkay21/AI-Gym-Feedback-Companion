import React, { useMemo } from "react";
import { View, Text, StyleSheet, FlatList, Image, Pressable, SafeAreaView } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";

export default function ExerciseSelectScreen({ navigation }) {

  const exercises = useMemo(
    () => [
      {
        id: "e1",
        title: "Bicep Curl",
        key: "bicep_curl",
        duration: "02.30 Minutes",
        image: "https://images.unsplash.com/photo-1599058918144-1ffabb6ab9a0?auto=format&fit=crop&w=200&q=80",
      },
      {
        id: "e2",
        title: "Lateral Raise",
        key: "lateral_raise",
        duration: "02.00 Minutes",
        image: "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=200&q=80",
      },
      {
        id: "e3",
        title: "Shoulder Press",
        key: "shoulder_press",
        duration: "02.00 Minutes",
        image: "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=200&q=80",
      },
      {
        id: "e4",
        title: "Hammer Curl",
        key: "hammer_curl",
        duration: "02.00 Minutes",
        image: "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=200&q=80",
      },
      {
        id: "e5",
        title: "Bent Over Row",
        key: "bent_over_row",
        duration: "02.00 Minutes",
        image: "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=200&q=80",
      },
      {
        id: "e6",
        title: "Close Grip Pulldown",
        key: "close_grip_pulldown",
        duration: "02.00 Minutes",
        image: "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=200&q=80",
      },
      {
        id: "e7",
        title: "Front Raise",
        key: "front_raise",
        duration: "02.00 Minutes",
        image: "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=200&q=80",
      },
      {
        id: "e8",
        title: "Left Front Raise",
        key: "iso_left_front_raise",
        duration: "02.00 Minutes",
        image: "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=200&q=80",
      },
      {
        id: "e9",
        title: "Left Overhead Extension",
        key: "iso_left_overhead_extension",
        duration: "02.00 Minutes",
        image: "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=200&q=80",
      },
      {
        id: "e10",
        title: "Overhead Extension",
        key: "overhead_extension",
        duration: "02.00 Minutes",
        image: "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=200&q=80",
      },
      {
        id: "e11",
        title: "Pushdown",
        key: "pushdown",
        duration: "02.00 Minutes",
        image: "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=200&q=80",
      },
      {
        id: "e12",
        title: "Right Front Raise",
        key: "iso_right_front_raise",
        duration: "02.00 Minutes",
        image: "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=200&q=80",
      },
      {
        id: "e13",
        title: "Right Overhead Extension",
        key: "iso_right_overhead_extension",
        duration: "02.00 Minutes",
        image: "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=200&q=80",
      },
    ],
    []
  );

    const onSelectExercise = (exercise) => {
    navigation.navigate("RecordVideo", { 
        selectedExercise: exercise.title,
        selectedExerciseKey: exercise.key,
    });
  };

  return (
    <LinearGradient
      colors={["#4C76D6", "#8E5AAE"]}
      start={{ x: 0.15, y: 0.1 }}
      end={{ x: 0.85, y: 0.95 }}
      style={styles.gradient}
    >
      <SafeAreaView style={styles.safe}>
        <View style={styles.card}>
          <View style={styles.topRow}>
            <Pressable style={styles.backBtn} onPress={() => navigation.goBack()}>
              <Ionicons name="chevron-back" size={20} color="rgba(255,255,255,0.95)" />
              <Text style={styles.backText}>Back</Text>
            </Pressable>
          </View>

          <Text style={styles.title}>Select Your Exercise</Text>

          <FlatList
            data={exercises}
            keyExtractor={(i) => i.id}
            showsVerticalScrollIndicator={false}
            contentContainerStyle={styles.listContent}
            ItemSeparatorComponent={() => <View style={{ height: 14 }} />}
            renderItem={({ item }) => (
              <Pressable style={styles.row} onPress={() => onSelectExercise(item)}>
                <Image source={{ uri: item.image }} style={styles.thumb} />
                <View style={styles.textCol}>
                  <Text style={styles.exerciseTitle}>{item.title}</Text>
                  <Text style={styles.duration}>{item.duration}</Text>
                </View>
              </Pressable>
            )}
          />
        </View>
      </SafeAreaView>
    </LinearGradient>
  );
}

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
    paddingHorizontal: 18,
    backgroundColor: "rgba(255,255,255,0.14)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.18)",
    overflow: "hidden",
  },

  topRow: { flexDirection: "row", justifyContent: "flex-start", paddingTop: 6, paddingBottom: 6 },
  backBtn: { flexDirection: "row", alignItems: "center", gap: 4, paddingVertical: 6, paddingHorizontal: 10, borderRadius: 999, backgroundColor: "rgba(255,255,255,0.10)", borderWidth: 1, borderColor: "rgba(255,255,255,0.14)" },
  backText: { color: "rgba(255,255,255,0.9)", fontSize: 12, fontWeight: "800" },

  title: { color: "rgba(255,255,255,0.96)", fontSize: 22, fontWeight: "800", textAlign: "center", marginBottom: 18, marginTop: 6 },
  listContent: { paddingBottom: 18 },

  row: { flexDirection: "row", alignItems: "center" },
  thumb: { width: 58, height: 58, borderRadius: 14, backgroundColor: "rgba(255,255,255,0.20)", borderWidth: 1, borderColor: "rgba(255,255,255,0.20)" },
  textCol: { marginLeft: 14, flex: 1 },
  exerciseTitle: { color: "rgba(255,255,255,0.95)", fontSize: 14, fontWeight: "800" },
  duration: { marginTop: 4, color: "rgba(255,255,255,0.65)", fontSize: 12, fontWeight: "700", letterSpacing: 0.2 },
});