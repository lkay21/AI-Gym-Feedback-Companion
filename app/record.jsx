import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { useRouter } from "expo-router";
import { Image, Pressable, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

export default function RecordVideoScreen() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.safe} edges={["top", "left", "right"]}>
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
          <View style={styles.cardHeader}>
            <Text style={styles.title}>Record a Video</Text>
            <Ionicons
              name="videocam-outline"
              size={22}
              color="rgba(255,255,255,0.92)"
            />
          </View>

          <Text style={styles.subtitle}>
            Click Start to begin recording! Click Stop to end{"\n"}
            the recording!
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
            <Pressable style={styles.pillBtn} onPress={() => {}}>
              <Text style={styles.pillBtnText}>Re-record Video</Text>
            </Pressable>

            <Pressable
              style={styles.pillBtn}
              onPress={() => router.push("/selectexercise")}
            >
              <Text style={styles.pillBtnText}>Upload Video</Text>
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