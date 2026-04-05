import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import AsyncStorage from "@react-native-async-storage/async-storage";
import * as DocumentPicker from "expo-document-picker";
import { Video, ResizeMode } from "expo-av";
import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { cvAPI } from "../services/api";

export default function UploadExerciseScreen({ navigation, route }) {
  const [selectedExercise, setSelectedExercise] = useState(null);
  const [selectedExerciseKey, setSelectedExerciseKey] = useState(null);
  const [videoFile, setVideoFile] = useState(null);
  const [userId, setUserId] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    AsyncStorage.getItem("userId").then((id) => {
      if (isMounted) setUserId(id);
    });
    return () => { isMounted = false; };
  }, []);

  useEffect(() => {
    const exercise = route?.params?.selectedExercise;
    const exerciseKey = route?.params?.selectedExerciseKey;
    if (exercise) {
      setSelectedExercise(exercise);
      setSelectedExerciseKey(exerciseKey ?? exercise.replace(/\s+/g, "_").toLowerCase());
    }
  }, [route?.params?.selectedExercise, route?.params?.selectedExerciseKey]);

  const pickVideoFile = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: "video/*",
        copyToCacheDirectory: true,
        multiple: false,
      });
      if (result.canceled || !result.assets?.length) return;
      const asset = result.assets[0];
      setVideoFile({
        uri: asset.uri,
        name: asset.name || "upload.mp4",
        mimeType: asset.mimeType || "video/mp4",
      });
    } catch (error) {
      Alert.alert("Picker failed", error?.message || "Unable to select video file.");
    }
  };

  const clearVideo = () => setVideoFile(null);

  const onUpload = async () => {
    if (!selectedExerciseKey) {
      Alert.alert("Exercise missing", "Please select an exercise first.");
      return;
    }
    if (!videoFile?.uri) {
      Alert.alert("Video missing", "Pick a video before uploading.");
      return;
    }
    if (!userId) {
      Alert.alert("Not logged in", "Please log in again before uploading.");
      return;
    }

    setIsUploading(true);
    try {
      const result = await cvAPI.analyzeVideo({
        uri: videoFile.uri,
        fileName: videoFile.name,
        mimeType: videoFile.mimeType,
        exercise: selectedExerciseKey,
        userId,
      });

      if (!result.success) {
        Alert.alert("Upload failed", result.error || "Unable to analyze video.");
        return;
      }

      navigation.navigate("Dashboard", {
        cvResult: {
          score: result.data.form_score ?? result.data.score ?? null,
          insight: result.data.insight ?? result.data.feedback ?? result.data.result ?? "Analysis complete.",
          feedback: result.data.feedback ?? result.data.result ?? "Analysis complete.",
          exercise: selectedExercise ?? selectedExerciseKey,
        },
      });
    } catch (err) {
      Alert.alert("Upload failed", err?.message || "Network error — check your connection and server URL.");
    } finally {
      setIsUploading(false);
    }
  };

  const ready = selectedExerciseKey && videoFile?.uri && userId && !isUploading;
  const step1Done = !!selectedExercise;
  const step2Done = !!videoFile;

  return (
    <SafeAreaView style={styles.safe}>
      <LinearGradient
        colors={["#4C76D6", "#8E5AAE"]}
        start={{ x: 0.15, y: 0.1 }}
        end={{ x: 0.85, y: 0.95 }}
        style={styles.gradient}
      >
        <View style={styles.shell}>
          <ScrollView
            style={{ flex: 1 }}
            showsVerticalScrollIndicator={false}
            contentContainerStyle={styles.scrollContent}
          >

            {/* ── Top nav ── */}
            <View style={styles.topNav}>
              <Pressable style={styles.backBtn} onPress={() => navigation.navigate("Dashboard")}>
                <Ionicons name="arrow-back" size={16} color="#fff" />
                <Text style={styles.backBtnText}>Back</Text>
              </Pressable>
            </View>

            {/* ── Header ── */}
            <Text style={styles.title}>Analyze Your Form</Text>
            <Text style={styles.subtitle}>
              Upload a video and get instant AI-powered feedback on your technique.
            </Text>

            {/* ── Stepper ── */}
            <View style={styles.stepper}>
              <View style={styles.stepItem}>
                <View style={[styles.stepCircle, step1Done && styles.stepCircleDone]}>
                  {step1Done
                    ? <Ionicons name="checkmark" size={14} color="#fff" />
                    : <Text style={styles.stepNum}>1</Text>}
                </View>
                <Text style={[styles.stepText, step1Done && styles.stepTextDone]}>Exercise</Text>
              </View>

              <View style={styles.stepLine}>
                <View style={[styles.stepLineFill, step1Done && styles.stepLineFilled]} />
              </View>

              <View style={styles.stepItem}>
                <View style={[styles.stepCircle, step2Done && styles.stepCircleDone]}>
                  {step2Done
                    ? <Ionicons name="checkmark" size={14} color="#fff" />
                    : <Text style={styles.stepNum}>2</Text>}
                </View>
                <Text style={[styles.stepText, step2Done && styles.stepTextDone]}>Video</Text>
              </View>
            </View>

            {/* ── Step 1: Exercise ── */}
            <View style={styles.section}>
              <Text style={styles.sectionLabel}>Choose Exercise</Text>
              <Pressable
                style={[styles.exerciseBtn, step1Done && styles.exerciseBtnSelected]}
                onPress={() => navigation.navigate("ExerciseSelect")}
              >
                <View style={[styles.exerciseIconWrap, step1Done && styles.exerciseIconWrapDone]}>
                  <Ionicons
                    name="barbell-outline"
                    size={20}
                    color={step1Done ? "#34D399" : "rgba(255,255,255,0.7)"}
                  />
                </View>
                <Text style={[styles.exerciseBtnText, step1Done && styles.exerciseBtnTextSelected]}>
                  {selectedExercise ?? "Select an Exercise"}
                </Text>
                <View style={styles.exerciseChevron}>
                  <Ionicons
                    name={step1Done ? "pencil-outline" : "chevron-forward"}
                    size={15}
                    color="rgba(255,255,255,0.5)"
                  />
                </View>
              </Pressable>
            </View>

            {/* ── Step 2: Video ── */}
            <View style={styles.section}>
              <Text style={styles.sectionLabel}>Select Video</Text>

              {!videoFile ? (
                <Pressable style={styles.dropZone} onPress={pickVideoFile}>
                  <View style={styles.dropIconRing}>
                    <Ionicons name="cloud-upload-outline" size={30} color="#fff" />
                  </View>
                  <Text style={styles.dropText}>Tap to choose a video</Text>
                  <Text style={styles.dropHint}>MP4 · MOV · AVI</Text>
                </Pressable>
              ) : (
                <View style={styles.videoCard}>
                  {/* Video preview */}
                  <View style={styles.videoWrapper}>
                    <Video
                      source={{ uri: videoFile.uri }}
                      style={styles.videoPreview}
                      resizeMode={ResizeMode.CONTAIN}
                      isLooping
                      shouldPlay
                      isMuted
                      useNativeControls={false}
                    />
                    {/* Analyzing overlay */}
                    {isUploading && (
                      <View style={styles.analyzingOverlay}>
                        <ActivityIndicator size="large" color="#fff" />
                        <Text style={styles.analyzingText}>Analyzing your form…</Text>
                      </View>
                    )}
                    {/* Exercise badge on video */}
                    {selectedExercise && (
                      <View style={styles.videoBadge}>
                        <Ionicons name="barbell-outline" size={11} color="#fff" />
                        <Text style={styles.videoBadgeText}>{selectedExercise}</Text>
                      </View>
                    )}
                  </View>

                  {/* File info bar */}
                  <View style={styles.fileBar}>
                    <Ionicons name="film-outline" size={15} color="rgba(255,255,255,0.7)" />
                    <Text style={styles.fileName} numberOfLines={1}>{videoFile.name}</Text>
                    <Pressable style={styles.changeBtn} onPress={pickVideoFile}>
                      <Text style={styles.changeBtnText}>Change</Text>
                    </Pressable>
                    <Pressable style={styles.removeBtn} onPress={clearVideo}>
                      <Ionicons name="trash-outline" size={15} color="rgba(255,100,100,0.85)" />
                    </Pressable>
                  </View>
                </View>
              )}
            </View>

            {/* ── Recording tips ── */}
            <View style={styles.tipsCard}>
              <View style={styles.tipsIconWrap}>
                <Ionicons name="bulb-outline" size={18} color="#FBBF24" />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.tipsTitle}>Pro tip</Text>
                <Text style={styles.tipsText}>
                  Keep your full body in frame. Step back from the camera if needed for best results.
                </Text>
              </View>
            </View>

          </ScrollView>

          {/* ── Upload button ── */}
          <View style={styles.bottomBar}>
            <Pressable
              style={[styles.uploadBtn, !ready && styles.uploadBtnDisabled]}
              disabled={!ready}
              onPress={onUpload}
            >
              {isUploading ? (
                <>
                  <ActivityIndicator size="small" color="#fff" />
                  <Text style={styles.uploadBtnText}>Analyzing…</Text>
                </>
              ) : (
                <>
                  <Text style={[styles.uploadBtnText, !ready && styles.uploadBtnTextDisabled]}>
                    Upload &amp; Get Feedback
                  </Text>
                  <Ionicons
                    name="arrow-forward-circle"
                    size={20}
                    color={ready ? "#fff" : "rgba(255,255,255,0.3)"}
                  />
                </>
              )}
            </Pressable>
          </View>
        </View>
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#4C76D6" },
  gradient: { flex: 1 },

  shell: {
    flex: 1,
    marginHorizontal: 14,
    marginTop: 10,
    marginBottom: 14,
    borderRadius: 28,
    paddingTop: 10,
    paddingHorizontal: 16,
    backgroundColor: "rgba(255,255,255,0.13)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.18)",
    overflow: "hidden",
  },

  scrollContent: {
    flexGrow: 1,
    paddingBottom: 20,
  },

  // ── Top nav ──
  topNav: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 18,
    marginTop: 4,
  },
  backBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 5,
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 999,
    backgroundColor: "rgba(255,255,255,0.12)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.15)",
  },
  backBtnText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "700",
  },

  // ── Header ──
  title: {
    color: "#fff",
    fontSize: 26,
    fontWeight: "900",
    textAlign: "center",
    letterSpacing: -0.5,
    marginBottom: 6,
  },
  subtitle: {
    color: "rgba(255,255,255,0.6)",
    fontSize: 12,
    fontWeight: "600",
    textAlign: "center",
    lineHeight: 18,
    marginBottom: 24,
    paddingHorizontal: 10,
  },

  // ── Stepper ──
  stepper: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 24,
    paddingHorizontal: 30,
  },
  stepItem: {
    alignItems: "center",
    gap: 5,
  },
  stepCircle: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: "rgba(255,255,255,0.18)",
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1.5,
    borderColor: "rgba(255,255,255,0.25)",
  },
  stepCircleDone: {
    backgroundColor: "#34D399",
    borderColor: "#34D399",
  },
  stepNum: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "800",
  },
  stepText: {
    color: "rgba(255,255,255,0.5)",
    fontSize: 11,
    fontWeight: "700",
  },
  stepTextDone: {
    color: "#34D399",
  },
  stepLine: {
    flex: 1,
    height: 2,
    backgroundColor: "rgba(255,255,255,0.15)",
    borderRadius: 1,
    marginHorizontal: 8,
    marginBottom: 16,
    overflow: "hidden",
  },
  stepLineFill: {
    width: "0%",
    height: "100%",
    backgroundColor: "#34D399",
    borderRadius: 1,
  },
  stepLineFilled: {
    width: "100%",
  },

  // ── Section ──
  section: {
    marginBottom: 20,
  },
  sectionLabel: {
    color: "rgba(255,255,255,0.55)",
    fontSize: 11,
    fontWeight: "800",
    textTransform: "uppercase",
    letterSpacing: 0.8,
    marginBottom: 8,
    marginLeft: 2,
  },

  // ── Exercise button ──
  exerciseBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    paddingVertical: 14,
    paddingHorizontal: 14,
    borderRadius: 16,
    backgroundColor: "rgba(255,255,255,0.10)",
    borderWidth: 1.5,
    borderColor: "rgba(255,255,255,0.14)",
  },
  exerciseBtnSelected: {
    backgroundColor: "rgba(52,211,153,0.12)",
    borderColor: "rgba(52,211,153,0.4)",
  },
  exerciseIconWrap: {
    width: 36,
    height: 36,
    borderRadius: 10,
    backgroundColor: "rgba(255,255,255,0.10)",
    alignItems: "center",
    justifyContent: "center",
  },
  exerciseIconWrapDone: {
    backgroundColor: "rgba(52,211,153,0.15)",
  },
  exerciseBtnText: {
    flex: 1,
    color: "rgba(255,255,255,0.55)",
    fontSize: 14,
    fontWeight: "700",
  },
  exerciseBtnTextSelected: {
    color: "#fff",
    fontWeight: "800",
  },
  exerciseChevron: {
    width: 28,
    height: 28,
    borderRadius: 8,
    backgroundColor: "rgba(255,255,255,0.07)",
    alignItems: "center",
    justifyContent: "center",
  },

  // ── Drop zone ──
  dropZone: {
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 42,
    borderRadius: 18,
    borderWidth: 1.5,
    borderStyle: "dashed",
    borderColor: "rgba(255,255,255,0.25)",
    backgroundColor: "rgba(255,255,255,0.05)",
    gap: 8,
  },
  dropIconRing: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: "rgba(255,255,255,0.12)",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 4,
  },
  dropText: {
    color: "rgba(255,255,255,0.9)",
    fontSize: 14,
    fontWeight: "800",
  },
  dropHint: {
    color: "rgba(255,255,255,0.38)",
    fontSize: 11,
    fontWeight: "600",
    letterSpacing: 0.5,
  },

  // ── Video card ──
  videoCard: {
    borderRadius: 18,
    overflow: "hidden",
    borderWidth: 1.5,
    borderColor: "rgba(255,255,255,0.16)",
  },
  videoWrapper: {
    width: "100%",
    height: 220,
    backgroundColor: "#000",
    alignSelf: "stretch",
  },
  videoPreview: {
    flex: 1,
    alignSelf: "stretch",
  },
  analyzingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(0,0,0,0.65)",
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
  },
  analyzingText: {
    color: "#fff",
    fontSize: 13,
    fontWeight: "700",
  },
  videoBadge: {
    position: "absolute",
    top: 10,
    left: 10,
    flexDirection: "row",
    alignItems: "center",
    gap: 5,
    paddingVertical: 4,
    paddingHorizontal: 9,
    borderRadius: 999,
    backgroundColor: "rgba(0,0,0,0.55)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.15)",
  },
  videoBadgeText: {
    color: "#fff",
    fontSize: 10,
    fontWeight: "800",
  },
  fileBar: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    paddingVertical: 10,
    paddingHorizontal: 12,
    backgroundColor: "rgba(255,255,255,0.08)",
  },
  fileName: {
    flex: 1,
    color: "rgba(255,255,255,0.75)",
    fontSize: 11,
    fontWeight: "700",
  },
  changeBtn: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
    backgroundColor: "rgba(255,255,255,0.12)",
  },
  changeBtnText: {
    color: "rgba(255,255,255,0.85)",
    fontSize: 11,
    fontWeight: "700",
  },
  removeBtn: {
    padding: 4,
  },

  // ── Tips card ──
  tipsCard: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 12,
    padding: 14,
    borderRadius: 16,
    backgroundColor: "rgba(251,191,36,0.08)",
    borderWidth: 1,
    borderColor: "rgba(251,191,36,0.2)",
  },
  tipsIconWrap: {
    width: 32,
    height: 32,
    borderRadius: 10,
    backgroundColor: "rgba(251,191,36,0.15)",
    alignItems: "center",
    justifyContent: "center",
  },
  tipsTitle: {
    color: "#FBBF24",
    fontSize: 12,
    fontWeight: "900",
    marginBottom: 3,
  },
  tipsText: {
    color: "rgba(255,255,255,0.6)",
    fontSize: 11,
    fontWeight: "600",
    lineHeight: 16,
  },

  // ── Bottom bar ──
  bottomBar: {
    paddingVertical: 14,
    paddingHorizontal: 2,
  },
  uploadBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    height: 52,
    borderRadius: 999,
    backgroundColor: "#34D399",
    borderWidth: 1,
    borderColor: "rgba(52,211,153,0.5)",
  },
  uploadBtnDisabled: {
    backgroundColor: "rgba(255,255,255,0.10)",
    borderColor: "rgba(255,255,255,0.10)",
  },
  uploadBtnText: {
    color: "#fff",
    fontSize: 15,
    fontWeight: "900",
  },
  uploadBtnTextDisabled: {
    color: "rgba(255,255,255,0.3)",
  },
});
