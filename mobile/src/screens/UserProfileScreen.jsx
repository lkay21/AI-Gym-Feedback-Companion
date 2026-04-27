import React, { useEffect, useState } from "react";
import {
  Alert,
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
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import AsyncStorage from "@react-native-async-storage/async-storage";
import MenuDropdown from "../components/MenuDropdown";

const PROFILE_STORAGE_KEY = "userProfile";
const AUTH_TOKEN_KEY = "authToken";

const DEFAULT_PROFILE = {
  email: "",
  weight: "",
  height: "",
  fitnessGoals: "",
};

function InputRow({ icon, value, onChangeText, placeholder, ...rest }) {
  return (
    <View style={styles.inputRow}>
      <View style={styles.inputIconWrap}>
        <Ionicons name={icon} size={16} color="rgba(255,255,255,0.5)" />
      </View>
      <TextInput
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor="rgba(255,255,255,0.35)"
        style={styles.input}
        {...rest}
      />
    </View>
  );
}

export default function UserProfileScreen({ navigation }) {
  const [profile, setProfile] = useState(DEFAULT_PROFILE);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const raw = await AsyncStorage.getItem(PROFILE_STORAGE_KEY);
      if (raw) setProfile({ ...DEFAULT_PROFILE, ...JSON.parse(raw) });
    } catch {
      // keep defaults
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field, value) =>
    setProfile((prev) => ({ ...prev, [field]: value }));

  const handleSave = async () => {
    try {
      setSaving(true);
      await AsyncStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profile));
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch {
      Alert.alert("Error", "Could not save your profile.");
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = async () => {
    try {
      setLoggingOut(true);
      await AsyncStorage.multiRemove([AUTH_TOKEN_KEY, "lastCVResult", "user", "username", "userId"]);
      navigation.reset({ index: 0, routes: [{ name: "Login" }] });
    } catch {
      Alert.alert("Error", "Could not log out.");
    } finally {
      setLoggingOut(false);
    }
  };

  const avatarLetter = profile.email?.trim()?.[0]?.toUpperCase() ?? null;

  return (
    <LinearGradient
      colors={["#7c3aed", "#6366f1", "#4c1d95"]}
      style={styles.gradient}
    >
      <SafeAreaView style={styles.safe}>
        <KeyboardAvoidingView
          style={styles.safe}
          behavior={Platform.OS === "ios" ? "padding" : undefined}
        >
          <View style={styles.shell}>
            <ScrollView
              showsVerticalScrollIndicator={false}
              contentContainerStyle={styles.scrollContent}
              keyboardShouldPersistTaps="handled"
            >
              <View style={styles.topBar}>
                <MenuDropdown />
              </View>

              {/* ── Avatar + title ── */}
              <View style={styles.heroSection}>
                <View style={styles.avatarRing}>
                  {avatarLetter ? (
                    <Text style={styles.avatarLetter}>{avatarLetter}</Text>
                  ) : (
                    <Ionicons name="person-outline" size={36} color="rgba(255,255,255,0.8)" />
                  )}
                </View>
                <Text style={styles.title}>
                  {profile.email ? profile.email.split("@")[0] : "Your Profile"}
                </Text>
                <Text style={styles.subtitle}>Manage your account and fitness info</Text>
              </View>

              {/* ── Account card ── */}
              <View style={styles.card}>
                <View style={styles.cardHeader}>
                  <View style={styles.cardHeaderIcon}>
                    <Ionicons name="lock-closed-outline" size={14} color="rgba(255,255,255,0.7)" />
                  </View>
                  <Text style={styles.cardHeaderText}>ACCOUNT</Text>
                </View>

                <Text style={styles.fieldLabel}>Email</Text>
                <InputRow
                  icon="mail-outline"
                  value={profile.email}
                  onChangeText={(t) => updateField("email", t)}
                  placeholder="Enter email"
                  autoCapitalize="none"
                  keyboardType="email-address"
                  editable={!loading}
                />

              </View>

              {/* ── Fitness card ── */}
              <View style={styles.card}>
                <View style={styles.cardHeader}>
                  <View style={styles.cardHeaderIcon}>
                    <Ionicons name="barbell-outline" size={14} color="rgba(255,255,255,0.7)" />
                  </View>
                  <Text style={styles.cardHeaderText}>FITNESS</Text>
                </View>

                <Text style={styles.fieldLabel}>Weight</Text>
                <InputRow
                  icon="scale-outline"
                  value={profile.weight}
                  onChangeText={(t) => updateField("weight", t)}
                  placeholder="e.g. 180 lbs"
                  editable={!loading}
                />

                <Text style={styles.fieldLabel}>Height</Text>
                <InputRow
                  icon="resize-outline"
                  value={profile.height}
                  onChangeText={(t) => updateField("height", t)}
                  placeholder={`e.g. 5'11"`}
                  editable={!loading}
                />

                <Text style={styles.fieldLabel}>Fitness Goals</Text>
                <View style={[styles.inputRow, styles.inputRowTextArea]}>
                  <View style={[styles.inputIconWrap, { alignSelf: "flex-start", marginTop: 14 }]}>
                    <Ionicons name="flag-outline" size={16} color="rgba(255,255,255,0.5)" />
                  </View>
                  <TextInput
                    value={profile.fitnessGoals}
                    onChangeText={(t) => updateField("fitnessGoals", t)}
                    placeholder="Build muscle, lose fat, improve endurance…"
                    placeholderTextColor="rgba(255,255,255,0.35)"
                    style={[styles.input, styles.textArea]}
                    multiline
                    textAlignVertical="top"
                    editable={!loading}
                  />
                </View>
              </View>

              {/* ── Actions ── */}
              <View style={styles.actionsCard}>
                <Pressable
                  style={[styles.saveBtn, saved && styles.saveBtnSaved, (saving || loading) && styles.btnDisabled]}
                  onPress={handleSave}
                  disabled={saving || loading}
                >
                  <Ionicons name={saved ? "checkmark-circle" : "checkmark-circle-outline"} size={18} color="#fff" />
                  <Text style={styles.saveBtnText}>{saving ? "Saving…" : saved ? "Saved!" : "Save Profile"}</Text>
                </Pressable>

                <Pressable
                  style={styles.chatBtn}
                  onPress={() => navigation.navigate("ChatBot")}
                >
                  <Ionicons name="chatbubble-ellipses-outline" size={16} color="rgba(255,255,255,0.85)" />
                  <Text style={styles.chatBtnText}>Go to ChatBot</Text>
                </Pressable>

                <Pressable
                  style={[styles.logoutBtn, loggingOut && styles.btnDisabled]}
                  onPress={handleLogout}
                  disabled={loggingOut}
                >
                  <Ionicons name="log-out-outline" size={16} color="#F87171" />
                  <Text style={styles.logoutBtnText}>{loggingOut ? "Logging Out…" : "Log Out"}</Text>
                </Pressable>
              </View>

            </ScrollView>
          </View>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: { flex: 1 },
  safe: { flex: 1 },

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
    paddingBottom: 30,
  },

  topBar: {
    paddingTop: 6,
    flexDirection: "row",
    justifyContent: "flex-end",
  },

  // ── Hero ──
  heroSection: {
    alignItems: "center",
    marginTop: 8,
    marginBottom: 22,
  },
  avatarRing: {
    width: 80,
    height: 80,
    borderRadius: 40,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(255,255,255,0.14)",
    borderWidth: 2,
    borderColor: "rgba(255,255,255,0.28)",
    marginBottom: 12,
  },
  avatarLetter: {
    color: "#fff",
    fontSize: 32,
    fontWeight: "900",
  },
  eyeBtn: {
    paddingHorizontal: 12,
    alignSelf: "stretch",
    alignItems: "center",
    justifyContent: "center",
  },
  title: {
    color: "#fff",
    fontSize: 24,
    fontWeight: "900",
    letterSpacing: -0.5,
    marginBottom: 4,
  },
  subtitle: {
    color: "rgba(255,255,255,0.5)",
    fontSize: 12,
    fontWeight: "600",
  },

  // ── Cards ──
  card: {
    borderRadius: 18,
    padding: 16,
    backgroundColor: "rgba(255,255,255,0.10)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.15)",
    marginBottom: 14,
  },
  cardHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 7,
    marginBottom: 14,
  },
  cardHeaderIcon: {
    width: 24,
    height: 24,
    borderRadius: 7,
    backgroundColor: "rgba(255,255,255,0.12)",
    alignItems: "center",
    justifyContent: "center",
  },
  cardHeaderText: {
    color: "rgba(255,255,255,0.55)",
    fontSize: 11,
    fontWeight: "800",
    letterSpacing: 1,
    textTransform: "uppercase",
  },

  // ── Fields ──
  fieldLabel: {
    color: "rgba(255,255,255,0.75)",
    fontSize: 11,
    fontWeight: "700",
    marginBottom: 6,
    marginTop: 10,
  },
  inputRow: {
    flexDirection: "row",
    alignItems: "center",
    borderRadius: 14,
    backgroundColor: "rgba(255,255,255,0.08)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.12)",
    overflow: "hidden",
  },
  inputRowTextArea: {
    alignItems: "flex-start",
  },
  inputIconWrap: {
    width: 42,
    alignItems: "center",
    justifyContent: "center",
  },
  input: {
    flex: 1,
    minHeight: 48,
    paddingVertical: 12,
    paddingRight: 14,
    color: "#fff",
    fontSize: 13,
    fontWeight: "600",
  },
  textArea: {
    minHeight: 100,
  },

  // ── Actions card ──
  actionsCard: {
    gap: 10,
    marginTop: 2,
  },
  saveBtn: {
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
  saveBtnSaved: {
    backgroundColor: "#059669",
    borderColor: "#059669",
  },
  saveBtnText: {
    color: "#fff",
    fontSize: 15,
    fontWeight: "900",
  },
  chatBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    height: 48,
    borderRadius: 999,
    backgroundColor: "rgba(255,255,255,0.10)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.14)",
  },
  chatBtnText: {
    color: "rgba(255,255,255,0.85)",
    fontSize: 14,
    fontWeight: "800",
  },
  logoutBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 7,
    height: 48,
    borderRadius: 999,
    backgroundColor: "rgba(248,113,113,0.10)",
    borderWidth: 1,
    borderColor: "rgba(248,113,113,0.25)",
  },
  logoutBtnText: {
    color: "#F87171",
    fontSize: 14,
    fontWeight: "800",
  },
  btnDisabled: {
    opacity: 0.5,
  },
});
