import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import AsyncStorage from "@react-native-async-storage/async-storage";
import * as DocumentPicker from "expo-document-picker";
import { useEffect, useState } from "react";
import { Alert, Image, Pressable, SafeAreaView, StyleSheet, Text, View } from "react-native";
import { cvAPI } from "../services/api";

export default function RecordVideoScreen({ navigation, route }) {
  const selectedExercise = route?.params?.selectedExercise ?? null;
  const selectedExerciseKey = route?.params?.selectedExerciseKey ?? null;
  const recordedVideoUri = route?.params?.recordedVideoUri ?? route?.params?.videoUri ?? null;
  const [userId, setUserId] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [videoFile, setVideoFile] = useState(() => (
    recordedVideoUri
      ? {
          uri: recordedVideoUri,
          name: "upload.mp4",
          mimeType: "video/mp4",
        }
      : null
  ));

  useEffect(() => {
    if (!recordedVideoUri) {
      return;
    }

    setVideoFile((prev) => {
      if (prev?.uri === recordedVideoUri) {
        return prev;
      }

      return {
        uri: recordedVideoUri,
        name: "upload.mp4",
        mimeType: "video/mp4",
      };
    });
  }, [recordedVideoUri]);

  useEffect(() => {
    let isMounted = true;

    const loadUserId = async () => {
      const storedUserId = await AsyncStorage.getItem("userId");
      if (isMounted) {
        setUserId(storedUserId);
      }
    };

    loadUserId();

    return () => {
      isMounted = false;
    };
  }, []);

  const resolveExerciseKey = () => {
    if (selectedExerciseKey) {
      return selectedExerciseKey;
    }

    if (!selectedExercise) {
      return null;
    }

    return selectedExercise.replace(/\s+/g, "_").toLowerCase();
  };

  const pickVideoFile = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: "video/*",
        copyToCacheDirectory: true,
        multiple: false,
      });

      if (result.canceled || !result.assets?.length) {
        return;
      }

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

  const onUpload = async () => {
    const exerciseKey = resolveExerciseKey();

    if (!exerciseKey) {
      navigation.navigate("ExerciseSelect");
      return;
    }

    if (!videoFile?.uri) {
      Alert.alert("Video missing", "Pick or record a video before uploading.");
      return;
    }

    if (!userId) {
      Alert.alert("User missing", "Please log in again before uploading a video.");
      return;
    }

    setIsUploading(true);

    try {
      const result = await cvAPI.analyzeVideo({
        uri: videoFile.uri,
        fileName: videoFile.name,
        mimeType: videoFile.mimeType,
        exercise: exerciseKey,
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
          exercise: selectedExercise ?? exerciseKey,
        },
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleUpload = () => {
    onUpload();
  };

  return (
    <SafeAreaView style={styles.safe}>
      <LinearGradient
        colors={["#8E5AAE", "#4C76D6"]}
        start={{ x: 0.05, y: 0.05 }}
        end={{ x: 0.95, y: 0.95 }}
        style={styles.bg}
      >
        <View style={styles.topLabelWrap}>
          <Text style={styles.topLabel}>CV Processing Screen</Text>
        </View>

        <View style={styles.card}>
          <Pressable
          style={styles.backButton}
          onPress={() => navigation.navigate("Dashboard")}
        >
          <Ionicons name="arrow-back" size={18} color="rgba(255,255,255,0.92)" />
          <Text style={styles.backButtonText}>Back to Dashboard</Text>
          </Pressable>

          <View style={styles.cardHeader}>
            <Text style={styles.title}>Upload a Video</Text>
            <Ionicons
              name="videocam-outline"
              size={22}
              color="rgba(255,255,255,0.92)"
            />
          </View>

          <Text style={styles.subtitle}>
            Pick your exercise video file and upload it for CV form scoring.
          </Text>

          <Text style={styles.metaLine}>
            Exercise: {selectedExercise ?? "Not selected"}
          </Text>
          <Text style={styles.metaLine}>
            Video: {videoFile?.name ? videoFile.name : "No file selected"}
          </Text>

          <View style={styles.previewFrame}>
            <Image
              source={{
                uri:
                  "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=1200&q=60",
              }}
              style={styles.previewImg}
              resizeMode="cover"
            />
            <View style={styles.previewTint} pointerEvents="none" />
          </View>

          <View style={styles.guidanceWrap}>
            <Text style={styles.guidanceTitle}>Step Further Back!</Text>
            <Text style={styles.guidanceText}>
              Keep your full body within frame of the camera!
            </Text>
          </View>

          <View style={styles.btnRow}>
            <Pressable style={styles.pillBtn} onPress={pickVideoFile}>
              <Text style={styles.pillBtnText}>Choose Video</Text>
            </Pressable>

            <Pressable
              style={styles.pillBtn}
              disabled={isUploading || !videoFile?.uri}
              onPress={handleUpload}
            >
              <Text style={styles.pillBtnText}>{isUploading ? "Uploading..." : "Upload Video"}</Text>
            </Pressable>
          </View>
        </View>
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#000" },
  bg: { flex: 1, paddingHorizontal: 16, paddingTop: 8, paddingBottom: 18 },

  topLabelWrap: { alignItems: "flex-start", paddingHorizontal: 6, paddingBottom: 8 },
  topLabel: { color: "rgba(255,255,255,0.35)", fontSize: 13, fontWeight: "800" },

  card: {
    flex: 1,
    borderRadius: 18,
    padding: 16,
    backgroundColor: "rgba(36, 12, 75, 0.35)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.10)",
  },

    backButton: {
    flexDirection: "row",
    alignItems: "center",
    alignSelf: "flex-start",
    gap: 6,
    marginBottom: 10,
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 999,
    backgroundColor: "rgba(0,0,0,0.22)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.12)",
  },

  backButtonText: {
    color: "rgba(255,255,255,0.92)",
    fontSize: 12,
    fontWeight: "800",
  },

  cardHeader: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    gap: 10,
    marginTop: 6,
  },
  title: { color: "#fff", fontSize: 22, fontWeight: "900", textAlign: "center" },
  subtitle: {
    color: "rgba(255,255,255,0.75)",
    fontSize: 11,
    fontWeight: "700",
    textAlign: "center",
    marginTop: 10,
    marginBottom: 12,
    lineHeight: 15,
  },
  metaLine: {
    color: "rgba(255,255,255,0.72)",
    fontSize: 11,
    fontWeight: "700",
    textAlign: "center",
    marginBottom: 6,
  },

  previewFrame: {
    flex: 1,
    borderRadius: 16,
    overflow: "hidden",
    backgroundColor: "rgba(0,0,0,0.18)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.12)",
  },
  previewImg: { width: "100%", height: "100%" },
  previewTint: { ...StyleSheet.absoluteFillObject, backgroundColor: "rgba(142, 90, 174, 0.20)" },

  guidanceWrap: { marginTop: 12, paddingHorizontal: 4 },
  guidanceTitle: { color: "rgba(255,255,255,0.95)", fontSize: 12, fontWeight: "900", marginBottom: 6 },
  guidanceText: { color: "rgba(255,255,255,0.75)", fontSize: 11, fontWeight: "700" },

  btnRow: { flexDirection: "row", justifyContent: "space-between", gap: 12, marginTop: 14 },
  pillBtn: {
    flex: 1,
    height: 32,
    borderRadius: 999,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(0,0,0,0.28)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.14)",
  },
  pillBtnText: { color: "rgba(255,255,255,0.92)", fontSize: 11, fontWeight: "900" },
});
